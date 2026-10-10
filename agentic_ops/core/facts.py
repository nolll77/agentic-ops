from __future__ import annotations
from datetime import datetime, timedelta
from pydantic import BaseModel, ConfigDict

SEV = {"INFO": 0, "WARNING": 1, "CRITICAL": 2}

class Observation(BaseModel):
    model_config = ConfigDict(frozen=True)
    layer: str
    severity: str
    timestamp: datetime

class SystemFacts(BaseModel):
    model_config = ConfigDict(frozen=True)
    as_of: datetime
    window_s: int
    complete: bool
    layer_severity: dict[str, int]

def compute_facts(obs: list[Observation], *, as_of: datetime, window_s: int = 1800) -> SystemFacts:
    lo = as_of - timedelta(seconds=window_s)
    sev: dict[str, int] = {}
    for o in obs:
        if lo <= o.timestamp <= as_of:
            sev[o.layer] = max(sev.get(o.layer, 0), SEV.get(o.severity, 0))
    return SystemFacts(as_of=as_of, window_s=window_s, complete=True, layer_severity=sev)

def unknown_facts(as_of: datetime, window_s: int = 1800) -> SystemFacts:
    return SystemFacts(as_of=as_of, window_s=window_s, complete=False, layer_severity={})
