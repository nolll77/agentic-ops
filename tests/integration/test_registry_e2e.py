import pytest
from pathlib import Path
from agentic_ops.adapters.registry_adapter import SimulatedModelRegistry
from agentic_ops.core.policy import PolicyEngine
from agentic_ops.core.evidence import EvidenceStore
from agentic_ops.core.contracts import (
    ActionProposal, 
    ActionType, 
    DecisionEnum, 
    ModelRegistryStatusEnum,
    ModelDeploymentStatusEnum,
    Episode,
    Signal
)
from agentic_ops.core import executor

def test_e2e_model_promotion_and_rollback(tmp_path):
    # 1. Setup the MLOps Control Plane
    registry = SimulatedModelRegistry()
    store = EvidenceStore(str(tmp_path / "evidence"))
    engine = PolicyEngine.__new__(PolicyEngine)
    engine.rules = {
        "promote_model": {"autonomy": "human_approval_required", "conditions": {}},
        "rollback": {"autonomy": "human_approval_required", "conditions": {}}
    }
    engine.shadow_rules = {}
    engine.evidence_store = store

    # 2. Register and validate a model
    registry.register_model("v2.0", metrics={"f1_score": 0.95}, schema_compatible=True)
    assert registry.validate_promotion("v2.0") is True

    # 3. Simulate an Orchestrator receiving a promotion proposal
    action = ActionProposal(
        type=ActionType.PROMOTE_MODEL,
        risk_id="MODEL-001",
        requested_by="CI/CD Pipeline",
        parameters={"version": "v2.0"}
    )
    
    # 4. Policy Engine evaluates the proposal
    decision = engine._evaluate_single(action, engine.rules, is_shadow=False)
    assert decision.decision == DecisionEnum.REQUIRE_APPROVAL
    
    # 5. Simulate Human Approval -> Execution
    exec_result = executor.execute(action)
    assert exec_result.status == "SIMULATED"
    assert "Promotion du modèle simulée" in exec_result.details
    
    # Actually trigger the registry change (in reality done by the adapter inside the executor)
    registry.promote_model("v2.0")
    assert registry.active_version_id == "v2.0"

    # 6. Trust Ledger saves the Episode
    ep = Episode.model_construct(
        episode_id="EP-100",
        signal=Signal.model_construct(signal_id="sig-1", source="datadog", observed_at="2026-01-01T00:00:00Z"),
        action_proposal=action,
        policy_evaluation=decision,
        execution=exec_result,
        state_trace=["SIGNAL_RECEIVED", "APPROVAL", "RESOLVED"]
    )
    store.save(ep.model_dump(exclude_none=True))

    # --- SIMULATE REGRESSION ---
    # Register an old stable version
    registry.register_model("v1.5", metrics={"f1_score": 0.90}, schema_compatible=True)
    registry.validate_promotion("v1.5")
    
    # Rollback action
    rollback_action = ActionProposal(
        type=ActionType.ROLLBACK,
        risk_id="MODEL-002",
        requested_by="Drift Monitor",
        parameters={"version": "v1.5"}
    )
    rollback_decision = engine._evaluate_single(rollback_action, engine.rules, is_shadow=False)
    assert rollback_decision.decision == DecisionEnum.REQUIRE_APPROVAL
    
    # Execute Rollback
    rollback_exec = executor.execute(rollback_action)
    assert rollback_exec.status == "SIMULATED"
    
    # Check that previous model is deactivated properly
    registry.rollback_model("v1.5")
    assert registry.active_version_id == "v1.5"
    assert registry.get_model("v2.0").deployment_status == ModelDeploymentStatusEnum.DEPLOYED
    assert registry.get_model("v1.5").deployment_status == ModelDeploymentStatusEnum.ACTIVE

    # Check bad rollback
    registry.register_model("v3.0-bad", metrics={"f1_score": 0.50}, schema_compatible=True)
    registry.validate_promotion("v3.0-bad") # Returns False, status=REJECTED
    bad_rollback = registry.rollback_model("v3.0-bad")
    assert bad_rollback is False # Cannot rollback to unvalidated model
