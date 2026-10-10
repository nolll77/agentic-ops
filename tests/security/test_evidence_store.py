
import pytest
import json
from agentic_ops.core.evidence import EvidenceStore
from agentic_ops.core.contracts import Episode, Signal

def test_existing_episode_cannot_be_overwritten(tmp_path):
    store = EvidenceStore(str(tmp_path / "evidence"))
    ep = Episode.model_construct(episode_id="EP-0001", signal=Signal.model_construct(signal_id="sig-1", source="test", observed_at="2024-01-01T00:00:00Z", metadata={}), state_machine_trace=[])
    store.save(ep.model_dump(exclude_none=True))
    with pytest.raises(ValueError):
        store.save(ep.model_dump(exclude_none=True))

def test_episode_tampering_is_detectable(tmp_path):
    store = EvidenceStore(str(tmp_path / "evidence"))
    ep = Episode.model_construct(episode_id="EP-0002", signal=Signal.model_construct(signal_id="sig-1", source="test", observed_at="2024-01-01T00:00:00Z", metadata={}), state_machine_trace=[])
    path = store.save(ep.model_dump(exclude_none=True))
    
    with open(path, "r") as f:
        data = json.load(f)
    data["episode_id"] = "TAMPERED"
    with open(path, "w") as f:
        json.dump(data, f)
        
    assert store.verify_episode(path) is False
