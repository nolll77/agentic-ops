"""
Orchestrator : câble Signal -> Specialist -> Diagnosis -> ActionProposal ->
PolicyEngine -> (Executor | Human Gate | Deny), avec State Machine et
Evidence Store systématiques. Zéro import de provider concret.
"""

from __future__ import annotations

from agentic_ops.core.contracts import (
    ActionProposal,
    ActionType,
    Decision,
    Episode,
    ExecutionResult,
)
from agentic_ops.core.evidence import EvidenceStore
from agentic_ops.core.idempotency import compute_semantic_fingerprint, acquire_idempotency_lock
from agentic_ops.core.policy import PolicyEngine
from agentic_ops.core.state import StateMachine
from agentic_ops.runtime import executor as executor_module

from agentic_ops.adapters.protocol import ObservabilityAdapter
from agentic_ops.core.circuit_breaker import global_circuit_breaker
from agentic_ops.core.telemetry import CIRCUIT_BREAKER_STATUS
from agentic_ops.core.contracts import Diagnosis, Finding



class Orchestrator:
    def __init__(
        self,
        observability: ObservabilityAdapter,
        policy_engine: PolicyEngine,
        evidence_store: EvidenceStore,
        environment: str = "staging",
    ):
        self.observability = observability
        self.policy_engine = policy_engine
        self.evidence_store = evidence_store
        self.environment = environment

    def _get_specialist(self, risk_id: str):
        if "MODEL" in risk_id.upper():
            from agentic_ops.core.model_specialist import ModelSpecialist

            return ModelSpecialist()
        elif "INFRA" in risk_id.upper():
            from agentic_ops.core.infra_specialist import InfraSpecialist

            return InfraSpecialist()
        else:
            from agentic_ops.core.specialist import DataSpecialist

            return DataSpecialist()

    def run(
        self,
        risk_id: str,
        signal_id: str = "data_drift",
        forced_action: ActionType | None = None,
        detection_window: str = "2026-09-30",
    ) -> Episode:
        sm = StateMachine(initial="DETECTED")
        signal = self.observability.get_signal(signal_id)

        # Fix P0: Idempotence sémantique et Verrou Distribué Redis
        tenant = signal.metadata.get("tenant", "default") if signal.metadata else "default"
        service = signal.metadata.get("service", "unknown") if signal.metadata else "unknown"
        fingerprint = compute_semantic_fingerprint(tenant, self.environment, service, risk_id)
        
        if not acquire_idempotency_lock(fingerprint, ttl_seconds=3600):
            print(f"[IDEMPOTENCE] Rejet: Incident {fingerprint[:8]} est déjà pris en charge (Lock Redis).")
            # En prod, on retournerait un objet Episode pointant vers l'existant.
            # On simule un drop pur pour le proof of concept.
            return None
        
        dedup_key = fingerprint  # On garde la variable pour la compatibilité EvidenceStore

        episode_id = self.evidence_store.next_episode_id()
        specialist = self._get_specialist(risk_id)

        # INVESTIGATING
        sm.transition("INVESTIGATING")
        print(f"[{sm.current}] specialist = {specialist.name}")
        
        # SecOps / FinOps Circuit Breaker Check
        global_circuit_breaker.record_call()
        CIRCUIT_BREAKER_STATUS.set(1 if global_circuit_breaker.is_tripped() else 0)
        
        if global_circuit_breaker.is_tripped():
            diagnosis = Diagnosis(
                risk_id=risk_id,
                agent="CIRCUIT_BREAKER_FALLBACK",
                confidence=1.0,
                findings=[Finding(description="LLM Circuit Breaker activé. Mode dégradé.")]
            )
            forced_action = ActionType.CREATE_ISSUE
            print("[CIRCUIT BREAKER] Mode dégradé forcé : CREATE_ISSUE")
        else:
            # DIAGNOSED
            diagnosis = specialist.diagnose(risk_id, signal)
            
        sm.transition("DIAGNOSED")
        print(f"[{sm.current}] {diagnosis.findings[0].description}")

        # PLANNED
        if forced_action is not None:
            action_type = forced_action
            action = ActionProposal(
                type=action_type,
                risk_id=risk_id,
                requested_by=specialist.name,
                reversible=action_type
                in (
                    ActionType.CREATE_ISSUE,
                    ActionType.INVESTIGATE,
                    ActionType.PROPOSE_RETRAIN,
                ),
                blast_radius=2 if action_type == ActionType.CREATE_ISSUE else 0,
            )
        else:
            from agentic_ops.core.remediation_agent import RemediationAgent

            remediation_agent = RemediationAgent()
            action = remediation_agent.plan_action(diagnosis)

        sm.transition("PLANNED")
        print(f"[{sm.current}] action = {action.type.value}")

        # POLICY
        decision = self.policy_engine.evaluate(action)
        print(
            f"[POLICY] {decision.decision.value} "
            f"(règle: {decision.matched_rule}, raisons: {', '.join(decision.reason_codes)})"
        )

        execution: ExecutionResult | None = None
        human_approval_required = False

        if decision.decision == Decision.ALLOW:
            sm.transition("EXECUTING")
            execution = executor_module.execute(action)
            sm.transition("RESOLVED")
            print(f"[{sm.current}] {execution.details} (ref: {execution.result_ref})")

        elif decision.decision == Decision.REQUIRE_APPROVAL:
            sm.transition("AWAITING_APPROVAL")
            human_approval_required = True
            print(
                f"[{sm.current}] BLOQUÉ — approbation humaine requise, aucune exécution"
            )

        else:  # DENY
            sm.transition("DENIED")
            print("[DENIED] Refusé par la politique — aucune exécution")

        episode = Episode(
            episode_id=episode_id,
            dedup_key=dedup_key,
            timestamp_utc=signal.observed_at,
            state_trace=sm.trace,
            risk_id=risk_id,
            signal=signal,
            diagnosis=diagnosis,
            action_proposal=action,
            policy_evaluation=decision,
            human_approval_required=human_approval_required,
            execution=execution,
        )

        path = self.evidence_store.save(episode)
        print(f"[EVIDENCE] {path}")
        return episode
