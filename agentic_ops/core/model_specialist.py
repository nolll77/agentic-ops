"""
Model Specialist piloté par LLM via Instructor.
Diagnostique les dégradations de modèle (Concept Drift, baisse de perfs).
"""

from __future__ import annotations

import instructor
import litellm
from tenacity import retry, stop_after_attempt, wait_exponential
from agentic_ops.core.contracts import Diagnosis, Signal


class ModelSpecialist:
    name = "model_specialist_llm"

    def __init__(self, model_name: str = "gemini/gemini-1.5-pro-latest"):
        self.model_name = model_name
        self.client = instructor.from_litellm(litellm.completion)

    # [ALERTE MLOPS] P1: Résilience face aux pannes LLM (Retry Backoff)
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def diagnose(
        self, risk_id: str, signal: Signal, context_info: str = ""
    ) -> Diagnosis:
        prompt = f"""
        Tu es l'agent spécialiste Modèle (Machine Learning). Ta mission est de diagnostiquer le risque {risk_id}.

        Signal observé :
        - ID: {signal.signal_id}
        - Valeur: {signal.metadata.get('value', 'N/A')} (Seuil: {signal.metadata.get('threshold', 'N/A')})
        - Source: {signal.source}
        - Dimensions: {signal.metadata.get('dimensions', 'N/A')}

        Contexte supplémentaire :
        {context_info}

        Analyse ce signal, typiquement une chute de performance (ex: F1-Score) sous le seuil d'alerte.
        Génère un diagnostic formel détaillant tes trouvailles (findings) avec des références d'évidence.
        """

        diagnosis = self.client.chat.completions.create(
            model=self.model_name,
            response_model=Diagnosis,
            messages=[{"role": "user", "content": prompt}],
        )

        # S'assurer que le risk_id et l'agent sont corrects
        diagnosis.risk_id = risk_id
        diagnosis.agent = self.name
        return diagnosis
