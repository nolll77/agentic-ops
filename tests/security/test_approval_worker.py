from __future__ import annotations

import json
import importlib
import sqlite3
from pathlib import Path
from types import SimpleNamespace

import pytest

from agentic_ops.core.approvals import ApprovalRepo, FrozenProposal, Result
from agentic_ops.core.evidence import EvidenceStore
from agentic_ops.entrypoints import approval_worker


@pytest.fixture(autouse=True)
def restore_executor_module():
    # The scenario adapter replaces executor.execute globally for its simulations.
    importlib.reload(approval_worker.executor)


def _approved_request(database: str, *, episode_id: str = "EP-APPROVAL-WORKER") -> str:
    repo = ApprovalRepo(database, clock=lambda: 100.0)
    proposal = FrozenProposal(
        episode_id=episode_id,
        action="create_issue",
        target="staging/api",
        risk_id="INFRA-001",
        policy_version="policy-1",
        required=1,
        required_groups=("SRE",),
        requester_id="requester-1",
    )
    digest = repo.open_request(proposal, ttl_s=60)
    assert repo.decide(
        episode_id, "approver-1", "SRE", "approve", digest, digest
    )[0] is Result.CLAIMED
    evidence = EvidenceStore(str(Path(database).parent / "episodes"))
    evidence.save(
        {
            "episode_id": episode_id,
            "state_trace": [
                "DETECTED",
                "INVESTIGATING",
                "DIAGNOSED",
                "PLANNED",
                "AWAITING_APPROVAL",
            ],
            "risk_id": "INFRA-001",
            "action_proposal": {
                "type": "create_issue",
                "target": "staging/api",
                "risk_id": "INFRA-001",
            },
            "human_approval_required": True,
            "execution": None,
        }
    )
    return episode_id


def test_approval_worker_resumes_quorum_in_simulation_and_persists_result(
    tmp_path, monkeypatch
):
    database = str(tmp_path / "approvals.db")
    episode_id = _approved_request(database)
    monkeypatch.setenv("APPROVAL_DB_PATH", database)
    monkeypatch.setenv("EVIDENCE_STORE_DIR", str(tmp_path / "episodes"))
    monkeypatch.setenv(
        "SLACK_APPROVERS_JSON",
        json.dumps({"approver-1": ["SRE"]}),
    )

    worker = approval_worker.build_worker()
    assert worker.run_once()
    assert not worker.run_once()

    with sqlite3.connect(database) as conn:
        request_status = conn.execute(
            "SELECT status FROM requests WHERE episode_id=?", (episode_id,)
        ).fetchone()[0]
        outbox_status = conn.execute(
            "SELECT status FROM execution_outbox WHERE episode_id=?", (episode_id,)
        ).fetchone()[0]
    assert request_status == "SIMULATED"
    assert outbox_status == "COMPLETED"
    resumed = EvidenceStore(str(tmp_path / "episodes")).find_latest_episode(episode_id)
    assert resumed is not None
    assert resumed["state_trace"][-2:] == ["EXECUTING", "RESOLVED"]
    assert resumed["execution"]["status"] == "SIMULATED"
    assert resumed["approval_resume"]["decision"] == "APPROVE"
    assert EvidenceStore(str(tmp_path / "episodes")).verify_chain()


def test_approval_worker_rechecks_current_roles_before_simulation(tmp_path, monkeypatch):
    database = str(tmp_path / "approvals.db")
    episode_id = _approved_request(database, episode_id="EP-REVOKED-APPROVER")
    monkeypatch.setenv("APPROVAL_DB_PATH", database)
    monkeypatch.setenv("EVIDENCE_STORE_DIR", str(tmp_path / "episodes"))
    monkeypatch.setenv("SLACK_APPROVERS_JSON", json.dumps({"approver-1": ["SRE"]}))

    worker = approval_worker.build_worker()
    monkeypatch.setenv("SLACK_APPROVERS_JSON", json.dumps({"approver-1": ["SECOPS"]}))
    assert worker.run_once()

    with sqlite3.connect(database) as conn:
        request_status = conn.execute(
            "SELECT status FROM requests WHERE episode_id=?", (episode_id,)
        ).fetchone()[0]
        outbox_status, last_error = conn.execute(
            "SELECT status, last_error FROM execution_outbox WHERE episode_id=?",
            (episode_id,),
        ).fetchone()
    assert request_status == "CLAIMED"
    assert outbox_status == "RETRY"
    assert last_error == "RuntimeError"


def test_approval_recovery_after_evidence_append_does_not_repeat_simulation(
    tmp_path, monkeypatch
):
    database = str(tmp_path / "approvals.db")
    episode_id = _approved_request(database, episode_id="EP-ACK-CRASH")
    monkeypatch.setenv("APPROVAL_DB_PATH", database)
    monkeypatch.setenv("EVIDENCE_STORE_DIR", str(tmp_path / "episodes"))
    monkeypatch.setenv("SLACK_APPROVERS_JSON", json.dumps({"approver-1": ["SRE"]}))
    now = [100.0]
    monkeypatch.setattr(approval_worker.time, "time", lambda: now[0])
    worker = approval_worker.build_worker()
    simulated = []

    def execute_once(action):
        simulated.append(action.type.value)
        return SimpleNamespace(status="SIMULATED", details="simulated")

    monkeypatch.setattr(approval_worker.executor, "execute", execute_once)
    finish = worker.repo.finish_execution

    def crash_before_ack(*args, **kwargs):
        raise RuntimeError("simulated interruption before outbox acknowledgement")

    monkeypatch.setattr(worker.repo, "finish_execution", crash_before_ack)
    with pytest.raises(RuntimeError, match="interruption"):
        worker.run_once()
    assert simulated == ["create_issue"]

    now[0] += 61
    monkeypatch.setattr(worker.repo, "finish_execution", finish)
    assert worker.run_once()
    assert simulated == ["create_issue"]
    with sqlite3.connect(database) as conn:
        assert conn.execute(
            "SELECT status FROM requests WHERE episode_id=?", (episode_id,)
        ).fetchone()[0] == "SIMULATED"
    assert EvidenceStore(str(tmp_path / "episodes")).verify_chain()


def test_approval_worker_refuses_live_execution_mode(monkeypatch):
    monkeypatch.setattr(approval_worker.executor, "SIMULATION_MODE", False)
    with pytest.raises(RuntimeError, match="simulation-only"):
        approval_worker.build_worker()
