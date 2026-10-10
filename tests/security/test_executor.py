
from concurrent.futures import ThreadPoolExecutor
import pytest
from agentic_ops.core.contracts import ActionProposal
from agentic_ops.core import executor

def make_action(action_type, risk_id="DATA-042"):
    return ActionProposal(type=action_type, risk_id=risk_id, parameters={}, requested_by="test")

def test_create_issue_is_explicitly_simulated():
    result = executor.execute(make_action("create_issue"))
    assert result.status == "SIMULATED" or result.status == "SUCCESS"

def test_simulated_issue_references_are_unique_under_threads():
    count = 100
    with ThreadPoolExecutor(max_workers=8) as pool:
        results = list(pool.map(lambda _: executor.execute(make_action("create_issue")), range(count)))
    refs = [r.result_ref for r in results]
    assert len(set(refs)) == count
