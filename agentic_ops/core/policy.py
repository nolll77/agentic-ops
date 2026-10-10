from datetime import datetime, timedelta
from agentic_ops.core.evidence import EvidenceStore
import yaml
import os
from pathlib import Path
from agentic_ops.core.contracts import ActionProposal, Decision, DecisionEnum
from agentic_ops.core.telemetry import POLICY_DECISIONS

class PolicyEngine:
    """Moteur déterministe granulaire basé sur autonomy_policy.yaml."""
    
    def __init__(self, policy_path: str = "agentic_ops/governance/autonomy_policy.yaml"):
        self.policy_path = Path(policy_path)
        self.rules = self._load_policies()
        self.evidence_store = EvidenceStore('agentic_ops/evidence_store')
        
    def _load_policies(self) -> dict:
        if not self.policy_path.exists():
            # Fallback strict en cas d'absence de fichier (Secure by default)
            return {}
        with open(self.policy_path, "r") as f:
            data = yaml.safe_load(f)
            return data.get("rules", {})

    def evaluate(self, action: ActionProposal) -> Decision:
        action_name = action.type.value
        
        # 1. Action inconnue du manifeste
        if action_name not in self.rules:
            POLICY_DECISIONS.labels(decision="DENY", action_type=action_name).inc()
            return Decision(
                decision=DecisionEnum.DENY, 
                matched_rule="default_deny", 
                reason_codes=["action_not_in_policy"]
            )
            
        rule = self.rules[action_name]
        autonomy_level = rule.get("autonomy", "human_approval_required")
        
        # 2. Vérification des conditions granulaires (ex: blast radius)
        conditions = rule.get("conditions", {})
        if "blast_radius_max" in conditions:
            if action.blast_radius > conditions["blast_radius_max"]:
                POLICY_DECISIONS.labels(decision="REQUIRE_APPROVAL", action_type=action_name).inc()
                return Decision(
                    decision=DecisionEnum.REQUIRE_APPROVAL,
                    matched_rule=action_name,
                    reason_codes=["blast_radius_exceeded"]
                )
                
        if "rate_limit" in conditions:
            limit_str = conditions["rate_limit"]  # e.g., "1/hour"
            if limit_str.endswith("/hour"):
                try:
                    max_count = int(limit_str.split("/")[0])
                    # Check history in evidence store
                    cutoff = datetime.utcnow() - timedelta(hours=1)
                    recent_count = 0
                    for file_path in self.evidence_store.store_dir.glob("*.json"):
                        if file_path.name == "_index.json":
                            continue
                        try:
                            import json
                            with open(file_path, "r") as f:
                                ep = json.load(f)
                        if ep.get("action_proposal", {}).get("type") == action_name:
                            ep_time_str = ep.get("timestamp_utc", "")
                            try:
                                # handle various ISO formats
                                ep_time = datetime.fromisoformat(ep_time_str.replace('Z', '+00:00').split('+')[0])
                                if ep_time > cutoff and ep.get("policy_evaluation", {}).get("decision") == "ALLOW":
                                    recent_count += 1
                            except Exception:
                                pass
                    if recent_count >= max_count:
                        POLICY_DECISIONS.labels(decision="REQUIRE_APPROVAL", action_type=action_name).inc()
                        return Decision(
                            decision=DecisionEnum.REQUIRE_APPROVAL,
                            matched_rule=action_name,
                            reason_codes=["rate_limit_exceeded"]
                        )
                except ValueError:
                    pass

        # 3. Arbitrage selon le niveau d'autonomie
        if autonomy_level == "autonomous":
            POLICY_DECISIONS.labels(decision="ALLOW", action_type=action_name).inc()
            return Decision(decision=DecisionEnum.ALLOW, matched_rule=action_name, reason_codes=["autonomous_allowed"])
            
        elif autonomy_level == "human_approval_required":
            POLICY_DECISIONS.labels(decision="REQUIRE_APPROVAL", action_type=action_name).inc()
            return Decision(decision=DecisionEnum.REQUIRE_APPROVAL, matched_rule=action_name, reason_codes=["human_in_the_loop"])
            
        # 4. Catch-all sécurisé
        POLICY_DECISIONS.labels(decision="DENY", action_type=action_name).inc()
        return Decision(decision=DecisionEnum.DENY, matched_rule="strict_fallback", reason_codes=["unknown_autonomy_level"])
