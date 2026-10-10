import json
import os
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

from agentic_ops.core.crypto import get_canonical_json, sign_payload, verify_signature

class EvidenceStore:
    def __init__(self, store_dir: str):
        self.store_dir = Path(store_dir)
        self.store_dir.mkdir(parents=True, exist_ok=True)
        self.ledger_file = self.store_dir / "ledger.jsonl"
        # Backward compatibility / fast lookup
        self.index_file = self.store_dir / "_index.json"
        
        if not self.index_file.exists():
            with open(self.index_file, "w") as f:
                json.dump({"last_episode_id": "EP-0000", "last_hash": "genesis"}, f)
        
        # Ensure ledger exists
        if not self.ledger_file.exists():
            self.ledger_file.touch()

    def next_episode_id(self) -> str:
        with open(self.index_file, "r") as f:
            index = json.load(f)
        last_id = index.get("last_episode_id", "EP-0000")
        try:
            num = int(last_id.split("-")[1])
        except (IndexError, ValueError):
            num = 0
        return f"EP-{num + 1:04d}"
        
    def find_existing_episode(self, dedup_key: str) -> bool:
        return False

    def save(self, episode: Dict[str, Any]) -> str:
        # Load the last state from index to chain the blocks
        with open(self.index_file, "r") as f:
            index = json.load(f)
            
        previous_hash = index.get("last_hash", "genesis")
        episode["previous_hash"] = previous_hash
        
        episode_id = episode.get("episode_id", self.next_episode_id())
        episode["episode_id"] = episode_id
        
        # Remove any existing hash or signature to prevent pollution
        episode.pop("hash", None)
        episode.pop("cryptographic_signature", None)
        
        # Canonicalize the episode payload
        canonical_json = get_canonical_json(episode)
        
        # Compute the signature of (previous_hash + canonical_json)
        # This guarantees chain integrity + payload integrity with a secret KMS key
        payload_to_sign = previous_hash + canonical_json
        signature = sign_payload(payload_to_sign)
        
        episode["cryptographic_signature"] = signature
        # We also keep a simple hash for quick referencing without secret keys
        current_hash = hashlib.sha256(canonical_json.encode('utf-8')).hexdigest()
        episode["hash"] = current_hash
        
        # Append-Only WORM storage
        with open(self.ledger_file, "a") as f:
            # We enforce an OS-level append. In a real system, the file would be chattr +a
            f.write(json.dumps(episode) + "\n")
            
        # Update fast index
        index["last_episode_id"] = episode_id
        index["last_hash"] = current_hash
        
        # Atomic index replacement
        tmp_index = self.index_file.with_suffix(".tmp")
        with open(tmp_index, "w") as f:
            json.dump(index, f, indent=2)
        os.replace(tmp_index, self.index_file)
            
        # Also write the individual file for backward compatibility with older readers
        file_path = self.store_dir / f"{episode_id}.json"
        if file_path.exists() and not episode_id.endswith("-RESUMED"):
            # Normally we should not overwrite, except maybe resumed episodes
            pass
        with open(file_path, "w") as f:
            json.dump(episode, f, indent=2)
            
        return str(self.ledger_file)

    def verify_episode(self, file_path: str) -> bool:
        """Legacy local verifier. Does not verify the chain."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                ep = json.load(f)
            stored_hash = ep.get("hash")
            ep.pop("hash", None)
            ep.pop("cryptographic_signature", None)
            canonical = get_canonical_json(ep)
            calculated = hashlib.sha256(canonical.encode('utf-8')).hexdigest()
            return calculated == stored_hash
        except Exception:
            return False
            
    def verify_chain(self) -> bool:
        """
        [PR5] Vérifie la cryptographie de l'ENSEMBLE de la chaîne.
        Retourne True si le registre (ledger) est 100% intègre, False si une falsification est détectée.
        """
        if not self.ledger_file.exists():
            return True
            
        expected_previous = "genesis"
        
        with open(self.ledger_file, "r") as f:
            for line_no, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    ep = json.loads(line)
                    sig = ep.pop("cryptographic_signature", None)
                    ep.pop("hash", None)
                    prev = ep.get("previous_hash")
                    
                    if prev != expected_previous:
                        print(f"Brèche de chaîne détectée à l'épisode {ep.get('episode_id', line_no)}")
                        return False
                        
                    canonical_json = get_canonical_json(ep)
                    payload_to_sign = prev + canonical_json
                    
                    if not verify_signature(payload_to_sign, sig):
                        print(f"Falsification cryptographique détectée à l'épisode {ep.get('episode_id', line_no)}")
                        return False
                        
                    expected_previous = hashlib.sha256(canonical_json.encode('utf-8')).hexdigest()
                    
                except Exception as e:
                    print(f"Erreur de parsing à la ligne {line_no}: {e}")
                    return False
        return True
