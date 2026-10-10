import shutil
from pathlib import Path
import pytest
from datetime import datetime, timezone
from agentic_ops.core.facts import SystemFacts
from agentic_ops.core.policy_engine import PolicyBundle, TargetInfo, EvalContext, ProposalView

GOV = Path(__file__).resolve().parents[2] / "agentic_ops/governance"
NOW = datetime(2026, 1, 12, 9, 0, tzinfo=timezone.utc)

class Inv:
    def describe(self, t): return None if t == "ghost" else TargetInfo(replicas=1)

@pytest.fixture(scope="module")
def bundle():
    return PolicyBundle.load(GOV / "autonomy_policy.yaml", GOV / "action_catalog.yaml", GOV / "risk_register.yaml")

def facts(infra=0, data=0, feat=0, complete=True):
    return SystemFacts(as_of=NOW, window_s=1800, complete=complete,
                       layer_severity={"infrastructure": infra, "data_pipeline": data, "feature_store": feat})

def ctx(f, recent=0):
    return EvalContext(facts=f, inventory=Inv(), recent_count=lambda *a: recent)

def prop(action, target="baac-prediction-api", risk="ML-014", **kw):
    return ProposalView(action=action, target=target, risk_id=risk, **kw)
