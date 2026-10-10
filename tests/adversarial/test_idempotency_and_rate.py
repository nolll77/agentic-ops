import pytest
import os
import uuid
from agentic_ops.core.distributed import RedisClient
from agentic_ops.core.idempotency import compute_semantic_fingerprint, acquire_idempotency_lock, release_idempotency_lock

def test_production_fails_without_redis(monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.setenv("REDIS_PORT", "9999")
    RedisClient._instance = None
    
    with pytest.raises(RuntimeError, match="critique en production"):
        RedisClient.get_client()

def test_lock_acquire_and_release(monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "development")
    monkeypatch.setenv("REDIS_PORT", "9999")
    RedisClient._instance = None
    
    fp = compute_semantic_fingerprint("tenantA", "dev", "srv", "risk-1")
    owner = acquire_idempotency_lock(fp)
    assert owner != ""
    assert acquire_idempotency_lock(fp) == ""
    assert release_idempotency_lock(fp, str(uuid.uuid4())) is False
    assert release_idempotency_lock(fp, owner) is True
    assert acquire_idempotency_lock(fp) != ""
