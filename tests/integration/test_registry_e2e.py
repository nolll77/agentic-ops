import pytest
import json
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

class SecurityException(Exception):
    pass

class MockOrchestrator:
    """Mock Orchestrator to enforce the Control Plane state machine"""
    def __init__(self, engine: PolicyEngine, exec_module, registry: SimulatedModelRegistry):
        self.engine = engine
        self.executor = exec_module
        self.registry = registry
        self.approvals = set()

    def approve_action(self, action_hash: str):
        self.approvals.add(action_hash)

    def process_action(self, action: ActionProposal):
        # 1. Policy Evaluation
        decision = self.engine._evaluate_single(action, self.engine.rules, is_shadow=False)
        
        # 2. Enforcement
        if decision.decision == DecisionEnum.DENY:
            raise SecurityException("Action is explicitly DENIED by policy")
            
        if decision.decision == DecisionEnum.REQUIRE_APPROVAL:
            action_hash = str(hash(action.json())) # simplified hash for the test
            if action_hash not in self.approvals:
                raise SecurityException("Action REQUIRES APPROVAL and has not been approved")
                
        # 3. Execution
        exec_result = self.executor.execute(action, registry=self.registry)
        
        return decision, exec_result


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
    
    orchestrator = MockOrchestrator(engine, executor, registry)

    # 2. Register and validate a model
    registry.register_model("v2.0", metrics={"f1_score": 0.95}, schema_compatible=True)
    registry.validate_promotion("v2.0")

    # 3. Simulate an Orchestrator receiving a promotion proposal
    action = ActionProposal(
        type=ActionType.PROMOTE_MODEL,
        risk_id="MODEL-001",
        requested_by="CI/CD Pipeline",
        parameters={"version": "v2.0"}
    )
    
    # 4. Attempt to process without approval (Must Fail)
    with pytest.raises(SecurityException, match="REQUIRES APPROVAL"):
        orchestrator.process_action(action)
        
    assert registry.active_version_id != "v2.0" # Registry remains untouched
    
    # 5. Provide Human Approval
    action_hash = str(hash(action.json()))
    orchestrator.approve_action(action_hash)
    
    # 6. Process again (Must Succeed)
    decision, exec_result = orchestrator.process_action(action)
    assert exec_result.status == "SIMULATED"
    
    # Registry was actually mutated by the executor!
    assert registry.active_version_id == "v2.0"

    # 7. Trust Ledger saves the Episode
    ep = Episode.model_construct(
        episode_id="EP-100",
        signal=Signal.model_construct(signal_id="sig-1", source="datadog", observed_at="2026-01-01T00:00:00Z"),
        action_proposal=action,
        policy_evaluation=decision,
        execution=exec_result,
        state_trace=["SIGNAL_RECEIVED", "APPROVAL", "RESOLVED"]
    )
    saved_path = store.save(ep.model_dump(exclude_none=True))
    
    # 8. Cryptographic verification
    assert store.verify_episode(saved_path) is True
    
    # Tampering test
    with open(saved_path, "r") as f:
        tampered_data = json.load(f)
    tampered_data["state_trace"] = ["TAMPERED"]
    with open(saved_path, "w") as f:
        json.dump(tampered_data, f)
        
    assert store.verify_episode(saved_path) is False

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
    
    # Test Negative Rollback (unapproved)
    with pytest.raises(SecurityException):
        orchestrator.process_action(rollback_action)
        
    # Approve and Execute Rollback
    orchestrator.approve_action(str(hash(rollback_action.json())))
    rollback_decision, rollback_exec = orchestrator.process_action(rollback_action)
    
    # Check that previous model is deactivated properly
    assert registry.active_version_id == "v1.5"
    assert registry.get_model("v2.0").deployment_status == ModelDeploymentStatusEnum.DEPLOYED
    assert registry.get_model("v1.5").deployment_status == ModelDeploymentStatusEnum.ACTIVE

def test_negative_promotion_denied_by_policy(tmp_path):
    registry = SimulatedModelRegistry()
    store = EvidenceStore(str(tmp_path / "evidence"))
    engine = PolicyEngine.__new__(PolicyEngine)
    engine.rules = {
        "promote_model": {"autonomy": "denied", "conditions": {}}
    }
    engine.shadow_rules = {}
    engine.evidence_store = store
    
    orchestrator = MockOrchestrator(engine, executor, registry)
    
    action = ActionProposal(
        type=ActionType.PROMOTE_MODEL,
        risk_id="MODEL-003",
        requested_by="Hacker",
        parameters={"version": "v9.9"}
    )
    
    with pytest.raises(SecurityException, match="explicitly DENIED"):
        orchestrator.process_action(action)
