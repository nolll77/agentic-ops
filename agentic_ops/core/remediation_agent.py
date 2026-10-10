"""
Remediation Agent piloté par LLM via Instructor.
Coordonne le plan d'action en se basant sur le diagnostic d'un spécialiste.
"""

from __future__ import annotations
from agentic_ops.core.prompt_guard import wrap_untrusted, UNTRUSTED_NOTICE



from agentic_ops.adapters.llm_protocol import LLMPort
from agentic_ops.core.contracts import ActionProposal, Diagnosis, ActionIntent


class RemediationAgent:
    name = "remediation_agent_llm"

    def __init__(self, llm: LLMPort):
        self.llm = llm

    # [ALERTE MLOPS] P1: Résilience face aux pannes LLM (Retry Backoff)
    
    def plan_action(self, diagnosis: Diagnosis) -> ActionIntent:
        prompt = f"""
        Tu es le 'Remediation Agent' (Coordinateur principal).
        Un agent spécialisé ({diagnosis.agent}) a émis le diagnostic suivant pour le risque '{diagnosis.risk_id}':

        Niveau de confiance: {diagnosis.confidence_score}
        Trouvailles:
        {chr(10).join([f'- {f.description}' for f in diagnosis.findings])}

        Ta mission est de proposer la meilleure action de remédiation parmi les ActionType disponibles.
        Si la confiance est basse ou les trouvailles bénignes, propose INVESTIGATE.
        Si le risque est élevé, choisis CREATE_ISSUE, PROPOSE_RETRAIN, ROLLBACK_PROD, etc., selon le cas.

        Génère l'ActionIntent Pydantic. Assure-toi de paramétrer correctement le blast_radius (0-5) et la réversibilité.
        """

        proposal = self.llm.complete(
            system="Tu es le Remediation Agent.",
            user=prompt,
            response_model=ActionIntent,
            temperature=0.0
        )

        # Override fields to maintain strict security chain constraints
        # Removed assignment to risk_id since ActionIntent doesn't have it

        return proposal
