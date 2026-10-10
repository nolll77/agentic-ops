import shutil, pytest
from agentic_ops.core.policy_engine import PolicyBundle, PolicyLoadError
from .conftest import GOV

def _copy(tmp_path):
    for n in ("autonomy_policy.yaml", "action_catalog.yaml", "risk_register.yaml"):
        shutil.copy(GOV / n, tmp_path / n)
    return tmp_path

def _load(d): return PolicyBundle.load(d/"autonomy_policy.yaml", d/"action_catalog.yaml", d/"risk_register.yaml")

def test_missing_file(tmp_path):
    d = _copy(tmp_path); (d/"autonomy_policy.yaml").unlink()
    with pytest.raises(PolicyLoadError): _load(d)

def test_invalid_yaml(tmp_path):
    d = _copy(tmp_path); (d/"autonomy_policy.yaml").write_text("a: [unclosed")
    with pytest.raises(PolicyLoadError): _load(d)

def test_unknown_key_rejected(tmp_path):
    d = _copy(tmp_path); p = d/"autonomy_policy.yaml"; p.write_text(p.read_text() + "\nrogue_key: 1\n")
    with pytest.raises(PolicyLoadError): _load(d)

def test_default_effect_must_be_deny(tmp_path):
    d = _copy(tmp_path); p = d/"autonomy_policy.yaml"; p.write_text(p.read_text().replace("default_effect: deny", "default_effect: allow"))
    with pytest.raises(PolicyLoadError): _load(d)

def test_catalog_action_without_policy_rejected(tmp_path):
    d = _copy(tmp_path); p = d/"autonomy_policy.yaml"
    p.write_text("\n".join(l for l in p.read_text().splitlines() if "scale_up:" not in l))
    with pytest.raises(PolicyLoadError): _load(d)

def test_schema_v1_rejected(tmp_path):
    d = _copy(tmp_path); p = d/"autonomy_policy.yaml"; p.write_text(p.read_text().replace("schema_version: 2", "schema_version: 1"))
    with pytest.raises(PolicyLoadError): _load(d)

def test_version_changes_with_content(tmp_path):
    d = _copy(tmp_path); v1 = _load(d).version
    p = d/"autonomy_policy.yaml"; p.write_text(p.read_text().replace("2/hour", "5/hour"))
    assert _load(d).version != v1
