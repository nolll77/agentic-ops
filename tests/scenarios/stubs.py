from __future__ import annotations
import hashlib
from dataclasses import dataclass, field
from typing import Any
from .schema import LLMScript, TelemetryEvent
from . import adapter

class ScriptedLLM:
    def __init__(self, script: LLMScript):
        self._by_model = {"Diagnosis": script.diagnosis, "ActionIntent": script.proposal}

    def complete(self, *, system, user, response_model, temperature=0.0):
        raw = self._by_model.get(response_model.__name__)
        if raw is None:
            raise KeyError(f"ScriptedLLM: pas de réponse pour {response_model.__name__}")
        return response_model.model_validate(raw)

class BaselineLLM:
    def __init__(self, telemetry: list[TelemetryEvent]):
        self.telemetry = telemetry

    def _layer(self) -> str:
        anomalies = sorted((e for e in self.telemetry if e.severity != "INFO"), key=lambda e: e.t)
        if not anomalies:
            return "data_pipeline"
        first = anomalies[0]
        return "data_pipeline" if first.layer == "feature_store" else first.layer

    def complete(self, *, system, user, response_model, temperature=0.0):
        if response_model.__name__ == "Diagnosis":
            return response_model.model_validate(
                adapter.diagnosis_dict(self._layer(), "baseline: première anomalie"))
        if response_model.__name__ == "ActionIntent":
            return response_model.model_validate(adapter.proposal_dict("create_issue", "tracker"))
        raise KeyError(response_model.__name__)

class RecordingLLM:
    def __init__(self, inner):
        self.inner, self.calls = inner, []

    def complete(self, *, system, user, response_model, temperature=0.0):
        out = self.inner.complete(system=system, user=user,
                                  response_model=response_model, temperature=temperature)
        self.calls.append({"model": response_model.__name__,
                           "prompt_sha256": hashlib.sha256((system + user).encode()).hexdigest()[:16]})
        return out

@dataclass
class RecordingExecutor:
    executed: list[dict[str, Any]] = field(default_factory=list)

    def execute(self, proposal, registry=None) -> Any:
        self.executed.append({"action": str(getattr(proposal, "type", proposal)),
                              "target": str(getattr(proposal, "target", ""))})
        return adapter.success_result(proposal)

@dataclass
class RecordingNotifier:
    requests: list[Any] = field(default_factory=list)

    def request_approval(self, episode) -> None:
        self.requests.append(episode)

class FakeObservability:
    def __init__(self, telemetry: list[TelemetryEvent]):
        self.telemetry = telemetry

    def get_events(self, layer: str | None = None):
        return [e for e in self.telemetry if layer in (None, e.layer)]
        
    def get_signal(self, signal_id: str):
        from agentic_ops.core.contracts import Signal
        from datetime import datetime, timezone
        return Signal(signal_id=signal_id, risk_id="SCENARIO", source="datadog", environment="prod", observed_at=datetime.now(timezone.utc), payload={})


class FakeKnowledge:
    def __init__(self, docs: dict[str, str]): self.docs = docs
    def fetch(self, risk_id: str) -> str:
        return self.docs.get(risk_id, "")

class RecordingLLM:
    def __init__(self, inner): self.inner, self.calls, self.prompts = inner, [], []
    def complete(self, *, system, user, response_model, temperature=0.0):
        self.prompts.append({"system": system, "user": user, "model": response_model.__name__})
        out = self.inner.complete(system=system, user=user, response_model=response_model, temperature=temperature)
        self.calls.append({"model": response_model.__name__})
        return out
