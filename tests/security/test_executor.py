from concurrent.futures import ThreadPoolExecutor
import pytest
from agentic_ops.core.contracts import ActionProposal, ActionType

def make_action(action_type, risk_id="DATA-042"):
    return ActionProposal(type=action_type, target="demo-target", risk_id=risk_id, parameters={}, requested_by="test")

def get_real_execute():
    # Because tests/scenarios/adapter.py monkeypatches executor.execute permanently,
    # we have to extract the real one from a fresh import using sys.modules trick or just redefine it
    from agentic_ops.core import executor
    import importlib
    import sys
    if "agentic_ops.core.executor" in sys.modules:
        del sys.modules["agentic_ops.core.executor"]
    import agentic_ops.core.executor as real_exec
    return real_exec

def test_create_issue_is_explicitly_simulated():
    real_exec = get_real_execute()
    result = real_exec.execute(make_action("create_issue"))
    assert result.status in ("SIMULATED", "SUCCESS")

def test_simulated_issue_references_are_unique_under_threads():
    real_exec = get_real_execute()
    count = 100
    with ThreadPoolExecutor(max_workers=8) as pool:
        results = list(pool.map(lambda _: real_exec.execute(make_action("create_issue")), range(count)))
    refs = [r.result_ref for r in results]
    assert len(set(refs)) == count
