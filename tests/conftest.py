import pytest, yaml
from pathlib import Path

# Load gaps
try:
    GAPS = yaml.safe_load((Path(__file__).parent / "known_gaps.yaml").read_text()) or {}
except FileNotFoundError:
    GAPS = {}
_used: set[str] = set()

def pytest_configure(config):
    config.addinivalue_line("markers", "gap(id): test attendu en échec tant que l'entrée existe dans known_gaps.yaml")

def pytest_collection_modifyitems(config, items):
    for it in items:
        m = it.get_closest_marker("gap")
        if not m:
            continue
        gid = m.args[0]
        _used.add(gid)
        if gid in GAPS:
            it.add_marker(pytest.mark.xfail(strict=True, reason=f"{GAPS[gid]['p0']}: {GAPS[gid]['why']}"))

def pytest_collection_finish(session):
    stale = set(GAPS) - _used
    # Wait, until we write all tests, let's just warn instead of failing
    if stale and not session.config.option.keyword:
        import warnings
        warnings.warn(f"known_gaps.yaml: entrées sans test: {sorted(stale)}")
