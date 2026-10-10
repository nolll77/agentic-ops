from pathlib import Path
from agentic_ops.core.contracts import Decision, DecisionEnum
from agentic_ops.core.facts import Observation, compute_facts, unknown_facts
from agentic_ops.core.policy_engine import PolicyBundle, evaluate, ProposalView, EvalContext, TargetInfo

class DummyInventory:
    def describe(self, target: str):
        return TargetInfo()

class DummyHistory:
    def count_recent(self, *args, **kwargs):
        return 0

class PolicyEngine:
    def __init__(self, bundle, shadow=None):
        self.bundle = bundle
        self.shadow = shadow

    @classmethod
    def from_yaml(cls, policy_path):
        p = Path(policy_path)
        g = p.parent
        main = PolicyBundle.load(p, g / "action_catalog.yaml", g / "risk_register.yaml")
        sp = g / "shadow_policy.yaml"
        shadow = PolicyBundle.load(sp, g / "action_catalog.yaml", g / "risk_register.yaml") if sp.exists() else None
        return cls(main, shadow)

    def decide(self, proposal, signal, episode, *, observability, inventory=None, history=None):
        if inventory is None: inventory = DummyInventory()
        if history is None: history = DummyHistory()
        try:
            obs = []
            for e in observability.get_events():
                ts = getattr(e, "timestamp", getattr(signal, "observed_at", None))
                obs.append(Observation(layer=e.layer, severity=e.severity, timestamp=ts))
            facts = compute_facts(obs, as_of=signal.observed_at)
        except Exception:
            facts = unknown_facts(signal.observed_at)

        view = ProposalView(action=str(proposal.type.value), target=proposal.target, risk_id=proposal.risk_id,
                            declared_blast_radius=proposal.declared_blast_radius,
                            declared_reversible=proposal.declared_reversible)
        ctx = EvalContext(facts=facts, inventory=inventory, recent_count=history.count_recent)
        verdict = evaluate(self.bundle, view, ctx)
        
        episode.policy_version = verdict.policy_version
        episode.facts = facts.model_dump(mode="json")
        proposal.blast_radius = verdict.computed_blast_radius
        proposal.reversible = verdict.computed_reversible

        if self.shadow:
            try:
                sv = evaluate(self.shadow, view, ctx)
                if sv.effect != verdict.effect:
                    episode.shadow_divergence = {"main": verdict.effect, "shadow": sv.effect,
                                                 "shadow_version": sv.policy_version, "rules": sv.rule_ids}
            except Exception:
                pass
                
        return Decision(
            decision=DecisionEnum[verdict.effect],
            matched_rule=",".join(verdict.rule_ids) if verdict.rule_ids else "default_allow",
            reason_codes=verdict.reasons,
            approvals_required=verdict.approvals_required
        )
        
    def evaluate(self, action):
        return Decision(decision=DecisionEnum.ALLOW, matched_rule="legacy", reason_codes=[])
