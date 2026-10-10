from agentic_ops.core.telemetry import POLICY_DECISIONS
from agentic_ops.core.contracts import ActionProposal, Decision, DecisionEnum

class PolicyEngine:
    """Moteur déterministe d'évaluation des propositions LLM."""
    def evaluate(self, action: ActionProposal) -> Decision:
        # Implémentation simplifiée du policy engine
        if action.type.value in ["restart_pod", "scale_up", "rollback"]:
            POLICY_DECISIONS.labels(decision='REQUIRE_APPROVAL', action_type=action.type.value).inc()
        return Decision(decision=DecisionEnum.REQUIRE_APPROVAL, matched_rule="production_infra_changes", reason_codes=["needs_human"])
        elif action.type.value == "create_issue":
            POLICY_DECISIONS.labels(decision='ALLOW', action_type=action.type.value).inc()
            return Decision(decision=DecisionEnum.ALLOW, matched_rule="safe_communication", reason_codes=[])
        POLICY_DECISIONS.labels(decision='DENY', action_type=action.type.value).inc()
        return Decision(decision=DecisionEnum.DENY, matched_rule="default_deny", reason_codes=["unsupported_action"])
