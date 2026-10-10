from __future__ import annotations
from typing import Any, Literal
from pydantic import BaseModel, Field, model_validator

Mode = Literal["scripted", "baseline", "live"]
Layer = Literal["infrastructure", "data_pipeline", "feature_store", "ml_model"]
Severity = Literal["INFO", "WARNING", "CRITICAL"]

class TelemetryEvent(BaseModel):
    t: int                                   # secondes depuis t0
    layer: Layer
    event: str
    severity: Severity = "INFO"
    component: str = "unknown"
    metrics: dict[str, float] = Field(default_factory=dict)
    message: str = ""                        # texte libre NON FIABLE (vecteur d'injection)

class Trigger(BaseModel):
    t: int
    risk_id: str
    source: str = "datadog"
    environment: str = "prod"
    payload: dict[str, Any] = Field(default_factory=dict)

class LLMScript(BaseModel):
    diagnosis: dict[str, Any]
    proposal: dict[str, Any]

class GroundTruth(BaseModel):
    root_cause_layer: Layer

class Expected(BaseModel):
    expect_approval: bool | None = None
    forbidden_actions: list[str] = Field(default_factory=list)
    allowed_actions: list[str]               # seules actions qui peuvent être EXÉCUTÉES
    final_states: list[str]                  # états FSM acceptables

class Scenario(BaseModel):
    id: str
    title: str
    source: list[str] = Field(default_factory=list)   # traçabilité vers le registre SIM-xxx
    modes: list[Mode]
    trigger: Trigger
    knowledge: dict[str, str] = Field(default_factory=dict)
    telemetry: list[TelemetryEvent]
    llm_script: LLMScript | None = None
    ground_truth: GroundTruth
    expected: Expected
    xfail: str | None = None                 # ex: "P0-1: blast_radius auto-déclaré par le LLM"

    @model_validator(mode="after")
    def _check(self):
        if "scripted" in self.modes and self.llm_script is None:
            raise ValueError(f"{self.id}: mode scripted exige llm_script")
        f = {a.lower() for a in self.expected.forbidden_actions}
        a = {x.lower() for x in self.expected.allowed_actions}
        if f & a:
            raise ValueError(f"{self.id}: actions à la fois interdites et autorisées: {f & a}")
        return self
