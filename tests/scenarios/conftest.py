import json
from collections import defaultdict
from pathlib import Path
import pytest

def pytest_addoption(parser):
    parser.addoption("--live-llm", action="store_true", help="exécute les scénarios en mode live")
    parser.addoption("--policy", default=None, help="autonomy_policy.yaml alternatif")

def pytest_configure(config):
    config._scenario_results = []

@pytest.fixture
def policy_path(request) -> Path:
    custom = request.config.getoption("--policy")
    return Path(custom) if custom else (
        Path(__file__).resolve().parents[2] / "agentic_ops/governance/autonomy_policy.yaml")

@pytest.fixture
def results_sink(request):
    return request.config._scenario_results

def pytest_terminal_summary(terminalreporter, config):
    res = config._scenario_results
    if not res:
        return
    out = Path("reports"); out.mkdir(exist_ok=True)
    (out / "scenarios.json").write_text(json.dumps([r.model_dump() for r in res], indent=2))
    by_mode = defaultdict(list)
    for r in res:
        by_mode[r.mode].append(r)
    tr = terminalreporter
    tr.section("scenario metrics")
    for mode, rs in by_mode.items():
        n = len(rs)
        tr.write_line(
            f"[{mode:8}] n={n}  diag_ok={sum(r.diagnosis_correct for r in rs)}/{n}  "
            f"forbidden_proposed={sum(r.forbidden_proposed for r in rs)}  "
            f"forbidden_executed={sum(bool(r.forbidden_executed) for r in rs)}  "
            f"avg_llm_calls={sum(r.llm_calls for r in rs)/n:.1f}")
    tr.write_line("")
    for r in res:
        slack_state = "Slack HITL (AWAITING_APPROVAL)" if r.approval_requested else ("Veto Amont (DENY)" if "DENY" in str(r.policy_decision) else "Autonomie L1 (ALLOW)")
        prod_state = "0 mutation prod" if not r.executed_actions else f"exécuté={r.executed_actions}"
        tr.write_line(
            f"[GUIDE:HOW_IT_PASSES] {r.scenario_id}-{r.mode:8} : Action IA='{r.proposed_action}' (interdite={r.forbidden_proposed}) "
            f"-> Policy={r.policy_decision} ({slack_state}) -> FSM='{r.final_state}' | {prod_state} | forbidden_executed={len(r.forbidden_executed)}"
        )

