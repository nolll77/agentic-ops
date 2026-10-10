
import pytest
from unittest.mock import Mock
from agentic_ops.core.contracts import ActionProposal, DecisionEnum
from agentic_ops.core.policy import PolicyEngine, PolicyUnavailable
from agentic_ops.core import policy as policy_module

def test_redis_failure_must_not_fail_open(monkeypatch):
    engine = PolicyEngine.__new__(PolicyEngine)
    engine.rules = {"restart_pod": {"autonomy": "autonomous", "conditions": {"rate_limit": "1/hour"}}}
    engine.shadow_rules = {}
    engine.evidence_store = Mock()
    
    redis = Mock()
    redis.pipeline.side_effect = ConnectionError("Redis unavailable")
    monkeypatch.setattr(policy_module.RedisClient, "get_client", lambda: redis)
    
    action = ActionProposal(type="restart_pod", risk_id="INFRA-001", parameters={}, requested_by="test")
    with pytest.raises(PolicyUnavailable):
        engine._evaluate_single(action, engine.rules, is_shadow=False)
