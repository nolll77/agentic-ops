import pytest
import os
import tempfile
import json
from agentic_ops.core.evidence import EvidenceStore

def test_tamper_evident_hash_chain():
    with tempfile.TemporaryDirectory() as tmpdir:
        store = EvidenceStore(store_dir=tmpdir)
        
        # Sauvegarde épisode 1
        ep1 = {"action": "investigate"}
        path1 = store.save(ep1)
        
        with open(path1, "r") as f:
            data1 = json.load(f)
        
        assert data1["previous_hash"] == "genesis"
        assert "hash" in data1
        
        # Sauvegarde épisode 2
        ep2 = {"action": "remediate"}
        path2 = store.save(ep2)
        
        with open(path2, "r") as f:
            data2 = json.load(f)
            
        assert data2["previous_hash"] == data1["hash"]
        assert data2["hash"] != data1["hash"]

def test_worm_protection():
    with tempfile.TemporaryDirectory() as tmpdir:
        store = EvidenceStore(store_dir=tmpdir)
        ep = {"episode_id": "EP-9999", "data": "test"}
        store.save(ep)
        
        # Tentative d'écrasement (WORM violation)
        with pytest.raises(ValueError, match="Immuabilité compromise"):
            store.save(ep)
