from __future__ import annotations
from datetime import datetime, timedelta, timezone
from pathlib import Path
from pydantic import BaseModel
from .schema import Trigger
from agentic_ops.core.contracts import ActionType

T0 = datetime(2026, 1, 12, 9, 0, tzinfo=timezone.utc)

class Outcome(BaseModel):
    diagnosis_layer: str | None
    proposed_action: str | None
    policy_decision: str | None
    final_state: str

def build_signal(trigger: Trigger):
    from agentic_ops.core.contracts import Signal
    return Signal(
        signal_id="scenario_test",
        risk_id=trigger.risk_id,
        source=trigger.source,
        environment=trigger.environment,
        observed_at=T0 + timedelta(seconds=trigger.t),
        payload=trigger.payload,
        metadata={"tenant": "test", "service": "scenario"}
    )

def diagnosis_dict(layer: str, summary: str) -> dict:
    return {"risk_id": "test", "agent": "baseline", "layer": layer, "confidence_score": 0.9, "findings": [{"description": summary, "evidence_ref": []}]}

def proposal_dict(action: str, target: str) -> dict:
    return {"action": action, "target": target}

def success_result(proposal):
    from agentic_ops.core.contracts import ExecutionResult
    return ExecutionResult(status="success", details="recorded", result_ref="test", executor="test")

def build_orchestrator(*, llm, observability, executor, notifier, evidence_dir: Path, policy_path: Path):
    from agentic_ops.core.orchestrator import Orchestrator
    from agentic_ops.core.policy import PolicyEngine
    from agentic_ops.core.evidence import EvidenceStore
    # We patch executor logic in Orchestrator dynamically for testing (recording executor)
    import agentic_ops.core.executor as ext
    ext.execute = executor.execute
    
    return Orchestrator(
        llm=llm,
        observability=observability,
        policy_engine=PolicyEngine.from_yaml(policy_path),
        evidence_store=EvidenceStore(str(evidence_dir)),
        registry=None
    )

def handle(orchestrator, trigger):
    # Pass the risk_id directly to run
    return orchestrator.run(trigger.risk_id, "scenario_test")

def extract_outcome(episode) -> Outcome:
    if episode is None:
        return Outcome(diagnosis_layer=None, proposed_action=None, policy_decision=None, final_state="DROPPED")
    diag = getattr(episode, "diagnosis", None)
    prop = getattr(episode, "action_proposal", None)
    dec = getattr(episode, "policy_evaluation", None)
    return Outcome(
        diagnosis_layer=getattr(diag, "layer", None) if diag else None,
        proposed_action=str(getattr(prop, "type", getattr(prop, "action", None))) if prop else None,
        policy_decision=str(getattr(dec, "decision", None)) if dec else None,
        final_state=str(episode.state_trace[-1] if episode.state_trace else "UNKNOWN")
    )
