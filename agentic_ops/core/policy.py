import yaml
import os
from pathlib import Path
from datetime import datetime, timedelta
from agentic_ops.core.evidence import EvidenceStore
from agentic_ops.core.contracts import ActionProposal, Decision, DecisionEnum
from agentic_ops.core.distributed import RedisClient
from agentic_ops.core.governance_schemas import PolicyManifest
import logging
logger = logging.getLogger("PolicyEngine")
from agentic_ops.core.telemetry import POLICY_DECISIONS, SHADOW_POLICY_DIVERGENCES

class PolicyUnavailable(RuntimeError):
    pass

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
            logger.warning(f"Fichier de politique manquant: {path}")
            return {}
        try:
            with open(path, "r") as f:
                data = yaml.safe_load(f)
                
            # [ALERTE MLOPS] Validation Pydantic Stricte (Crash-Early)
            manifest = PolicyManifest.model_validate(data)
            return {k: v.model_dump() for k, v in manifest.rules.items()}
            
        except Exception as e:
            logger.critical(f"🚨 ERREUR FATALE DE GOUVERNANCE: Le fichier {path} est invalide.")
            logger.critical(str(e))
            raise RuntimeError(f"Fail-Safe: Arrêt du Control Plane. Politique de sécurité corrompue ({path}).") from e

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
                
        # Conditions de Rate Limiting Atomique (Redis INCR) Fix P0 Audit
        if "rate_limit" in conditions:
            limit_str = conditions["rate_limit"]
            if limit_str.endswith("/hour"):
                try:
                    max_count = int(limit_str.split("/")[0])
                    redis = RedisClient.get_client()
                    
                    # Clé granulaire (idéalement enrichie avec namespace/cibles)
                    rl_key = f"ratelimit:{action_name}:global"
                    
                    if is_shadow:
                        pass # Le mode Shadow ne consomme pas le quota de production (P0)
                    else:
                        # Transaction atomique (INCR + EXPIRE) via pipeline (P1)
                        pipe = redis.pipeline()
                        pipe.incr(rl_key)
                        pipe.expire(rl_key, 3600, nx=True)
                        results = pipe.execute()
                        current = results[0]
                        
                        if current > max_count:
                            POLICY_DECISIONS.labels(decision="DENY", action_type=action_name).inc()
                            return Decision(decision=DecisionEnum.DENY, matched_rule=action_name, reason_codes=["rate_limit_exceeded_hard_cap"])
                except Exception as e:
                    logger.error(f"Erreur évaluation quota: {e}")
                    raise PolicyUnavailable("Rate-limit backend unavailable") from e

        # Arbitrage selon le niveau d'autonomie
        if autonomy_level == "autonomous":
            if not is_shadow: POLICY_DECISIONS.labels(decision="ALLOW", action_type=action_name).inc()
            return Decision(decision=DecisionEnum.ALLOW, matched_rule=action_name, reason_codes=["autonomous_allowed"])
            
        elif autonomy_level == "human_approval_required":
            if not is_shadow: POLICY_DECISIONS.labels(decision="REQUIRE_APPROVAL", action_type=action_name).inc()
            return Decision(decision=DecisionEnum.REQUIRE_APPROVAL, matched_rule=action_name, reason_codes=["human_in_the_loop"])
            
        if not is_shadow: POLICY_DECISIONS.labels(decision="DENY", action_type=action_name).inc()
        return Decision(decision=DecisionEnum.DENY, matched_rule="strict_fallback", reason_codes=["unknown_autonomy_level"])
