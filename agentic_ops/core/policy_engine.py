from __future__ import annotations
import hashlib, json, re
from pathlib import Path
from typing import Literal, Protocol, Any, Callable, Callable
import yaml
from pydantic import BaseModel, ConfigDict, Field, ValidationError, model_validator
from .facts import SEV, SystemFacts

class PolicyLoadError(Exception): ...

class _S(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

# ---------- catalogue ----------
class Blast(_S):
    mode: Literal["fixed", "target_replicas"]
    value: int = 0

class ActionSpec(_S):
    klass: Literal["ticket", "service_mutation", "model_mutation"] = Field(alias="class")
    mutating: bool
    reversible: bool
    blast: Blast
    target_pattern: str

class Catalog(_S):
    schema_version: Literal[1]
    actions: dict[str, ActionSpec]

# ---------- policy ----------
class Level(_S):
    effect: Literal["allow", "require_approval"]
    approvals: int = 0

class ActionPolicy(_S):
    level: Literal["L1", "L2", "L3"]
    blast_radius_max: int | None = None
    rate_limit: str | None = Field(None, pattern=r"^\d+/(hour|day)$")

class Rule(_S):
    id: str
    kind: Literal["upstream_masks_service", "risk_register_forbids"]
    applies_to_classes: list[Literal["ticket", "service_mutation", "model_mutation"]]
    min_severity: Literal["WARNING", "CRITICAL"] = "WARNING"
    description: str = ""

class PolicyFile(_S):
    schema_version: Literal[2]
    default_effect: Literal["deny"]
    levels: dict[Literal["L1", "L2", "L3"], Level]
    actions: dict[str, ActionPolicy]
    rules: list[Rule]

class PolicyBundle(_S):
    policy: PolicyFile
    catalog: Catalog
    forbidden_by_risk: dict[str, frozenset[str]]
    version: str

    @model_validator(mode="after")
    def _consistent(self):
        a, c = set(self.policy.actions), set(self.catalog.actions)
        if a != c:
            raise ValueError(f"policy/catalogue désalignés: seulement policy={a - c}, seulement catalogue={c - a}")
        return self

    @classmethod
    def load(cls, policy: Path, catalog: Path, risk_register: Path) -> "PolicyBundle":
        try:
            raws = [yaml.safe_load(p.read_text()) for p in (policy, catalog, risk_register)]
            pol, cat, risks = raws
            forb = {rid: frozenset(str(x).lower() for x in (e or {}).get("forbidden_actions", []))
                    for rid, e in risks.items() if isinstance(e, dict)}
            canon = json.dumps(raws, sort_keys=True, default=str).encode()
            return cls(policy=PolicyFile.model_validate(pol), catalog=Catalog.model_validate(cat),
                       forbidden_by_risk=forb, version=hashlib.sha256(canon).hexdigest()[:12])
        except (OSError, yaml.YAMLError, ValidationError, ValueError, AttributeError, TypeError) as e:
            raise PolicyLoadError(f"policy invalide, démarrage refusé: {e}") from e

# ---------- évaluation ----------
class TargetInfo(BaseModel):
    replicas: int = Field(default=1, ge=1)
    criticality: Literal["low", "high"] = "low"

class InventoryPort(Protocol):
    def describe(self, target: str) -> TargetInfo | None: ...

class ProposalView(BaseModel):
    action: str
    target: str
    risk_id: str
    declared_blast_radius: int | None = None
    declared_reversible: bool | None = None

class EvalContext(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    facts: SystemFacts
    inventory: Any
    recent_count: Any
    reserve_quota: Callable[..., bool] | None = None
    reservation_key: str = ""

class Verdict(BaseModel):
    effect: Literal["ALLOW", "REQUIRE_APPROVAL", "DENY"]
    approvals_required: int = 0
    rule_ids: list[str]
    reasons: list[str]
    policy_version: str
    inventory_version: str | None = None
    computed_blast_radius: int | None = None
    computed_reversible: bool | None = None
    declared_blast_radius: int | None = None

_WINDOW = {"hour": 3600, "day": 86400}

def _blast(spec: ActionSpec, info: TargetInfo) -> int:
    base = spec.blast.value if spec.blast.mode == "fixed" else info.replicas
    return base + (1 if info.criticality == "high" else 0)

def evaluate(b: PolicyBundle, p: ProposalView, ctx: EvalContext) -> Verdict:
    action = p.action.split(".")[-1].strip().lower()
    deny: list[tuple[str, str]] = []

    def out(effect, rules, reasons, approvals=0, blast=None, rev=None) -> Verdict:
        return Verdict(effect=effect, approvals_required=approvals, rule_ids=rules, reasons=reasons,
                       policy_version=b.version,
                       inventory_version=getattr(ctx.inventory, "version", None),
                       computed_blast_radius=blast, computed_reversible=rev,
                       declared_blast_radius=p.declared_blast_radius)

    spec = b.catalog.actions.get(action)
    if spec is None:
        return out("DENY", ["CAT-001"], [f"action inconnue du catalogue: {action!r}"])
    if not re.fullmatch(spec.target_pattern, p.target):
        return out("DENY", ["CAT-002"], [f"cible {p.target!r} hors du format autorisé pour {action}"])
    info = ctx.inventory.describe(p.target)
    if info is None:
        failure_reason = getattr(ctx.inventory, "failure_reason", None)
        reason = (
            failure_reason
            if failure_reason
            else f"cible {p.target!r} absente de l'inventaire"
        )
        return out("DENY", ["INV-001"], [reason])

    blast = _blast(spec, info)
    ap = b.policy.actions[action]
    if ap.blast_radius_max is not None and blast > ap.blast_radius_max:
        deny.append(("BLAST-001", f"blast_radius calculé {blast} > max {ap.blast_radius_max}"))

    for r in b.policy.rules:
        if spec.klass not in r.applies_to_classes:
            continue
        if r.kind == "upstream_masks_service":
            ls = ctx.facts.layer_severity
            up = max(ls.get("data_pipeline", 0), ls.get("feature_store", 0))
            if up >= SEV[r.min_severity] and up >= ls.get("infrastructure", 0):
                deny.append((r.id, "anomalie data/feature >= infra: cause probable en amont du service"))
        elif r.kind == "risk_register_forbids" and action in b.forbidden_by_risk.get(p.risk_id, frozenset()):
            deny.append((r.id, f"{action} interdit par le registre pour {p.risk_id}"))

    if deny:
        return out("DENY", [d[0] for d in deny], [d[1] for d in deny], blast=blast, rev=spec.reversible)

    if ap.rate_limit:
        n, per = ap.rate_limit.split("/")
        if ctx.reserve_quota is not None:
            reserved = ctx.reserve_quota(
                action, p.target, int(n), _WINDOW[per], ctx.reservation_key
            )
            if not reserved:
                return out(
                    "DENY", ["RATE-001"], [f"rate limit {ap.rate_limit} atteint"],
                    blast=blast, rev=spec.reversible,
                )
        elif ctx.recent_count(action, p.target, _WINDOW[per]) >= int(n):
            return out(
                "DENY", ["RATE-001"], [f"rate limit {ap.rate_limit} atteint"],
                blast=blast, rev=spec.reversible,
            )

    lvl = b.policy.levels[ap.level]
    if lvl.effect == "allow" and spec.mutating and not ctx.facts.complete:
        return out("REQUIRE_APPROVAL", ["FACTS-001"], ["observabilité indisponible: autonomie suspendue"],
                   approvals=1, blast=blast, rev=spec.reversible)
    if lvl.effect == "allow":
        return out("ALLOW", [], [], blast=blast, rev=spec.reversible)
    return out("REQUIRE_APPROVAL", [f"LEVEL-{ap.level}"], [f"niveau {ap.level}: {lvl.approvals} approbation(s)"],
               approvals=lvl.approvals, blast=blast, rev=spec.reversible)
