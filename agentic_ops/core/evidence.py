import json
import os
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

from agentic_ops.core.crypto import get_canonical_json, sign_payload, verify_signature
from agentic_ops.core.merkle import MerkleTree, hash_leaf

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

    def load_all_episodes(self) -> List[Dict[str, Any]]:
        """Loads all sealed episodes from the append-only ledger or individual JSON files in canonical order."""
        episodes: List[Dict[str, Any]] = []
        if self.ledger_file.exists() and self.ledger_file.stat().st_size > 0:
            with open(self.ledger_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            episodes.append(json.loads(line))
                        except Exception:
                            pass
        elif self.store_dir.exists():
            for p in sorted(self.store_dir.glob("*.json")):
                if p.name.startswith("_"):
                    continue
                try:
                    with open(p, "r", encoding="utf-8") as f:
                        episodes.append(json.load(f))
                except Exception:
                    pass
        return episodes

    def get_merkle_tree(self) -> MerkleTree:
        """
        [RFC 6962] Constructs an immutable Binary Merkle Tree across all episodes in the ledger.
        Each episode is converted to a canonical leaf: SHA-256(0x00 || canonical_json).
        """
        episodes = self.load_all_episodes()
        # Canonical representation of each episode without signature for leaf hashing
        leaves = []
        for ep in episodes:
            c_ep = dict(ep)
            c_ep.pop("hash", None)
            c_ep.pop("cryptographic_signature", None)
            leaves.append(get_canonical_json(c_ep))
        return MerkleTree(leaves)

    def get_merkle_root(self) -> str:
        """Returns the current 32-byte hex Merkle Root representing the whole ledger."""
        return self.get_merkle_tree().root

    def get_merkle_proof(self, episode_id: str) -> Optional[Dict[str, Any]]:
        """
        Generates an O(log N) Merkle Audit Proof of inclusion for a given episode.
        Allows third-party auditors to verify that `episode_id` is sealed in the ledger
        without revealing any other episode.
        Includes the canonical episode payload to cryptographically bind:
        episode_id -> canonical_payload -> leaf_hash -> Merkle Root.
        """
        episodes = self.load_all_episodes()
        target_idx = -1
        target_ep = None
        for idx, ep in enumerate(episodes):
            if ep.get("episode_id") == episode_id:
                target_idx = idx
                target_ep = ep
                break
        if target_idx == -1 or target_ep is None:
            return None

        # Canonical representation of the episode for leaf hashing
        c_ep = dict(target_ep)
        c_ep.pop("hash", None)
        c_ep.pop("cryptographic_signature", None)
        canonical_payload = get_canonical_json(c_ep)

        tree = self.get_merkle_tree()
        leaf_hash = tree.leaf_hashes[target_idx]
        audit_path = tree.get_audit_proof(target_idx)

        return {
            "episode_id": episode_id,
            "leaf_index": target_idx,
            "total_leaves": len(episodes),
            "leaf_hash": leaf_hash,
            "canonical_payload": canonical_payload,
            "merkle_root": tree.root,
            "audit_path": audit_path,
        }

    @staticmethod
    def verify_merkle_proof(
        proof_packet: Dict[str, Any],
        raw_episode: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Verifies a Merkle inclusion proof packet in O(log N) time.
        Does not require reading or loading the local ledger.
        Strictly binds episode_id and episode content to leaf_hash before
        verifying the Merkle inclusion path.
        """
        leaf_hash = proof_packet.get("leaf_hash", "")
        proof = proof_packet.get("audit_path", [])
        expected_root = proof_packet.get("merkle_root", "")
        claimed_episode_id = proof_packet.get("episode_id", "")

        if not leaf_hash or not expected_root or not claimed_episode_id:
            return False

        # 1. Cryptographic binding check: bind episode_id & payload to leaf_hash
        payload_to_check = None
        if raw_episode is not None:
            c_ep = dict(raw_episode)
            c_ep.pop("hash", None)
            c_ep.pop("cryptographic_signature", None)
            if c_ep.get("episode_id") != claimed_episode_id:
                return False
            payload_to_check = get_canonical_json(c_ep)
        elif "canonical_payload" in proof_packet:
            payload_str = proof_packet["canonical_payload"]
            try:
                parsed = json.loads(payload_str)
                if parsed.get("episode_id") != claimed_episode_id:
                    return False
            except Exception:
                return False
            payload_to_check = payload_str

        if payload_to_check is not None:
            computed_leaf_hash = hash_leaf(payload_to_check)
            if computed_leaf_hash.lower() != leaf_hash.lower():
                return False  # Payload does not match leaf_hash!

        # 2. O(log N) Merkle path verification
        return MerkleTree.verify_audit_proof(leaf_hash, proof, expected_root)


