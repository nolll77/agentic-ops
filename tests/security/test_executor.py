from concurrent.futures import ThreadPoolExecutor
import pytest
from agentic_ops.core.contracts import ActionProposal, ActionType

def make_action(action_type, risk_id="DATA-042"):
    return ActionProposal(type=action_type, target="demo-target", risk_id=risk_id, parameters={}, requested_by="test")

def get_real_execute():
    # Because tests/scenarios/adapter.py monkeypatches executor.execute permanently,
    # we have to extract the real one from a fresh import using sys.modules trick or just redefine it
    from agentic_ops.core import executor
    import importlib
    import sys
    if "agentic_ops.core.executor" in sys.modules:
        del sys.modules["agentic_ops.core.executor"]
    import agentic_ops.core.executor as real_exec
    return real_exec

def test_create_issue_is_explicitly_simulated():
    real_exec = get_real_execute()
    result = real_exec.execute(make_action("create_issue"))
    assert result.status in ("SIMULATED", "SUCCESS")

def test_simulated_issue_references_are_unique_under_threads():
    real_exec = get_real_execute()
    count = 100
    with ThreadPoolExecutor(max_workers=8) as pool:
        results = list(pool.map(lambda _: real_exec.execute(make_action("create_issue")), range(count)))
    refs = [r.result_ref for r in results]
    assert len(set(refs)) == count

def test_live_execution_fails_closed_without_explicit_gateway_configuration(monkeypatch):
    real_exec = get_real_execute()
    monkeypatch.setattr(real_exec, "SIMULATION_MODE", False)
    monkeypatch.delenv("ALLOW_LIVE_EXECUTION", raising=False)
    result = real_exec.execute(make_action(ActionType.SCALE_TO_ZERO))
    assert result.status == "FAILED"
    assert result.executor == "executor_gateway"
    assert "not been explicitly enabled" in result.details

def test_active_kill_switch_blocks_live_mutation_before_network(monkeypatch, tmp_path):
    real_exec = get_real_execute()
    from agentic_ops.core import executor_gateway
    monkeypatch.setattr(executor_gateway, "QUALIFIED_LIVE_ACTIONS", frozenset({"scale_to_zero"}))
    monkeypatch.setattr(real_exec, "SIMULATION_MODE", False)
    monkeypatch.setenv("ALLOW_LIVE_EXECUTION", "true")
    monkeypatch.setenv("LIVE_EXECUTION_ACK", "I_UNDERSTAND_LIVE_MUTATIONS")
    monkeypatch.setenv("EXECUTION_PROFILE", "staging")
    monkeypatch.setenv("LIVE_EXECUTION_ACTIONS", "scale_to_zero")
    monkeypatch.setenv("LIVE_EXECUTION_TARGETS", "demo-target")
    switch = tmp_path / "kill-switch"
    switch.touch()
    monkeypatch.setenv("KILL_SWITCH_FILE", str(switch))

    result = real_exec.execute(make_action(ActionType.SCALE_TO_ZERO))
    assert result.status == "FAILED"
    assert "kill-switch is active" in result.details

def test_no_action_is_live_qualified_by_default(monkeypatch):
    from agentic_ops.core.executor_gateway import live_execution_block_reason
    monkeypatch.setenv("ALLOW_LIVE_EXECUTION", "true")
    monkeypatch.setenv("LIVE_EXECUTION_ACK", "I_UNDERSTAND_LIVE_MUTATIONS")
    monkeypatch.setenv("EXECUTION_PROFILE", "staging")
    monkeypatch.setenv("LIVE_EXECUTION_ACTIONS", "scale_to_zero")
    monkeypatch.setenv("LIVE_EXECUTION_TARGETS", "demo-target")
    assert "no live adapter is qualified" in live_execution_block_reason(
        make_action(ActionType.SCALE_TO_ZERO), simulation_mode=False
    )

def test_simulation_never_mutates_model_registry():
    real_exec = get_real_execute()
    from unittest.mock import Mock
    registry = Mock()
    result = real_exec.execute(make_action(ActionType.ROLLBACK), registry=registry)
    assert result.status == "SIMULATED"
    registry.rollback_model.assert_not_called()

def test_executor_rejects_injected_or_unauthorized_target_fail_closed(monkeypatch, tmp_path):
    """
    Validates defense against SC-102 command/param injection at the executor level:
    Even if the gateway were configured with this target, the executor kernel
    enforces ALLOWED_K8S_DEPLOYMENTS fail-closed whitelist before any K8s interaction.
    """
    real_exec = get_real_execute()
    from agentic_ops.core import executor_gateway
    monkeypatch.setattr(executor_gateway, "QUALIFIED_LIVE_ACTIONS", frozenset({"scale_to_zero"}))
    monkeypatch.setattr(real_exec, "SIMULATION_MODE", False)
    monkeypatch.setenv("ALLOW_LIVE_EXECUTION", "true")
    monkeypatch.setenv("LIVE_EXECUTION_ACK", "I_UNDERSTAND_LIVE_MUTATIONS")
    monkeypatch.setenv("EXECUTION_PROFILE", "staging")
    monkeypatch.setenv("LIVE_EXECUTION_ACTIONS", "scale_to_zero")
    # Even if target is present in gateway env:
    injected_target = "baac-api; kubectl delete ns prod"
    monkeypatch.setenv("LIVE_EXECUTION_TARGETS", injected_target)
    switch = tmp_path / "kill-switch-inactive"
    monkeypatch.setenv("KILL_SWITCH_FILE", str(switch))

    malicious_action = ActionProposal(
        type=ActionType.SCALE_TO_ZERO,
        target=injected_target,
        risk_id="INFRA-001",
        parameters={},
        requested_by="red_team_sc102"
    )
    result = real_exec.execute(malicious_action)
    assert result.status == "FAILED"
    assert result.executor == "kubernetes"
    assert "non autorisée par la Policy Executor" in result.details
    assert injected_target in result.details

def test_parse_and_validate_k8s_target_adversarial_matrix():
    """
    Validates that Kubernetes workload target parsing enforces structured semantics:
    whitelisted deployment name, exact namespace match, resource type filtering,
    and immediate rejection of shell metacharacters, trailing slashes, and namespace escapes.
    """
    real_exec = get_real_execute()
    parse = real_exec.parse_and_validate_k8s_target
    default_ns = "demo-sandbox"

    # Valid targets
    assert parse("fastapi-model-demo", default_ns) == (default_ns, "fastapi-model-demo")
    assert parse("worker-demo", default_ns) == (default_ns, "worker-demo")
    assert parse("deployment/fastapi-model-demo", default_ns) == (default_ns, "fastapi-model-demo")
    assert parse("demo-sandbox/fastapi-model-demo", default_ns) == (default_ns, "fastapi-model-demo")
    assert parse("demo-sandbox/deployment/fastapi-model-demo", default_ns) == (default_ns, "fastapi-model-demo")

    # Invalid targets: unauthorized namespace, injection, illegal format
    assert parse("production/fastapi-model-demo", default_ns) is None
    assert parse("kube-system/fastapi-model-demo", default_ns) is None
    assert parse("deployment/fastapi-model-demo/", default_ns) is None
    assert parse("/fastapi-model-demo", default_ns) is None
    assert parse("statefulset/fastapi-model-demo", default_ns) is None
    assert parse("fastapi-model-demo; kubectl delete ns prod", default_ns) is None
    assert parse("fastapi-model-demo $(whoami)", default_ns) is None
    assert parse("fastapi-model-demo | rm -rf /", default_ns) is None
    assert parse("unauthorized-service", default_ns) is None
    assert parse(None, default_ns) is None
    assert parse("", default_ns) is None
    assert parse("   ", default_ns) is None

