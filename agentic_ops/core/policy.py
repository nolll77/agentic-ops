import yaml
import os
from pathlib import Path
from datetime import datetime, timedelta
from agentic_ops.core.evidence import EvidenceStore
from agentic_ops.core.contracts import ActionProposal, Decision, DecisionEnum
from agentic_ops.core.telemetry import POLICY_DECISIONS, SHADOW_POLICY_DIVERGENCES

class PolicyEngine:
    """Moteur déterministe granulaire avec support du mode Shadow (A/B testing)."""
    
    def __init__(self, 
                 policy_path: str = "agentic_ops/governance/autonomy_policy.yaml",
                 shadow_path: str = "agentic_ops/governance/shadow_policy.yaml"):
        self.policy_path = Path(policy_path)
        self.shadow_path = Path(shadow_path)
        
        self.rules = self._load_policies(self.policy_path)
        self.shadow_rules = self._load_policies(self.shadow_path)
        
        self.evidence_store = EvidenceStore('agentic_ops/evidence_store')
        
    def _load_policies(self, path: Path) -> dict:
        if not path.exists():
            return {}
        with open(path, "r") as f:
            data = yaml.safe_load(f)
            return data.get("rules", {})

    def evaluate(self, action: ActionProposal) -> Decision:
        # 1. Évaluation Primaire (Celle qui sera appliquée)
        primary_decision = self._evaluate_single(action, self.rules, is_shadow=False)
        
        # 2. Évaluation Shadow (Optionnelle, pour Audit)
        if self.shadow_rules:
            shadow_decision = self._evaluate_single(action, self.shadow_rules, is_shadow=True)
            
            primary_decision.shadow_decision = shadow_decision.decision.value
            if primary_decision.decision.value != shadow_decision.decision.value:
                primary_decision.shadow_divergence = True
                SHADOW_POLICY_DIVERGENCES.labels(
                    action_type=action.type.value,
                    primary_decision=primary_decision.decision.value,
                    shadow_decision=shadow_decision.decision.value
                ).inc()
                print(f"👻 [SHADOW MODE] Divergence détectée sur {action.type.value}: Primary={primary_decision.decision.value} vs Shadow={shadow_decision.decision.value}")
                
        return primary_decision

    def _evaluate_single(self, action: ActionProposal, rules: dict, is_shadow: bool) -> Decision:
        action_name = action.type.value
        
        if action_name not in rules:
            if not is_shadow: POLICY_DECISIONS.labels(decision="DENY", action_type=action_name).inc()
            return Decision(decision=DecisionEnum.DENY, matched_rule="default_deny", reason_codes=["action_not_in_policy"])
            
        rule = rules[action_name]
        autonomy_level = rule.get("autonomy", "human_approval_required")
        conditions = rule.get("conditions", {})
        
        # Conditions de Blast Radius
        if "blast_radius_max" in conditions:
            if action.blast_radius > conditions["blast_radius_max"]:
                if not is_shadow: POLICY_DECISIONS.labels(decision="REQUIRE_APPROVAL", action_type=action_name).inc()
                return Decision(decision=DecisionEnum.REQUIRE_APPROVAL, matched_rule=action_name, reason_codes=["blast_radius_exceeded"])
                
        # Conditions de Rate Limiting
        if "rate_limit" in conditions:
            limit_str = conditions["rate_limit"]
            if limit_str.endswith("/hour"):
                try:
                    max_count = int(limit_str.split("/")[0])
                    cutoff = datetime.utcnow() - timedelta(hours=1)
                    recent_count = 0
                    for file_path in self.evidence_store.store_dir.glob("*.json"):
                        if file_path.name == "_index.json": continue
                        try:
                            import json
                            with open(file_path, "r") as f:
                                ep = json.load(f)
                            if ep.get("action_proposal", {}).get("type") == action_name:
                                ep_time_str = ep.get("timestamp_utc", "")
                                ep_time = datetime.fromisoformat(ep_time_str.replace('Z', '+00:00').split('+')[0])
                                if ep_time > cutoff and ep.get("policy_evaluation", {}).get("decision") == "ALLOW":
                                    recent_count += 1
                        except Exception:
                            pass
                            
                    if recent_count >= max_count:
                        if not is_shadow: POLICY_DECISIONS.labels(decision="REQUIRE_APPROVAL", action_type=action_name).inc()
                        return Decision(decision=DecisionEnum.REQUIRE_APPROVAL, matched_rule=action_name, reason_codes=["rate_limit_exceeded"])
                except ValueError:
                    pass

        # Arbitrage selon le niveau d'autonomie
        if autonomy_level == "autonomous":
            if not is_shadow: POLICY_DECISIONS.labels(decision="ALLOW", action_type=action_name).inc()
            return Decision(decision=DecisionEnum.ALLOW, matched_rule=action_name, reason_codes=["autonomous_allowed"])
            
        elif autonomy_level == "human_approval_required":
            if not is_shadow: POLICY_DECISIONS.labels(decision="REQUIRE_APPROVAL", action_type=action_name).inc()
            return Decision(decision=DecisionEnum.REQUIRE_APPROVAL, matched_rule=action_name, reason_codes=["human_in_the_loop"])
            
        if not is_shadow: POLICY_DECISIONS.labels(decision="DENY", action_type=action_name).inc()
        return Decision(decision=DecisionEnum.DENY, matched_rule="strict_fallback", reason_codes=["unknown_autonomy_level"])
