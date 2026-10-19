from __future__ import annotations

import argparse
import json
import logging
import os
import time
from pathlib import Path

from agentic_ops.core import executor
from agentic_ops.core.approvals import (
    ApprovalExecutionWorker,
    ApprovalRepo,
    FrozenProposal,
)
from agentic_ops.core.contracts import ActionProposal, ActionType
from agentic_ops.core.entra_scim import SCIMDirectory, scim_database_path, scim_enabled


def _approver_directory() -> dict[str, set[str]]:
    path = os.environ.get("SLACK_APPROVERS_FILE")
    if path:
        try:
            raw = Path(path).read_text(encoding="utf-8")
        except OSError as exc:
            raise ValueError("cannot read SLACK_APPROVERS_FILE") from exc
    else:
        raw = os.environ.get("SLACK_APPROVERS_JSON", "")
    if not raw:
        return {}
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError("SLACK_APPROVERS_JSON must be valid JSON") from exc
    if not isinstance(parsed, dict):
        raise ValueError("SLACK_APPROVERS_JSON must map Slack user IDs to role arrays")
    directory: dict[str, set[str]] = {}
    allowed = {"SRE", "SRE_LEAD", "DATA_STEWARD", "SECOPS"}
    for user_id, groups in parsed.items():
        if not isinstance(user_id, str) or not user_id.strip() or not isinstance(groups, list):
            raise ValueError("approver directory entries must map non-empty user IDs to arrays")
        if any(not isinstance(group, str) or group not in allowed for group in groups):
            raise ValueError(f"approver {user_id!r} has an unknown or invalid role")
        directory[user_id] = set(groups)
    return directory


def build_worker() -> ApprovalExecutionWorker:
    if not executor.SIMULATION_MODE:
        raise RuntimeError(
            "approval worker is simulation-only until an action-specific live profile is qualified"
        )

    database_path = os.environ.get("APPROVAL_DB_PATH", "state/approvals.db")
    if database_path == ":memory:":
        raise ValueError("APPROVAL_DB_PATH must be persistent for the approval worker")
    repo = ApprovalRepo(database_path, time.time)
    enterprise_directory = None
    if scim_enabled():
        identity_path = scim_database_path()
        if identity_path == ":memory:":
            raise ValueError("SCIM_DB_PATH must be persistent for the approval worker")
        enterprise_directory = SCIMDirectory(identity_path, time.time)
    else:
        _approver_directory()

    def execute_approved(proposal: FrozenProposal) -> str:
        directory = _approver_directory()
        approvals = repo.approvals_for(proposal.episode_id)
        if len(approvals) < proposal.required:
            raise RuntimeError("approval quorum is no longer present")
        current_groups = {group for _, group in approvals}
        if not set(proposal.required_groups).issubset(current_groups):
            raise RuntimeError("approval group quorum is no longer present")
        for approver, group in approvals:
            current_roles = (
                enterprise_directory.roles_for_external_id(approver)
                if enterprise_directory is not None
                else _approver_directory().get(approver, set())
            )
            if group not in current_roles:
                raise RuntimeError("an approver role is no longer authorized")

        try:
            action_type = ActionType(proposal.action)
        except ValueError as exc:
            raise RuntimeError(f"unsupported approved action {proposal.action!r}") from exc
        action = ActionProposal(
            type=action_type,
            target=proposal.target,
            risk_id=proposal.risk_id,
            requested_by=proposal.requester_id,
        )
        result = executor.execute(action)
        if result.status != "SIMULATED":
            raise RuntimeError(
                f"simulation executor did not safely simulate {proposal.action}: {result.status}"
            )
        logging.getLogger(__name__).info(
            "approved action simulated episode_id=%s action=%s",
            proposal.episode_id,
            proposal.action,
        )
        return "SIMULATED"

    return ApprovalExecutionWorker(
        repo,
        os.environ.get("APPROVAL_WORKER_ID", f"approval-sim-{os.getpid()}"),
        execute_approved,
    )


def run_approval_worker(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Resume approved actions in simulation-only mode."
    )
    parser.add_argument("--once", action="store_true", help="process at most one claim and exit")
    parser.add_argument(
        "--poll-interval-seconds",
        type=float,
        default=1.0,
        help="delay between empty queue polls (default: 1 second)",
    )
    args = parser.parse_args(argv)
    if args.poll_interval_seconds <= 0:
        parser.error("--poll-interval-seconds must be positive")

    logging.basicConfig(level=os.environ.get("LOG_LEVEL", "INFO"))
    worker = build_worker()
    if args.once:
        worker.run_once()
        return 0
    logging.getLogger(__name__).info("approval execution worker started (simulation only)")
    try:
        while True:
            if not worker.run_once():
                time.sleep(args.poll_interval_seconds)
    except KeyboardInterrupt:
        logging.getLogger(__name__).info("approval execution worker stopped")
        return 0


if __name__ == "__main__":
    raise SystemExit(run_approval_worker())
