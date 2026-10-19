from __future__ import annotations

import os
import stat

from agentic_ops.core.contracts import ActionProposal


QUALIFIED_LIVE_ACTIONS: frozenset[str] = frozenset()


def live_execution_block_reason(action: ActionProposal, simulation_mode: bool) -> str | None:
    if simulation_mode:
        return "simulation mode is enabled"
    if os.environ.get("ALLOW_LIVE_EXECUTION", "").lower() != "true":
        return "live execution has not been explicitly enabled"
    if os.environ.get("LIVE_EXECUTION_ACK") != "I_UNDERSTAND_LIVE_MUTATIONS":
        return "live execution acknowledgement is missing"

    profile = os.environ.get("EXECUTION_PROFILE", "")
    if profile not in {"staging", "production"}:
        return "a qualified staging or production execution profile is required"

    allowed_actions = {
        item.strip().lower()
        for item in os.environ.get("LIVE_EXECUTION_ACTIONS", "").split(",")
        if item.strip()
    }
    if action.type.value.lower() not in allowed_actions:
        return f"action {action.type.value!r} is not explicitly allowlisted"

    allowed_targets = {
        item.strip()
        for item in os.environ.get("LIVE_EXECUTION_TARGETS", "").split(",")
        if item.strip()
    }
    if not action.target or action.target not in allowed_targets:
        return f"target {action.target!r} is not explicitly allowlisted"
    if action.type.value.lower() not in QUALIFIED_LIVE_ACTIONS:
        return f"no live adapter is qualified for action {action.type.value!r}"

    switch_path = os.environ.get("KILL_SWITCH_FILE")
    if not switch_path:
        return "kill-switch file path is not configured"
    parent = os.path.dirname(os.path.abspath(switch_path))
    if not os.path.isdir(parent):
        return "kill-switch control directory is unavailable"
    try:
        mode = os.lstat(switch_path).st_mode
    except FileNotFoundError:
        return None
    except OSError as exc:
        return f"kill-switch state cannot be checked: {type(exc).__name__}"
    if stat.S_ISLNK(mode) or stat.S_ISREG(mode) or stat.S_ISDIR(mode):
        return "kill-switch is active"
    return "kill-switch state is unsupported"
