import json
import os
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

class EvidenceStore:
    def __init__(self, store_dir: str):
        self.store_dir = Path(store_dir)
        self.store_dir.mkdir(parents=True, exist_ok=True)
        self.index_file = self.store_dir / "_index.json"
        
        if not self.index_file.exists():
            with open(self.index_file, "w") as f:
                json.dump({"last_episode_id": "EP-0000", "last_hash": "genesis"}, f)

    def next_episode_id(self) -> str:
        with open(self.index_file, "r") as f:
            index = json.load(f)
        last_id = index.get("last_episode_id", "EP-0000")
        num = int(last_id.split("-")[1])
        return f"EP-{num + 1:04d}"
        
    def find_existing_episode(self, dedup_key: str) -> bool:
        # Simplification: we don't index by dedup_key yet
        return False

    def save(self, episode: Dict[str, Any]) -> str:
        # [ALERTE MLOPS] Cryptographie de l'Evidence Store (Tamper-Evident)
        # On charge le dernier hash pour créer une chaîne inaltérable
        with open(self.index_file, "r") as f:
            index = json.load(f)
            
        previous_hash = index.get("last_hash", "genesis")
        
        # Injection du lien cryptographique
        episode["previous_hash"] = previous_hash
        
        # Sérialisation canonique (tri des clés, pas d'espaces)
        canonical_json = json.dumps(episode, sort_keys=True, separators=(',', ':'))
        
        # Hachage SHA-256
        current_hash = hashlib.sha256(canonical_json.encode('utf-8')).hexdigest()
        episode["hash"] = current_hash
        
        episode_id = episode.get("episode_id", self.next_episode_id())
        file_path = self.store_dir / f"{episode_id}.json"
        
        # Sauvegarde WORM (Write Once Read Many) simulée (append only locally)
        if file_path.exists():
            raise ValueError("Tentative de réécriture d'un épisode existant détectée ! Immuabilité compromise.")
            
        with open(file_path, "w") as f:
            json.dump(episode, f, indent=2)
            
        # Mise à jour de l'index avec le nouveau hash
        index["last_episode_id"] = episode_id
        index["last_hash"] = current_hash
        with open(self.index_file, "w") as f:
            json.dump(index, f, indent=2)
            
        return str(file_path)
