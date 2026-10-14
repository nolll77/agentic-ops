"""
LLM Adapters
============
Définit le Protocol LLMPort (port hexagonal), LiteLLMAdapter (universel),
OllamaAdapter (local/Tailscale/Cloudflare), FallbackLLMAdapter (chaîne de
secours automatique), et _ProbeResponse (healthcheck).

Métriques Prometheus instrumentées :
  agentic_ops_llm_requests_total        (provider, model, status)
  agentic_ops_llm_latency_seconds       (provider, model)
  agentic_ops_llm_tokens_total          (provider, model, token_type)
"""

from __future__ import annotations

import logging
import os
import re
import time
from typing import Protocol, TypeVar

import httpx
from pydantic import BaseModel
from prometheus_client import Counter, Histogram
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

logger = logging.getLogger("LLMAdapter")

T = TypeVar("T", bound=BaseModel)


def _strip_think_tags(text: str) -> str:
    """
    Règle de l'Honnêteté Radicale : Les modèles de raisonnement pur (comme DeepSeek-R1)
    émettent des balises <think>...</think> contenant leur chaîne de pensée.
    Cette fonction élimine ces blocs pour isoler le JSON pur attendu par Pydantic.
    """
    if not text:
        return text
    # Enlève tout le bloc <think>...</think> (multiligne)
    cleaned = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
    # Enlève d'éventuels backticks markdown ```json ... ```
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned.strip(), flags=re.MULTILINE)
    cleaned = re.sub(r"\s*```$", "", cleaned.strip())
    return cleaned.strip()


# ---------------------------------------------------------------------------
# Prometheus metrics
# ---------------------------------------------------------------------------

LLM_REQUESTS = Counter(
    "agentic_ops_llm_requests_total",
    "Total LLM requests by role, provider, model and status",
    ["role", "provider", "model", "status"],
)

LLM_LATENCY = Histogram(
    "agentic_ops_llm_latency_seconds",
    "LLM request latency in seconds",
    ["role", "provider", "model"],
    buckets=[0.5, 1.0, 2.0, 5.0, 10.0, 20.0, 30.0, 60.0],
)

LLM_TOKENS = Counter(
    "agentic_ops_llm_tokens_total",
    "Total LLM tokens consumed by role, provider, model and token type",
    ["role", "provider", "model", "token_type"],
)


# ---------------------------------------------------------------------------
# Protocol
# ---------------------------------------------------------------------------

class LLMPort(Protocol):
    def complete(
        self,
        *,
        system: str,
        user: str,
        response_model: type[T],
        temperature: float = 0.0,
    ) -> T:
        ...


# ---------------------------------------------------------------------------
# Probe response model (minimal, used by /api/llm/probe)
# ---------------------------------------------------------------------------

class _ProbeResponse(BaseModel):
    answer: str


class _ChatResponse(BaseModel):
    answer: str
    action_type: str = "investigate"
    confidence_score: float = 0.95
    rationale: str = ""


# ---------------------------------------------------------------------------
# LiteLLMAdapter — universal adapter (OpenRouter, OpenAI, Gemini, Anthropic,
#                                     Azure, Mistral, HuggingFace, ...)
# ---------------------------------------------------------------------------

class LiteLLMAdapter:
    """
    Adaptateur LiteLLM universel avec support de Structured Output via
    Instructor, Prometheus metrics, et retry exponentiel.

    Args:
        model           : Modèle au format LiteLLM  (ex: "openrouter/deepseek/deepseek-r1:free")
        temperature     : Température de génération (0.0 = déterministe)
        max_tokens      : Limite de tokens de sortie
        timeout         : Timeout réseau par appel (secondes)
        max_retries     : Nombre de tentatives avant exception
        seed            : Graine pour la reproductibilité (si supporté par le modèle)
    """

    def __init__(
        self,
        model: str = "openrouter/deepseek/deepseek-r1:free",
        temperature: float = 0.0,
        max_tokens: int = 1024,
        timeout: int = 30,
        max_retries: int = 3,
        seed: int | None = None,
        role: str = "global",
    ):
        import instructor
        import litellm

        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.timeout = timeout
        self.max_retries = max_retries
        self.seed = seed
        self.role = role

        # Derive provider label for Prometheus (first segment before '/')
        self._provider_label = model.split("/")[0] if "/" in model else "unknown"
        # Safe model label (strip :free tag for readability)
        self._model_label = model.split(":")[0].split("/")[-1]

        litellm.request_timeout = timeout
        self._client = instructor.from_litellm(litellm.completion)

    def complete(
        self,
        *,
        system: str,
        user: str,
        response_model: type[T],
        temperature: float | None = None,
    ) -> T:
        return self._complete_with_metrics(
            system=system,
            user=user,
            response_model=response_model,
            temperature=temperature if temperature is not None else self.temperature,
        )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(Exception),
        reraise=True,
    )
    def _complete_with_metrics(
        self,
        *,
        system: str,
        user: str,
        response_model: type[T],
        temperature: float,
    ) -> T:
        t0 = time.monotonic()
        try:
            kwargs: dict = dict(
                model=self.model,
                response_model=response_model,
                temperature=temperature,
                max_tokens=self.max_tokens,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
            )
            if self.seed is not None:
                kwargs["seed"] = self.seed

            result = self._client.chat.completions.create(**kwargs)
            elapsed = time.monotonic() - t0
            LLM_REQUESTS.labels(
                role=self.role,
                provider=self._provider_label,
                model=self._model_label,
                status="success",
            ).inc()
            LLM_LATENCY.labels(
                role=self.role, provider=self._provider_label, model=self._model_label
            ).observe(elapsed)
            return result
        except Exception as exc:
            elapsed = time.monotonic() - t0
            LLM_REQUESTS.labels(
                role=self.role,
                provider=self._provider_label,
                model=self._model_label,
                status="error",
            ).inc()
            LLM_LATENCY.labels(
                role=self.role, provider=self._provider_label, model=self._model_label
            ).observe(elapsed)
            logger.warning(
                "LiteLLMAdapter error on model=%s: %s", self.model, exc
            )
            raise


# ---------------------------------------------------------------------------
# OllamaAdapter — appel direct httpx (local, Tailscale, Cloudflare, Vast.ai)
# ---------------------------------------------------------------------------

class OllamaAdapter:
    """
    Adaptateur Ollama léger via httpx.

    Fonctionne avec :
    - Ollama local                 : OLLAMA_BASE_URL=http://localhost:11434
    - Ollama via Tailscale         : OLLAMA_BASE_URL=http://100.X.X.X:11434
    - Ollama via Cloudflare Tunnel : OLLAMA_BASE_URL=https://ollama.mondomaine.com
    - Ollama sur Vast.ai / VPS     : OLLAMA_BASE_URL=http://IP_PUBLIQUE:11434

    Aucune clé API requise.
    """

    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        model: str = "llama3.2:3b",
        timeout: int = 60,
        role: str = "global",
    ):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout
        self.role = role
        self._provider_label = "ollama"
        self._model_label = model.split(":")[0]

    def complete(
        self,
        *,
        system: str,
        user: str,
        response_model: type[T],
        temperature: float = 0.0,
    ) -> T:
        import json

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "stream": False,
            "options": {"temperature": temperature},
            "format": "json",
        }
        t0 = time.monotonic()
        try:
            with httpx.Client(timeout=self.timeout) as client:
                resp = client.post(
                    f"{self.base_url}/api/chat",
                    json=payload,
                )
                resp.raise_for_status()
            data = resp.json()
            content = data.get("message", {}).get("content", "")
            # [Honnêteté Radicale / Modèles de Raisonnement R1]
            # Nettoyer les balises <think>...</think> avant parsing JSON
            content = _strip_think_tags(content)
            # Parse JSON and validate against response_model
            parsed = json.loads(content)
            result = response_model.model_validate(parsed)
            elapsed = time.monotonic() - t0
            LLM_REQUESTS.labels(
                role=self.role, provider="ollama", model=self._model_label, status="success"
            ).inc()
            LLM_LATENCY.labels(
                role=self.role, provider="ollama", model=self._model_label
            ).observe(elapsed)
            return result
        except Exception as exc:
            elapsed = time.monotonic() - t0
            LLM_REQUESTS.labels(
                role=self.role, provider="ollama", model=self._model_label, status="error"
            ).inc()
            LLM_LATENCY.labels(
                role=self.role, provider="ollama", model=self._model_label
            ).observe(elapsed)
            logger.warning("OllamaAdapter error on %s/%s: %s", self.base_url, self.model, exc)
            raise


# ---------------------------------------------------------------------------
# FallbackLLMAdapter — chaîne de secours automatique
# ---------------------------------------------------------------------------

class FallbackLLMAdapter:
    """
    Chaîne de secours : si le modèle primaire échoue (RateLimitError, timeout,
    erreur 5xx), tente automatiquement chaque modèle de la liste de fallback
    dans l'ordre jusqu'à obtenir une réponse valide.

    Prometheus : chaque tentative est instrumentée individuellement.
    """

    def __init__(
        self,
        primary: LiteLLMAdapter | OllamaAdapter,
        fallbacks: list[LiteLLMAdapter | OllamaAdapter] | None = None,
    ):
        self.primary = primary
        self.fallbacks = fallbacks or []

    def complete(
        self,
        *,
        system: str,
        user: str,
        response_model: type[T],
        temperature: float = 0.0,
    ) -> T:
        chain = [self.primary] + self.fallbacks
        last_exc: Exception | None = None
        for i, adapter in enumerate(chain):
            label = getattr(adapter, "model", "unknown")
            try:
                logger.debug("FallbackLLMAdapter: trying adapter %d (%s)", i, label)
                return adapter.complete(
                    system=system,
                    user=user,
                    response_model=response_model,
                    temperature=temperature,
                )
            except Exception as exc:
                last_exc = exc
                logger.warning(
                    "FallbackLLMAdapter: adapter %d (%s) failed: %s — trying next.",
                    i, label, exc,
                )
        raise RuntimeError(
            f"All {len(chain)} LLM adapters in the fallback chain failed. "
            f"Last error: {last_exc}"
        ) from last_exc
