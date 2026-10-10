import pytest
import json
import os
from pathlib import Path
from agentic_ops.core.evidence import EvidenceStore

def test_evidence_store_tampering(tmp_path):
    store = EvidenceStore(str(tmp_path / "evidence"))
    
    # Create Episode 1
    ep1 = {"episode_id": "EP-0001", "data": "hello"}
    path1 = store.save(ep1)
    
    assert store.verify_episode(path1) is True
    
    # Tamper state trace / data
    with open(path1, "r") as f:
        tampered_ep1 = json.load(f)
    tampered_ep1["data"] = "hacked"
    with open(path1, "w") as f:
        json.dump(tampered_ep1, f)
        
    assert store.verify_episode(path1) is False
    
    # Restore ep1
    with open(path1, "w") as f:
        json.dump(ep1, f)
    
    # Create Episode 2
    ep2 = {"episode_id": "EP-0002", "data": "world"}
    path2 = store.save(ep2)
    
    assert store.verify_episode(path2) is True
    
    # Tamper previous hash
    with open(path2, "r") as f:
        tampered_ep2 = json.load(f)
    tampered_ep2["previous_hash"] = "fake_hash"
    with open(path2, "w") as f:
        json.dump(tampered_ep2, f)
        
    assert store.verify_episode(path2) is False

