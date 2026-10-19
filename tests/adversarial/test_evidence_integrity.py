import pytest
import os
import json
from pathlib import Path
from agentic_ops.core.evidence import EvidenceStore

@pytest.fixture
def evidence_store(tmp_path):
    # Fix the environment key for tests
    os.environ["LEDGER_SECRET_KEY"] = "test-secret"
    return EvidenceStore(str(tmp_path / "evidence"))

def test_ledger_append_and_verify_chain(evidence_store):
    # Save a first episode
    evidence_store.save({"data": "incident-1", "action": "investigate"})
    # Save a second
    evidence_store.save({"data": "incident-2", "action": "deny"})
    
    assert evidence_store.verify_chain() is True

def test_ledger_tamper_payload_detected(evidence_store):
    evidence_store.save({"data": "incident-1", "action": "deny"})
    
    # Tamper the ledger file directly
    ledger_path = evidence_store.ledger_file
    with open(ledger_path, "r") as f:
        lines = f.readlines()
        
    # Modify the JSON
    modified_line = lines[0].replace("deny", "approve")
    
    with open(ledger_path, "w") as f:
        f.write(modified_line)
        
    assert evidence_store.verify_chain() is False

def test_ledger_tamper_chain_detected(evidence_store):
    evidence_store.save({"data": "incident-1"})
    evidence_store.save({"data": "incident-2"})
    
    # Delete the first line (breaking the chain)
    ledger_path = evidence_store.ledger_file
    with open(ledger_path, "r") as f:
        lines = f.readlines()
        
    with open(ledger_path, "w") as f:
        f.write(lines[1])
        
    assert evidence_store.verify_chain() is False


def test_crypto_fail_closed_in_production_without_key(monkeypatch):
    """Enforces strict Fail-Closed in production environment if no cryptographic key is supplied."""
    import importlib
    import agentic_ops.core.crypto as crypto_mod

    monkeypatch.setenv("AGENTIC_OPS_ENV", "production")
    monkeypatch.delenv("LEDGER_SECRET_KEY", raising=False)
    monkeypatch.delenv("EVIDENCE_STORE_HMAC_KEY", raising=False)

    with pytest.raises(RuntimeError, match=r"\[FAIL-CLOSED\]"):
        importlib.reload(crypto_mod)

    # Cleanup reload back to normal
    monkeypatch.delenv("AGENTIC_OPS_ENV", raising=False)
    importlib.reload(crypto_mod)

