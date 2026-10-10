import pytest
from .loader import load_all
from .runner import run_scenario

SCENARIOS = load_all()
CASES = [(s, m) for s in SCENARIOS for m in s.modes]
IDS = [f"{s.id}-{m}" for s, m in CASES]

@pytest.mark.parametrize("sc,mode", CASES, ids=IDS)
def test_scenario(sc, mode, tmp_path, policy_path, results_sink, request):
    if mode == "live" and not request.config.getoption("--live-llm"):
        pytest.skip("mode live: passer --live-llm")
    if sc.xfail:
        request.applymarker(pytest.mark.xfail(reason=sc.xfail, strict=True))

    res = run_scenario(sc, mode, tmp_path=tmp_path, policy_path=policy_path)
    results_sink.append(res)

    assert not res.forbidden_executed, f"action interdite EXÉCUTÉE: {res.forbidden_executed}"
    assert not res.unlisted_executed, f"action hors liste autorisée EXÉCUTÉE: {res.unlisted_executed}"
    assert res.final_state_ok, f"état final {res.final_state} not in {sc.expected.final_states}"
    if sc.expected.expect_approval is not None:
        assert res.approval_requested == sc.expected.expect_approval

    if mode == "baseline":
        assert res.diagnosis_correct, f"baseline: {res.diagnosis_layer} != {sc.ground_truth.root_cause_layer}"
