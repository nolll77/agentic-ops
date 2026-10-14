"""
LLM Provider Registry
=====================
Registre centralisé des fournisseurs LLM. Lit les variables d'environnement
et instancie l'adaptateur correct (LiteLLM, Ollama, HuggingFace) pour
OpenRouter, Gemini, OpenAI, Anthropic, Azure, Mistral, HuggingFace, ou Ollama.

Usage:
    from agentic_ops.adapters.llm_provider_registry import LLMProviderRegistry
    adapter = LLMProviderRegistry.build_adapter_from_env()

Environment Variables:
    LLM_PROVIDER           : openrouter | openai | gemini | anthropic | azure
                             | mistral | huggingface | ollama
                             (default: openrouter)
    LLM_MODEL              : Model string in LiteLLM format
                             (default: openrouter/deepseek/deepseek-r1:free)
    LLM_FALLBACK_MODELS    : Comma-separated list of fallback model strings
    LLM_TEMPERATURE        : float, default 0.0
    LLM_MAX_TOKENS         : int, default 1024
    LLM_TIMEOUT_SECONDS    : int, default 30
    LLM_MAX_RETRIES        : int, default 3
    LLM_SEED               : int, default None (reproducibility if supported)
    LLM_STRUCTURED_MODE    : instructor | json_schema (default: instructor)

    Per-provider API keys:
    OPENROUTER_API_KEY, OPENAI_API_KEY, GOOGLE_API_KEY,
    ANTHROPIC_API_KEY, AZURE_API_KEY, AZURE_API_BASE, AZURE_API_VERSION,
    MISTRAL_API_KEY, HUGGINGFACE_API_KEY, OLLAMA_BASE_URL
"""

from __future__ import annotations

import logging
import os
import time
from dataclasses import dataclass, field
from typing import Any, Optional

logger = logging.getLogger("LLMProviderRegistry")

# ---------------------------------------------------------------------------
# Provider profiles — default model strings and required env vars
# ---------------------------------------------------------------------------

PROVIDER_PROFILES: dict[str, dict[str, Any]] = {
    "openrouter": {
        "description": "OpenRouter hub — 200+ models, :free tag = 0 EUR",
        "default_model": "openrouter/deepseek/deepseek-r1:free",
        "api_key_env": "OPENROUTER_API_KEY",
        "litellm_prefix": "openrouter/",
        "free_models": [
            "openrouter/deepseek/deepseek-r1:free",
            "openrouter/deepseek/deepseek-chat:free",
            "openrouter/meta-llama/llama-3.3-70b-instruct:free",
            "openrouter/google/gemini-2.0-flash-exp:free",
            "openrouter/mistralai/mistral-7b-instruct:free",
            "openrouter/qwen/qwen-2.5-72b-instruct:free",
        ],
        "rate_limits": "20 req/min, 200 req/day per key (free tier)",
    },
    "gemini": {
        "description": "Google Gemini via LiteLLM",
        "default_model": "gemini/gemini-1.5-pro-latest",
        "api_key_env": "GOOGLE_API_KEY",
        "litellm_prefix": "gemini/",
        "free_models": ["gemini/gemini-1.5-flash-latest"],
        "rate_limits": "60 req/min on free tier",
    },
    "openai": {
        "description": "OpenAI GPT-4o, GPT-4o-mini",
        "default_model": "gpt-4o-mini",
        "api_key_env": "OPENAI_API_KEY",
        "litellm_prefix": "",
        "free_models": [],
        "rate_limits": "Paid only",
    },
    "anthropic": {
        "description": "Anthropic Claude 3.5 family",
        "default_model": "claude-3-5-haiku-20241022",
        "api_key_env": "ANTHROPIC_API_KEY",
        "litellm_prefix": "",
        "free_models": [],
        "rate_limits": "Paid only",
    },
    "azure": {
        "description": "Azure OpenAI — enterprise GPT-4o",
        "default_model": "azure/gpt-4o",
        "api_key_env": "AZURE_API_KEY",
        "litellm_prefix": "azure/",
        "free_models": [],
        "rate_limits": "Depends on Azure subscription",
    },
    "mistral": {
        "description": "Mistral AI — Mistral Large, Codestral",
        "default_model": "mistral/mistral-large-2411",
        "api_key_env": "MISTRAL_API_KEY",
        "litellm_prefix": "mistral/",
        "free_models": [],
        "rate_limits": "Paid only (cheap — 2 EUR/M tokens)",
    },
    "huggingface": {
        "description": "HuggingFace Inference API — serverless free tier",
        "default_model": "huggingface/mistralai/Mistral-7B-Instruct-v0.2",
        "api_key_env": "HUGGINGFACE_API_KEY",
        "litellm_prefix": "huggingface/",
        "free_models": [
            "huggingface/mistralai/Mistral-7B-Instruct-v0.2",
            "huggingface/meta-llama/Llama-3.1-8B-Instruct",
        ],
        "rate_limits": "~1000 req/month free, high latency (cold start 5-30s)",
    },
    "ollama": {
        "description": "Ollama local or Tailscale-routed — 0 EUR, requires machine on",
        "default_model": "ollama/llama3.2:3b",
        "api_key_env": None,
        "litellm_prefix": "ollama/",
        "free_models": ["ollama/llama3.2:3b", "ollama/mistral:7b", "ollama/phi3:mini"],
        "rate_limits": "Unlimited — constrained by your local GPU/CPU",
    },
}


@dataclass
class LLMProviderConfig:
    """Resolved configuration for the active LLM provider."""
    provider: str
    model: str
    fallback_models: list[str]
    temperature: float
    max_tokens: int
    timeout_seconds: int
    max_retries: int
    seed: Optional[int]
    structured_mode: str
    api_key_present: bool
    api_key_masked: str
    ollama_base_url: str
    azure_api_base: str
    azure_api_version: str
    extra_kwargs: dict = field(default_factory=dict)


class LLMProviderRegistry:
    """
    Registre centralisé. Point d'entrée unique pour résoudre le fournisseur
    LLM actif depuis les variables d'environnement et instancier l'adaptateur.
    """

    @staticmethod
    def resolve_config() -> LLMProviderConfig:
        """Lit les variables d'environnement et retourne la config résolue."""
        provider = os.environ.get("LLM_PROVIDER", "openrouter").lower().strip()
        if provider not in PROVIDER_PROFILES:
            logger.warning(
                "LLM_PROVIDER='%s' inconnu. Fallback sur 'openrouter'.", provider
            )
            provider = "openrouter"

        profile = PROVIDER_PROFILES[provider]
        model = os.environ.get("LLM_MODEL", profile["default_model"])

        raw_fallbacks = os.environ.get("LLM_FALLBACK_MODELS", "")
        fallback_models = [m.strip() for m in raw_fallbacks.split(",") if m.strip()]
        # Si aucun fallback déclaré et qu'on est sur OpenRouter, on ajoute les gratuits
        if not fallback_models and provider == "openrouter":
            fallback_models = [
                m for m in profile["free_models"] if m != model
            ]

        api_key_env = profile.get("api_key_env")
        api_key = os.environ.get(api_key_env, "") if api_key_env else ""
        api_key_present = bool(api_key)
        if api_key and len(api_key) > 8:
            api_key_masked = api_key[:6] + "***" + api_key[-3:]
        elif api_key:
            api_key_masked = "***"
        else:
            api_key_masked = "(absent)"

        seed_str = os.environ.get("LLM_SEED", "")
        seed = int(seed_str) if seed_str.isdigit() else None

        return LLMProviderConfig(
            provider=provider,
            model=model,
            fallback_models=fallback_models,
            temperature=float(os.environ.get("LLM_TEMPERATURE", "0.0")),
            max_tokens=int(os.environ.get("LLM_MAX_TOKENS", "1024")),
            timeout_seconds=int(os.environ.get("LLM_TIMEOUT_SECONDS", "30")),
            max_retries=int(os.environ.get("LLM_MAX_RETRIES", "3")),
            seed=seed,
            structured_mode=os.environ.get("LLM_STRUCTURED_MODE", "instructor"),
            api_key_present=api_key_present,
            api_key_masked=api_key_masked,
            ollama_base_url=os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434"),
            azure_api_base=os.environ.get("AZURE_API_BASE", ""),
            azure_api_version=os.environ.get("AZURE_API_VERSION", "2024-02-01"),
        )

    @staticmethod
    def build_adapter_from_env():
        """
        Factory principale. Construit et retourne l'adaptateur LLM approprié
        selon LLM_PROVIDER.

        Returns:
            FallbackLLMAdapter wrapping the resolved provider adapter.
        """
        from agentic_ops.adapters.llm_protocol import (
            LiteLLMAdapter,
            OllamaAdapter,
            FallbackLLMAdapter,
        )

        cfg = LLMProviderRegistry.resolve_config()
        logger.info(
            "LLMProviderRegistry: provider=%s model=%s fallbacks=%s",
            cfg.provider,
            cfg.model,
            cfg.fallback_models,
        )

        # Inject per-provider env vars that LiteLLM reads automatically
        if cfg.provider == "openrouter":
            _set_env_if_missing("OPENROUTER_API_KEY", os.environ.get("OPENROUTER_API_KEY", ""))
        elif cfg.provider == "azure":
            _set_env_if_missing("AZURE_API_KEY", os.environ.get("AZURE_API_KEY", ""))
            _set_env_if_missing("AZURE_API_BASE", cfg.azure_api_base)
            _set_env_if_missing("AZURE_API_VERSION", cfg.azure_api_version)

        # Ollama → dedicated lightweight adapter (no LiteLLM overhead)
        if cfg.provider == "ollama":
            primary = OllamaAdapter(
                base_url=cfg.ollama_base_url,
                model=cfg.model.replace("ollama/", ""),
                timeout=cfg.timeout_seconds,
            )
        else:
            primary = LiteLLMAdapter(
                model=cfg.model,
                temperature=cfg.temperature,
                max_tokens=cfg.max_tokens,
                timeout=cfg.timeout_seconds,
                max_retries=cfg.max_retries,
                seed=cfg.seed,
            )

        # Build fallback chain
        fallback_adapters = []
        for fb_model in cfg.fallback_models:
            if fb_model.startswith("ollama/"):
                fallback_adapters.append(
                    OllamaAdapter(
                        base_url=cfg.ollama_base_url,
                        model=fb_model.replace("ollama/", ""),
                        timeout=cfg.timeout_seconds,
                    )
                )
            else:
                fallback_adapters.append(
                    LiteLLMAdapter(
                        model=fb_model,
                        temperature=cfg.temperature,
                        max_tokens=cfg.max_tokens,
                        timeout=cfg.timeout_seconds,
                        max_retries=1,
                        seed=cfg.seed,
                    )
                )

        return FallbackLLMAdapter(primary=primary, fallbacks=fallback_adapters)

    @staticmethod
    def list_providers() -> list[dict]:
        """Retourne le catalogue de tous les fournisseurs supportés."""
        cfg = LLMProviderRegistry.resolve_config()
        result = []
        for name, profile in PROVIDER_PROFILES.items():
            api_key_env = profile.get("api_key_env")
            key_present = bool(os.environ.get(api_key_env, "")) if api_key_env else True
            result.append({
                "provider": name,
                "description": profile["description"],
                "default_model": profile["default_model"],
                "active": name == cfg.provider,
                "api_key_configured": key_present,
                "free_models": profile["free_models"],
                "rate_limits": profile["rate_limits"],
            })
        return result

    @staticmethod
    def probe(timeout: float = 10.0) -> dict:
        """
        Sonde le LLM actif avec un prompt minimal et mesure la latence.
        Retourne le résultat et la latence en millisecondes.
        """
        from agentic_ops.adapters.llm_protocol import _ProbeResponse
        try:
            adapter = LLMProviderRegistry.build_adapter_from_env()
            cfg = LLMProviderRegistry.resolve_config()
            t0 = time.monotonic()
            result = adapter.complete(
                system="You are a health-check bot.",
                user="Respond with exactly: ok",
                response_model=_ProbeResponse,
                temperature=0.0,
            )
            latency_ms = round((time.monotonic() - t0) * 1000, 1)
            return {
                "status": "ok",
                "provider": cfg.provider,
                "model": cfg.model,
                "response": result.answer,
                "latency_ms": latency_ms,
            }
        except Exception as exc:
            return {
                "status": "error",
                "error": str(exc),
                "provider": os.environ.get("LLM_PROVIDER", "openrouter"),
                "model": os.environ.get("LLM_MODEL", "unknown"),
                "latency_ms": None,
            }


def _set_env_if_missing(key: str, value: str) -> None:
    if key not in os.environ and value:
        os.environ[key] = value
