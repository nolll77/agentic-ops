from pathlib import Path
import yaml
from .schema import Scenario

DATA = Path(__file__).parent / "data"

def load_all() -> list[Scenario]:
    scenarios = [Scenario.model_validate(yaml.safe_load(p.read_text()))
                 for p in sorted(DATA.glob("**/*.yaml"))]
    ids = [s.id for s in scenarios]
    dup = {i for i in ids if ids.count(i) > 1}
    if dup:
        raise ValueError(f"IDs de scénarios dupliqués: {dup}")
    return scenarios
