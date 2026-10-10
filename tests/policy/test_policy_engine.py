import pytest
from hypothesis import given, strategies as st
from agentic_ops.core.policy_engine import evaluate
from .conftest import facts, ctx, prop

@pytest.mark.parametrize("action,f,effect,rule", [
    ("restart_pod", facts(infra=0, data=1, feat=1), "DENY", "R-001"),
    ("scale_up",    facts(infra=1, data=2),          "DENY", "R-001"),
    ("restart_pod", facts(infra=2, data=0),          "REQUIRE_APPROVAL", "LEVEL-L2"),
    ("create_issue", facts(infra=0, data=2),         "ALLOW", None),
    ("create_issue", facts(complete=False),          "ALLOW", None),
    ("restart_pod",  facts(infra=2, complete=False), "REQUIRE_APPROVAL", "LEVEL-L2"),
])
def test_table(bundle, action, f, effect, rule):
    v = evaluate(bundle, prop(action), ctx(f))
    assert v.effect == effect
    if rule: assert rule in v.rule_ids

def test_risk_register_forbids_retrain(bundle):
    v = evaluate(bundle, prop("propose_retrain", target="baac_severity_predictor", risk="DATA-042"), ctx(facts()))
    assert v.effect == "DENY" and "R-002" in v.rule_ids

def test_retrain_other_risk_needs_two_approvals(bundle):
    v = evaluate(bundle, prop("propose_retrain", target="baac_severity_predictor"), ctx(facts()))
    assert (v.effect, v.approvals_required) == ("REQUIRE_APPROVAL", 2)

@pytest.mark.parametrize("action", ["rollback_model", "open_breaker", "RESTART_POD; rm -rf /", ""])
def test_unknown_action_denied(bundle, action):
    assert evaluate(bundle, prop(action), ctx(facts())).effect == "DENY"

@pytest.mark.parametrize("target", ["ghost", "prod-db", "baac-x; scale 0", "../../etc", ""])
def test_bad_target_denied(bundle, target):
    assert evaluate(bundle, prop("restart_pod", target=target), ctx(facts(infra=2))).effect == "DENY"

def test_rate_limit(bundle):
    assert evaluate(bundle, prop("restart_pod"), ctx(facts(infra=2), recent=1)).rule_ids[0] == "RATE-001"

@given(br=st.one_of(st.none(), st.integers(-5, 10_000)), rev=st.one_of(st.none(), st.booleans()),
       infra=st.integers(0, 2), data=st.integers(0, 2), feat=st.integers(0, 2))
def test_declared_values_never_change_verdict(bundle, br, rev, infra, data, feat):
    f = facts(infra, data, feat)
    base = evaluate(bundle, prop("scale_up"), ctx(f))
    lied = evaluate(bundle, prop("scale_up", declared_blast_radius=br, declared_reversible=rev), ctx(f))
    assert (base.effect, base.rule_ids, base.computed_blast_radius) == (lied.effect, lied.rule_ids, lied.computed_blast_radius)

@given(infra=st.integers(0, 2), data=st.integers(1, 2), feat=st.integers(0, 2),
       action=st.sampled_from(["restart_pod", "scale_up", "propose_retrain"]))
def test_masked_service_action_never_executes(bundle, infra, data, feat, action):
    f = facts(infra, data, feat)
    up = max(data, feat)
    if up >= infra:
        tgt = "baac_severity_predictor" if action == "propose_retrain" else "baac-prediction-api"
        assert evaluate(bundle, prop(action, target=tgt), ctx(f)).effect == "DENY"
