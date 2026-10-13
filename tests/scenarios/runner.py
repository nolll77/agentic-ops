from __future__ import annotations
import os
from pathlib import Path
from pydantic import BaseModel, Field
from . import adapter
from .schema import Scenario, Mode
from .stubs import (BaselineLLM, FakeObservability, RecordingExecutor,
                    RecordingLLM, RecordingNotifier, ScriptedLLM)

def _norm(a: str | None) -> str:
    return str(a or "").split(".")[-1].strip().lower()

class ScenarioResult(BaseModel):
    scenario_id: str
    mode: Mode
    diagnosis_layer: str | None
    diagnosis_correct: bool
    proposed_action: str
    forbidden_proposed: bool
    executed_actions: list[str]
    forbidden_executed: list[str]
    unlisted_executed: list[str]
    final_state: str
    final_state_ok: bool
    policy_decision: str | None
    approval_requested: bool
    llm_calls: int
    prompts: list[dict] = Field(default_factory=list, exclude=True)

def _make_llm(sc: Scenario, mode: Mode):
    if mode == "scripted":
        return ScriptedLLM(sc.llm_script)
    if mode == "baseline":
        return BaselineLLM(sc.telemetry)
    from agentic_ops.adapters.llm_protocol import LiteLLMAdapter
    return LiteLLMAdapter(model=os.environ.get("LIVE_LLM_MODEL", "gpt-4o"))

def run_scenario(sc: Scenario, mode: Mode, *, tmp_path: Path, policy_path: Path) -> ScenarioResult:
    llm = RecordingLLM(_make_llm(sc, mode))
    executor, notifier = RecordingExecutor(), RecordingNotifier()
    orch = adapter.build_orchestrator(
        llm=llm, observability=FakeObservability(sc.telemetry), executor=executor,
        notifier=notifier, evidence_dir=tmp_path / "evidence", policy_path=policy_path)

    # Patch the real orchestrator idempotency check to always pass during test if needed
    import agentic_ops.core.orchestrator as orch_module
    orch_module.acquire_idempotency_lock = lambda x, **kwargs: True

    episode = adapter.handle(orch, sc.trigger)
    out = adapter.extract_outcome(episode)

    forbidden = {_norm(a) for a in sc.expected.forbidden_actions}
    allowed = {_norm(a) for a in sc.expected.allowed_actions}
    executed = [_norm(c["action"]) for c in executor.executed]
    proposed = _norm(out.proposed_action)
    approval_requested = bool(notifier.requests) or "REQUIRE_APPROVAL" in str(out.policy_decision)
    forbidden_exec = sorted(set(executed) & forbidden)

    return ScenarioResult(
        scenario_id=sc.id, mode=mode,
        diagnosis_layer=out.diagnosis_layer,
        diagnosis_correct=out.diagnosis_layer == sc.ground_truth.root_cause_layer,
        proposed_action=proposed, forbidden_proposed=proposed in forbidden,
        executed_actions=executed,
        forbidden_executed=forbidden_exec,
        unlisted_executed=sorted(set(executed) - allowed),
        final_state=out.final_state,
        final_state_ok=out.final_state in sc.expected.final_states,
        policy_decision=out.policy_decision,
        approval_requested=approval_requested,
        llm_calls=len(llm.calls))

