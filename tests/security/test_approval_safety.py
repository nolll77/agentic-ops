import hashlib
import json

import pytest

from agentic_ops.core.approvals import (
    ApprovalExecutionWorker,
    ApprovalRepo,
    FrozenProposal,
    Result,
)


def make_proposal(episode_id="EP-APPROVAL"):
    return FrozenProposal(
        episode_id=episode_id,
        action="restart_pod",
        target="staging/api",
        risk_id="INFRA-001",
        policy_version="policy-1",
        required=2,
        required_groups=("SRE", "SECOPS"),
        requester_id="requester-1",
    )


def test_approval_rejects_self_approval_and_wrong_role(tmp_path):
    now = [100.0]
    repo = ApprovalRepo(str(tmp_path / "approvals.db"), clock=lambda: now[0])
    proposal = make_proposal()
    claim_hash = repo.open_request(proposal, ttl_s=60)

    result, claim = repo.decide(
        proposal.episode_id, "requester-1", "SRE", "approve", claim_hash, claim_hash
    )
    assert result is Result.SELF_APPROVAL
    assert claim is None

    result, claim = repo.decide(
        proposal.episode_id, "reviewer-1", "ADMIN", "approve", claim_hash, claim_hash
    )
    assert result is Result.UNAUTHORIZED
    assert claim is None


def test_quorum_requires_distinct_approvers_and_required_roles(tmp_path):
    repo = ApprovalRepo(str(tmp_path / "approvals.db"), clock=lambda: 100.0)
    proposal = make_proposal("EP-QUORUM")
    digest = repo.open_request(proposal, ttl_s=60)

    first, _ = repo.decide(proposal.episode_id, "reviewer-1", "SRE", "approve", digest, digest)
    duplicate_group, _ = repo.decide(
        proposal.episode_id, "reviewer-2", "SRE", "approve", digest, digest
    )
    complete, claim = repo.decide(
        proposal.episode_id, "reviewer-3", "SECOPS", "approve", digest, digest
    )

    assert first is Result.RECORDED
    assert duplicate_group is Result.RECORDED
    assert complete is Result.CLAIMED
    assert claim is not None


def test_quorum_revalidates_prior_role_membership(tmp_path):
    repo = ApprovalRepo(str(tmp_path / "approvals.db"), clock=lambda: 100.0)
    proposal = make_proposal("EP-REVOKED-ROLE")
    digest = repo.open_request(proposal, ttl_s=60)
    assert repo.decide(
        proposal.episode_id, "reviewer-1", "SRE", "approve", digest, digest
    )[0] is Result.RECORDED

    result, _ = repo.decide(
        proposal.episode_id,
        "reviewer-2",
        "SECOPS",
        "approve",
        digest,
        digest,
        eligible_group_for=lambda user: None if user == "reviewer-1" else "SECOPS",
    )
    assert result is Result.RECORDED


def test_approval_request_requires_requester_and_cannot_be_redefined(tmp_path):
    repo = ApprovalRepo(str(tmp_path / "approvals.db"), clock=lambda: 100.0)
    proposal = make_proposal("EP-IMMUTABLE")
    without_requester = FrozenProposal(
        episode_id="EP-NO-REQUESTER",
        action="restart_pod",
        target="staging/api",
        risk_id="INFRA-001",
        policy_version="policy-1",
        required=1,
    )
    with pytest.raises(ValueError, match="requester_id"):
        repo.open_request(without_requester, ttl_s=60)

    repo.open_request(proposal, ttl_s=60)
    changed = FrozenProposal(
        **{**proposal.__dict__, "target": "production/api"}
    )
    with pytest.raises(ValueError, match="different proposal"):
        repo.open_request(changed, ttl_s=60)


def test_legacy_request_without_requester_fails_closed(tmp_path):
    repo = ApprovalRepo(str(tmp_path / "approvals.db"), clock=lambda: 100.0)
    legacy = {
        "episode_id": "EP-LEGACY",
        "action": "restart_pod",
        "target": "staging/api",
        "risk_id": "INFRA-001",
        "policy_version": "policy-1",
        "required": 1,
        "required_groups": [],
    }
    digest = hashlib.sha256(
        json.dumps(legacy, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    conn = repo._conn()
    try:
        conn.execute(
            "INSERT INTO requests VALUES(?,?,?,?,?,?,?,?)",
            (
                legacy["episode_id"],
                digest,
                json.dumps(legacy),
                "PENDING",
                1,
                "[]",
                100.0,
                200.0,
            ),
        )
    finally:
        conn.close()

    result, _ = repo.decide(
        "EP-LEGACY", "reviewer", "SRE", "approve", digest, digest
    )
    assert result is Result.UNAUTHORIZED


def test_quorum_and_execution_outbox_are_atomic_and_leased(tmp_path):
    now = [100.0]
    repo = ApprovalRepo(str(tmp_path / "approvals.db"), clock=lambda: now[0])
    proposal = FrozenProposal(
        episode_id="EP-DURABLE-CLAIM",
        action="restart_pod",
        target="staging/api",
        risk_id="INFRA-001",
        policy_version="policy-1",
        required=1,
        required_groups=("SRE",),
        requester_id="requester-1",
    )
    digest = repo.open_request(proposal, ttl_s=60)
    decision, _ = repo.decide(
        proposal.episode_id, "reviewer-1", "SRE", "approve", digest, digest
    )
    assert decision is Result.CLAIMED

    first = repo.claim_execution("worker-a", lease_s=5)
    assert first is not None
    assert repo.claim_execution("worker-b", lease_s=5) is None
    now[0] += 6
    recovered = repo.claim_execution("worker-b", lease_s=5)
    assert recovered is not None
    assert recovered.proposal.episode_id == proposal.episode_id
    with pytest.raises(RuntimeError, match="does not own"):
        repo.finish_execution(proposal.episode_id, "worker-a", success=True)

    repo.finish_execution(proposal.episode_id, "worker-b", success=True)
    assert repo.claim_execution("worker-c") is None
    conn = repo._conn()
    try:
        request_status = conn.execute(
            "SELECT status FROM requests WHERE episode_id=?", (proposal.episode_id,)
        ).fetchone()["status"]
        outbox_status = conn.execute(
            "SELECT status FROM execution_outbox WHERE episode_id=?", (proposal.episode_id,)
        ).fetchone()["status"]
    finally:
        conn.close()
    assert request_status == "EXECUTED"
    assert outbox_status == "COMPLETED"


def test_approval_execution_worker_marks_success_and_failure(tmp_path):
    repo = ApprovalRepo(str(tmp_path / "approvals.db"), clock=lambda: 100.0)
    proposal = FrozenProposal(
        episode_id="EP-WORKER",
        action="restart_pod",
        target="staging/api",
        risk_id="INFRA-001",
        policy_version="policy-1",
        required=1,
        requester_id="requester-1",
    )
    digest = repo.open_request(proposal, ttl_s=60)
    assert repo.decide(
        proposal.episode_id, "reviewer-1", "SRE", "approve", digest, digest
    )[0] is Result.CLAIMED

    executed = []
    worker = ApprovalExecutionWorker(repo, "worker", lambda p: executed.append(p.episode_id))
    assert worker.run_once()
    assert executed == [proposal.episode_id]
    assert not worker.run_once()
