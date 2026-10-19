from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone

from agentic_ops.core.approvals import ApprovalRepo, Result
from agentic_ops.core.contracts import (
    ActionType,
    Decision,
    DecisionEnum,
    Diagnosis,
    Finding,
    Signal,
)
from agentic_ops.core.evidence import EvidenceStore
from agentic_ops.core.orchestrator import Orchestrator


class _Observability:
    def get_signal(self, signal_id: str) -> Signal:
        return Signal(
            signal_id=signal_id,
            source="test",
            observed_at=datetime.now(timezone.utc),
            metadata={"tenant": "test", "service": "api", "target": "service/api"},
        )


class _Policy:
    def decide(self, proposal, signal, episode, **kwargs):
        episode.policy_version = "policy-test"
        episode.inventory_version = "inventory-test"
        return Decision(
            decision=DecisionEnum.REQUIRE_APPROVAL,
            matched_rule="LEVEL-L2",
            approvals_required=2,
        )


class _Specialist:
    name = "test-specialist"

    def diagnose(self, risk_id, signal):
        return Diagnosis(
            risk_id=risk_id,
            findings=[Finding(description="deterministic test diagnosis")],
            confidence_score=1.0,
        )


def test_orchestrator_persists_frozen_approval_request_for_suspended_episode(
    tmp_path, monkeypatch
):
    database = str(tmp_path / "approvals.db")
    evidence_directory = tmp_path / "evidence"
    repo = ApprovalRepo(database, clock=lambda: 100.0)
    evidence = EvidenceStore(str(evidence_directory))
    orchestrator = Orchestrator(
        observability=_Observability(),
        policy_engine=_Policy(),
        evidence_store=evidence,
        approval_repo=repo,
        approval_requester_id="agentic-ops-test",
    )
    monkeypatch.setattr(orchestrator, "_get_specialist", lambda risk_id: _Specialist())
    monkeypatch.setattr(
        "agentic_ops.core.orchestrator.global_circuit_breaker.record_call",
        lambda: None,
    )
    monkeypatch.setattr(
        "agentic_ops.core.orchestrator.global_circuit_breaker.is_tripped",
        lambda: False,
    )

    episode = orchestrator.run(
        risk_id="INFRA-001",
        signal_id="signal-approval-test",
        forced_action=ActionType.RESTART_POD,
        idempotency_key="approval-test-idempotency",
    )

    assert episode.state_trace[-1] == "AWAITING_APPROVAL"
    assert episode.execution is None
    with sqlite3.connect(database) as connection:
        row = connection.execute(
            "SELECT hash, proposal, status FROM requests WHERE episode_id=?",
            (episode.episode_id,),
        ).fetchone()
    assert row is not None
    request_hash, serialized_proposal, status = row
    assert status == "PENDING"
    proposal_data = json.loads(serialized_proposal)
    assert proposal_data["requester_id"] == "agentic-ops-test"
    assert proposal_data["required"] == 2
    assert proposal_data["action"] == ActionType.RESTART_POD.value
    assert proposal_data["target"] == "service/api"
    assert orchestrator.current_proposal_hash(proposal_data) == request_hash

    # Retrying after evidence persistence must re-open the same request, not fork it.
    orchestrator.ensure_approval_request(episode.model_dump(mode="json"))
    assert repo.decide(
        episode.episode_id,
        "approver-one",
        "SRE",
        "approve",
        request_hash,
        request_hash,
    )[0] is Result.RECORDED
    assert repo.decide(
        episode.episode_id,
        "approver-two",
        "SRE_LEAD",
        "approve",
        request_hash,
        request_hash,
    )[0] is Result.CLAIMED
    with sqlite3.connect(database) as connection:
        assert connection.execute(
            "SELECT status FROM execution_outbox WHERE episode_id=?",
            (episode.episode_id,),
        ).fetchone()[0] == "RECEIVED"
