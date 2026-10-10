"""
Infra Specialist piloté par LLM via Instructor.
Diagnostique les alertes liées au système, réseau et bases de données.
"""

from __future__ import annotations



from agentic_ops.adapters.llm_protocol import LLMPort
from agentic_ops.core.contracts import Diagnosis, Signal


class InfraSpecialist:
    name = "infra_specialist_llm"

    def __init__(self, llm: LLMPort):
        self.llm = llm

    # [ALERTE MLOPS] P1: Résilience face aux pannes LLM (Retry Backoff)
    
    def diagnose(
        self, risk_id: str, signal: Signal, context_info: str = ""
    ) -> Diagnosis:
        prompt = f"""
        Tu es l'agent spécialiste Infrastructure (SRE/DevOps). Ta mission est de diagnostiquer le risque {risk_id}.

        Signal observé :
        - ID: {signal.signal_id}
        - Valeur: {signal.metadata.get('value', 'N/A')} (Seuil: {signal.metadata.get('threshold', 'N/A')})
        - Source: {signal.source}
        - Dimensions: {signal.metadata.get('dimensions', 'N/A')}

        Contexte supplémentaire :
        {context_info}

        Analyse ce signal système (ex: saturation CPU, Ram, PostgreSQL connections).
        Génère un diagnostic formel détaillant tes trouvailles (findings) avec des références d'évidence.
        Si la valeur dépasse le seuil, il y a saturation.
        """

        diagnosis = self.llm.complete(
            system="Tu es un spécialiste MLOps.",
            user=prompt,
            response_model=Diagnosis,
            temperature=0.0
        )

        # S'assurer que le risk_id et l'agent sont corrects
        diagnosis.risk_id = risk_id
        diagnosis.agent = self.name
        return diagnosis
