import pytest
import json
from pathlib import Path
from agentic_ops.adapters.registry_adapter import SimulatedModelRegistry
from agentic_ops.core.policy import PolicyEngine
from agentic_ops.core.evidence import EvidenceStore
from agentic_ops.core.orchestrator import Orchestrator
from agentic_ops.core.contracts import (
    ActionProposal, 
    ActionType, 
    DecisionEnum, 
    ModelRegistryStatusEnum,
    ModelDeploymentStatusEnum,
    Signal
)

class DummyObservability:
    def get_signal(self, signal_id: str) -> Signal:
        return Signal(signal_id=signal_id, source="test", observed_at="2026-01-01T00:00:00Z")

class DummySpecialist:
    name = "dummy_specialist"
    def diagnose(self, risk_id, signal):
        from agentic_ops.core.contracts import Diagnosis, Finding
        return Diagnosis(findings=[Finding(description="Test finding")], confidence_score=1.0)

def test_true_e2e_governance(tmp_path, monkeypatch):
    registry = SimulatedModelRegistry()

    # Mock orchestrator._get_specialist to bypass LLM calls
    def mock_get_specialist(self, risk_id):
        return DummySpecialist()
    monkeypatch.setattr(Orchestrator, "_get_specialist", mock_get_specialist)

    store = EvidenceStore(str(tmp_path / "evidence"))
    engine = PolicyEngine.__new__(PolicyEngine)
    engine.rules = {
        "promote_model": {"autonomy": "human_approval_required", "conditions": {}},
        "rollback": {"autonomy": "human_approval_required", "conditions": {}}
    }
    engine.shadow_rules = {}
    engine.evidence_store = store

    orchestrator = Orchestrator(
        observability=DummyObservability(),
        policy_engine=engine,
        evidence_store=store,
        registry=registry
    )

    # 1. Register a valid model
    registry.register_model("v2.0", metrics={"f1_score": 0.95}, schema_compatible=True)
    registry.validate_promotion("v2.0")

    # 2. Run Orchestrator (it will stop at AWAITING_APPROVAL because of Policy)
    ep1 = orchestrator.run(risk_id="MODEL-001", forced_action=ActionType.PROMOTE_MODEL)

    assert ep1.state_trace[-1] == "AWAITING_APPROVAL"
    assert ep1.human_approval_required is True
    assert ep1.execution is None

    # Check that registry has NOT been mutated!
    assert registry.active_version_id is None

    # 3. Resume the episode with an APPROVE decision
    ep_dict = ep1.model_dump(mode='json', exclude_none=True)
    ep_dict["action_proposal"]["parameters"] = {"version": "v2.0"}
    ep_dict["human_approval"] = {
        "required": True,
        "approval_record": {
            "decision": "APPROVE",
            "approved_by": "alice",
            "timestamp": 123456789,
            "signature_verified": True
        }
    }

    resumed_ep = orchestrator.resume_episode(ep_dict)

    # Check execution actually occurred and registry mutated
    assert resumed_ep.execution is not None
    assert resumed_ep.execution.status == "SIMULATED"
    assert registry.active_version_id == "v2.0"

    # --- SIMULATE DENY ---
    # We propose rolling back to v1.0 (which doesn't exist)
    ep2 = orchestrator.run(risk_id="MODEL-002", forced_action=ActionType.ROLLBACK)
    assert ep2.state_trace[-1] == "AWAITING_APPROVAL"

    ep2_dict = ep2.model_dump(mode='json', exclude_none=True)
    ep2_dict["action_proposal"]["parameters"] = {"version": "v1.0"}
    ep2_dict["human_approval"] = {
        "approval_record": {"decision": "DENY", "approved_by": "bob"}
    }
    resumed_ep2 = orchestrator.resume_episode(ep2_dict)

    # Execution must be None because it was denied
    assert resumed_ep2.execution is None
    assert resumed_ep2.state_trace[-1] == "DENIED"
    assert registry.active_version_id == "v2.0" # Unchanged

    # --- SIMULATE FAILED EXECUTION (Registry Rejects) ---
    # If approved but registry rejects it (e.g. version not validated)
    registry.register_model("v3.0", metrics={"f1_score": 0.50}, schema_compatible=True)
    registry.validate_promotion("v3.0") # Returns False

    ep3 = orchestrator.run(risk_id="MODEL-003", forced_action=ActionType.PROMOTE_MODEL)
    ep3_dict = ep3.model_dump(mode='json', exclude_none=True)
    ep3_dict["action_proposal"]["parameters"] = {"version": "v3.0"}
    ep3_dict["human_approval"] = {
        "approval_record": {"decision": "APPROVE", "approved_by": "charlie"}
    }
    resumed_ep3 = orchestrator.resume_episode(ep3_dict)

    # Execution occurred but FAILED
    assert resumed_ep3.execution.status == "FAILED"
    assert "échoué" in resumed_ep3.execution.details
    assert registry.active_version_id == "v2.0" # Unchanged

