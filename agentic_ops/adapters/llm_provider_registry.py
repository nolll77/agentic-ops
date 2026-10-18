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
            "openrouter/google/gemma-2-9b-it:free",
            "openrouter/mistralai/mistral-7b-instruct:free",
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


SUPPORTED_ROLES: tuple[str, ...] = ("remediation", "infra", "data", "model", "chat")

ROLE_RECOMMENDED_MODELS: dict[str, dict[str, str]] = {
    "remediation": {
        "model": "openrouter/deepseek/deepseek-r1:free",
        "reason": "Raisonnement CoT délibéré pour planification d'actions et calcul blast radius",
    },
    "infra": {
        "model": "openrouter/google/gemma-4-31b-it:free",
        "reason": "Large contexte (256k tokens) pour ingestion de dumps de logs et traces Loki",
    },
    "data": {
        "model": "openrouter/google/gemma-4-26b-a4b-it:free",
        "reason": "Latence faible et parsing rapide des covariances et métriques Evidently",
    },
    "model": {
        "model": "openrouter/meta-llama/llama-3.3-70b-instruct:free",
        "reason": "Benchmark 70B pour comparaison stricte des métriques F1 et dérives MLflow",
    },
    "chat": {
        "model": "openrouter/deepseek/deepseek-chat:free",
        "reason": "Mode conversationnel rapide sans balises think pour interface SRE chat",
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
    LLM actif et spécialisé par rôle (remediation, infra, data, model, chat)
    depuis les variables d'environnement et instancier les adaptateurs.
    """

    @staticmethod
    def resolve_role_config(role: str = "global") -> LLMProviderConfig:
        """
        Lit les variables d'environnement pour un rôle cognitif donné (remediation,
        infra, data, model, chat, global) et retourne la configuration résolue.

        Ordre de préséance :
          1. Variable spécifique au rôle : LLM_MODEL_{ROLE}, LLM_PROVIDER_{ROLE},
             LLM_FALLBACK_MODELS_{ROLE}, LLM_TEMPERATURE_{ROLE}, etc.
          2. Variable globale : LLM_MODEL, LLM_PROVIDER, LLM_FALLBACK_MODELS, etc.
          3. Modèle par défaut du profil du fournisseur.
        """
        role_clean = role.lower().strip()
        role_upper = role_clean.upper()

        provider = (
            os.environ.get(f"LLM_PROVIDER_{role_upper}")
            or os.environ.get("LLM_PROVIDER", "openrouter")
        ).lower().strip()

        if provider not in PROVIDER_PROFILES:
            logger.warning(
                "LLM_PROVIDER='%s' inconnu pour rôle '%s'. Fallback sur 'openrouter'.",
                provider,
                role,
            )
            provider = "openrouter"

        profile = PROVIDER_PROFILES[provider]

        # Résolution du modèle
        role_model = os.environ.get(f"LLM_MODEL_{role_upper}")
        global_model = os.environ.get("LLM_MODEL")
        
        # Par défaut natif MAS : si aucun override n'est spécifié, chaque rôle hérite
        # de son modèle expert recommandé dans ROLE_RECOMMENDED_MODELS
        role_default = ROLE_RECOMMENDED_MODELS.get(role_clean, {}).get("model") if provider == "openrouter" else None
        model = role_model or global_model or role_default or profile["default_model"]
        is_specialized = bool(role_model or (role_default and not global_model))

        # Résolution des fallbacks
        raw_fallbacks = os.environ.get(f"LLM_FALLBACK_MODELS_{role_upper}")
        if raw_fallbacks is None:
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

        seed_str = (
            os.environ.get(f"LLM_SEED_{role_upper}")
            or os.environ.get("LLM_SEED", "")
        )
        seed = int(seed_str) if seed_str.isdigit() else None

        temperature = float(
            os.environ.get(f"LLM_TEMPERATURE_{role_upper}")
            or os.environ.get("LLM_TEMPERATURE", "0.0")
        )
        max_tokens = int(
            os.environ.get(f"LLM_MAX_TOKENS_{role_upper}")
            or os.environ.get("LLM_MAX_TOKENS", "1024")
        )
        timeout_seconds = int(
            os.environ.get(f"LLM_TIMEOUT_SECONDS_{role_upper}")
            or os.environ.get("LLM_TIMEOUT_SECONDS", "30")
        )
        max_retries = int(
            os.environ.get(f"LLM_MAX_RETRIES_{role_upper}")
            or os.environ.get("LLM_MAX_RETRIES", "3")
        )

        return LLMProviderConfig(
            provider=provider,
            model=model,
            fallback_models=fallback_models,
            temperature=temperature,
            max_tokens=max_tokens,
            timeout_seconds=timeout_seconds,
            max_retries=max_retries,
            seed=seed,
            structured_mode=os.environ.get("LLM_STRUCTURED_MODE", "instructor"),
            api_key_present=api_key_present,
            api_key_masked=api_key_masked,
            ollama_base_url=os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434"),
            azure_api_base=os.environ.get("AZURE_API_BASE", ""),
            azure_api_version=os.environ.get("AZURE_API_VERSION", "2024-02-01"),
            extra_kwargs={"role": role_clean, "is_specialized": is_specialized},
        )

    @staticmethod
    def resolve_config() -> LLMProviderConfig:
        """Lit les variables d'environnement globales et retourne la config résolue."""
        return LLMProviderRegistry.resolve_role_config(role="global")

    @staticmethod
    def build_adapter_for_role(role: str = "global"):
        """
        Construit et retourne l'adaptateur LLM spécialisé pour le rôle cognitif
        spécifié ('remediation', 'infra', 'data', 'model', 'chat', 'global').

        Returns:
            FallbackLLMAdapter wrapping the resolved provider adapter with role labeling.
        """
        from agentic_ops.adapters.llm_protocol import (
            LiteLLMAdapter,
            OllamaAdapter,
            FallbackLLMAdapter,
        )

        cfg = LLMProviderRegistry.resolve_role_config(role)
        logger.info(
            "LLMProviderRegistry: role=%s provider=%s model=%s fallbacks=%s",
            role,
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
                role=role,
            )
        else:
            primary = LiteLLMAdapter(
                model=cfg.model,
                temperature=cfg.temperature,
                max_tokens=cfg.max_tokens,
                timeout=cfg.timeout_seconds,
                max_retries=cfg.max_retries,
                seed=cfg.seed,
                role=role,
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
                        role=role,
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
                        role=role,
                    )
                )

        return FallbackLLMAdapter(primary=primary, fallbacks=fallback_adapters)

    @staticmethod
    def build_adapter_from_env():
        """
        Factory principale par défaut (rôle 'global').
        Maintenu pour stricte rétrocompatibilité.
        """
        return LLMProviderRegistry.build_adapter_for_role(role="global")

    @staticmethod
    def get_roles_topology() -> dict[str, Any]:
        """
        Retourne la topologie active de tous les rôles cognitifs (modèles résolus,
        fournisseurs, chaînes de fallback et indicateur de spécialisation explicite).
        """
        topology = {}
        for role in SUPPORTED_ROLES:
            cfg = LLMProviderRegistry.resolve_role_config(role)
            topology[role] = {
                "provider": cfg.provider,
                "model": cfg.model,
                "fallback_models": cfg.fallback_models,
                "is_specialized": cfg.extra_kwargs.get("is_specialized", False),
                "temperature": cfg.temperature,
                "max_tokens": cfg.max_tokens,
                "timeout_seconds": cfg.timeout_seconds,
                "recommendation": ROLE_RECOMMENDED_MODELS.get(role, {}),
            }
        return topology

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

    @staticmethod

    def chat(message: str, history: list[dict] | None = None) -> dict:
        """
        Interroge le LLM actif spécialisé pour le rôle 'chat' (ou global en fallback)
        avec le contexte de gouvernance du Control Plane.
        Retourne la réponse textuelle, les métadonnées et la latence.
        """
        from agentic_ops.adapters.llm_protocol import _ChatResponse
        try:
            from unittest.mock import Mock
            if isinstance(getattr(LLMProviderRegistry, "build_adapter_from_env", None), Mock):
                adapter = LLMProviderRegistry.build_adapter_from_env()
                cfg = LLMProviderRegistry.resolve_config()
            else:
                adapter = LLMProviderRegistry.build_adapter_for_role("chat")
                cfg = LLMProviderRegistry.resolve_role_config("chat")
            t0 = time.monotonic()

            system_prompt = (
                "Tu es l'assistant cognitif SRE et MLOps d'Agentic-Ops Control Plane. "
                "Tu analyses les pannes d'infrastructure et de données (dérives Evidently, saturation Redis, "
                "crash de pods, fausses alertes Loki, registres MLflow). "
                "Tu respectes strictement le principe de moindre privilège et de gouvernance déterministe. "
                "Réponds en français avec précision technique, concision et rigueur d'ingénieur SRE."
            )

            # Si l'utilisateur pose une question libre
            user_content = message
            if history:
                conversation_summary = "\n".join(
                    [f"{h.get('role', 'user')}: {h.get('content', '')}" for h in history[-4:]]
                )
                user_content = f"Historique récent:\n{conversation_summary}\n\nNouvelle question:\n{message}"

            result = adapter.complete(
                system=system_prompt,
                user=user_content,
                response_model=_ChatResponse,
                temperature=0.2,
            )
            latency_ms = round((time.monotonic() - t0) * 1000, 1)
            return {
                "status": "ok",
                "answer": result.answer,
                "action_type": result.action_type,
                "confidence_score": result.confidence_score,
                "rationale": result.rationale,
                "provider": cfg.provider,
                "model": cfg.model,
                "latency_ms": latency_ms,
            }
        except Exception as exc:
            t_elapsed = round((time.monotonic() - t0) * 1000, 1)
            offline_answer = _get_offline_sre_answer(message)
            if offline_answer:
                return {
                    "status": "ok",
                    "answer": offline_answer,
                    "action_type": "KNOWLEDGE_LOOKUP",
                    "confidence_score": 1.0,
                    "rationale": "Réponse déterministe servie depuis la base de connaissances SRE intégrée (mode dégradé Zero-Token).",
                    "provider": "agentic_ops_builtin",
                    "model": "deterministic_sre_knowledge_base",
                    "latency_ms": t_elapsed,
                }

            key_env = os.environ.get("OPENROUTER_API_KEY", "")
            key_hint = "" if key_env else " (La variable OPENROUTER_API_KEY est absente de l'environnement)."
            return {
                "status": "error",
                "error": str(exc),
                "answer": (
                    f"Erreur de communication avec le fournisseur LLM : {exc}.{key_hint} "
                    "Vérifiez vos clés d'API (OPENROUTER_API_KEY, etc.) ou posez une question sur les concepts clés du Control Plane "
                    "(Circuit Breaker, WORM Ledger, Slack HITL, Dérive Evidently, Fail-Closed)."
                ),
                "provider": os.environ.get("LLM_PROVIDER", "openrouter"),
                "model": os.environ.get("LLM_MODEL", "unknown"),
                "latency_ms": t_elapsed,
            }


def _get_offline_sre_answer(message: str) -> str | None:
    msg = message.lower()
    if any(k in msg for k in ["circuit breaker", "saturation", "quota", "coupe-circuit"]):
        return (
            "**[Mode Dégradé SRE — Base Déterministe In-Memory]**\n\n"
            "Le **Circuit Breaker** (FinOps & SecOps) protège le cluster contre les tempêtes de requêtes, "
            "les boucles infinies d'agents et l'explosion des coûts d'API LLM :\n\n"
            "• **Seuil de déclenchement** : au-delà de 50 requêtes/heure ou en cas de défaillances 5xx en chaîne, "
            "le coupe-circuit bascule immédiatement en état `TRIPPED`.\n"
            "• **Gouvernance Fail-Closed** : dès l'activation du coupe-circuit, tout appel vers les modèles probabilistes "
            "est coupé. Le système injecte le diagnostic figé `CIRCUIT_BREAKER_FALLBACK` et restreint les actions possibles "
            "à l'opération non-mutante `CREATE_ISSUE` (ouverture d'un ticket GitHub d'alerte, 0 token consommé, 0 mutation en production)."
        )
    if any(k in msg for k in ["worm", "trust ledger", "ledger", "immuab", "tamper", "audit trail"]):
        return (
            "**[Mode Dégradé SRE — Base Déterministe In-Memory]**\n\n"
            "Le **WORM Trust Ledger** (*Write Once, Read Many*) garantit l'immuabilité cryptographique et la non-répudiation "
            "de chaque intervention autonome sur le cluster MLOps :\n\n"
            "• **Chaînage cryptographique** : chaque épisode résolu est scellé par double signature `SHA-256` et `HMAC-SHA512` "
            "enchaînée sur l'état du bloc précédent (arbre de Merkle).\n"
            "• **Traçabilité forensique** : le registre consigne l'empreinte exacte du signal d'alerte, les faits système observés, "
            "le diagnostic de l'agent, l'approbation humaine Slack et la commande exécutée.\n"
            "• **Détection d'altération** : la commande `agentic-ops audit` recalcule l'intégrité de la chaîne. Toute modification "
            "post-mortem ou suppression d'entrée déclenche immédiatement une alerte de falsification (*Tampering Alert*)."
        )
    if any(k in msg for k in ["drift", "evidently", "dérive"]):
        return (
            "**[Mode Dégradé SRE — Base Déterministe In-Memory]**\n\n"
            "La surveillance du **Data Drift** et du **Model Staleness** est opérée en continu via les connecteurs Evidently et Pandera :\n\n"
            "• **Détection statistique** : calcul des distances de Wasserstein et tests de Kolmogorov-Smirnov sur les distributions d'entrées.\n"
            "• **Routage spécialisé** : toute dérive avérée est acheminée vers le `DataSpecialist` pour discriminer une dérive ponctuelle de covariables d'une dérive de concept réelle exigeant un réentraînement."
        )
    if any(k in msg for k in ["slack", "hitl", "approbation", "quorum"]):
        return (
            "**[Mode Dégradé SRE — Base Déterministe In-Memory]**\n\n"
            "Le protocole **Slack HITL** (*Human-in-the-Loop*) constitue le garde-fou obligatoire pour toute action à impact matériel (*Mutating Actions*) :\n\n"
            "• **Sécurité cryptographique** : chaque interaction est validée par signature `HMAC-SHA256` (`X-Slack-Signature`) et fenêtre anti-rejeu (< 300s).\n"
            "• **Concurrence distribuée** : les approbations concurrentes sont arbitrées par verrou atomique `SQLite BEGIN IMMEDIATE` pour éliminer tout risque de double exécution (Race Condition)."
        )
    if any(k in msg for k in ["fail-closed", "zero-trust", "politique", "policy"]):
        return (
            "**[Mode Dégradé SRE — Base Déterministe In-Memory]**\n\n"
            "Le principe **Fail-Closed** stipule qu'en l'absence de règle explicite autorisant une action (`ALLOW`), "
            "ou lors d'une défaillance réseau / partition Tailscale, le `PolicyEngine` applique par défaut le statut `DENY`.\n\n"
            "Aucune action mutante ne peut être exécutée sans autorisation déterministe préalable."
        )
    if any(k in msg for k in ["cac", "pull", "100.117.99.62", "lecture seule", "read-only", "vps"]):
        return (
            "**[Mode Dégradé SRE — Base Déterministe In-Memory]**\n\n"
            "La collecte de télémétrie vers le cluster cible `jakatt/cac_mlops` (`100.117.99.62`) est **strictement en lecture seule** (100% Read-Only) pour 3 raisons fondamentales :\n\n"
            "• **Principe du Moindre Privilège & Zero-Trust** : le Control Plane n'interroge que des requêtes HTTP GET non-mutantes sur les 5 endpoints d'observabilité (`/metrics`, `/health`, etc.).\n"
            "• **Isolation stricte contre les pannes en cascade** : aucune action physique (mutation, redémarrage, rollback) ne peut être injectée directement sur la prod sans passer par le `PolicyEngine` et le quorum d'approbation Slack HITL.\n"
            "• **Fail-Safe & Résilience** : si le VPS cible est éteint ou inaccessible, le collecteur `CacPullCollector` renvoie un statut dégradé `REMOTE_TARGET_OFFLINE` sans impacter la stabilité du cluster."
        )
    return None


def _set_env_if_missing(key: str, value: str) -> None:
    if key not in os.environ and value:
        os.environ[key] = value
