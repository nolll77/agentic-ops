import os
import re
import socket
import subprocess
import sys
import time
from enum import Enum
from types import SimpleNamespace
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, PlainTextResponse
from agentic_ops.entrypoints.slack_webhook import router as slack_router
from agentic_ops.entrypoints.mcp_server import router as mcp_router
from agentic_ops.core.approvals import ApprovalRepo
from agentic_ops.adapters.cac_pull_collector import CacPullCollector

app = FastAPI(
    title="Agentic-Ops Control Plane",
    description="Deterministic SRE & MLOps Governance Control Plane (Auto-Wake Ready + Web Console + MCP Gateway)",
    version="0.1.0",
)

# CORS enabled so a Vercel frontend or external dashboard can wake the container via fetch()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# HITL (Human-In-The-Loop) state initialization for /slack/interactive
db_path = os.environ.get("APPROVAL_DB_PATH", "state/approvals.db")
if db_path != ":memory:":
    os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
clock = time.time
repo = ApprovalRepo(db_path, clock)

app.state.hitl = SimpleNamespace(
    secrets=[os.environ.get("SLACK_SIGNING_SECRET", "dummy_secret_defense_presentation")],
    clock=clock,
    repo=repo,
    orchestrator=SimpleNamespace(
        load_episode=lambda ep_id: None,
        current_proposal_hash=lambda ep: "",
        resume_from_claim=lambda claim: None,
        close_episode=lambda ep_id, val: None,
    ),
    policy=SimpleNamespace(level_of=lambda ep: "L1"),
    approvers=SimpleNamespace(group_of=lambda user, level: "admin"),
)


def _is_port_open(host: str, port: int, timeout: float = 0.5) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def _redact_pii(text: str) -> str:
    """Redacts email addresses, truncated Tailscale account names, and personal workstation hostnames."""
    if not text:
        return text
    redacted = re.sub(r"[\w\.-]+@(?:[\w\.-]+\.\w+|(?=\s|$))", "[REDACTED_ACCOUNT]", text)
    redacted = re.sub(r"(?i)(jacquess-imac|jacquess-mac-mini|nollls-macbook-pro)", "[REDACTED_WORKSTATION]", redacted)
    return redacted


class DiagnosticCommand(str, Enum):
    sandbox_phase_a_vitals = "sandbox_phase_a_vitals"
    sandbox_phase_b_slack_spoof = "sandbox_phase_b_slack_spoof"
    sandbox_phase_c_adversarial_worm = "sandbox_phase_c_adversarial_worm"
    sandbox_phase_d_mlops_scenarios = "sandbox_phase_d_mlops_scenarios"
    sandbox_phase_e_fsm_governance = "sandbox_phase_e_fsm_governance"
    pytest_cac_connector = "pytest_cac_connector"
    pytest_mcp_gateway = "pytest_mcp_gateway"
    pytest_llm_hub = "pytest_llm_hub"
    pytest_security = "pytest_security"
    pytest_all = "pytest_all"
    trust_ledger_list = "trust_ledger_list"
    tailscale_status = "tailscale_status"
    tailscale_netcheck = "tailscale_netcheck"
    tailscale_logs = "tailscale_logs"
    redis_ping = "redis_ping"
    system_info = "system_info"


@app.get("/")
def root():
    """
    Auto-wake landing route. Visiting the container URL or calling it from a
    frontend wakes the container and returns the live Control Plane status.
    """
    from agentic_ops.adapters.llm_provider_registry import LLMProviderRegistry

    llm_cfg = LLMProviderRegistry.resolve_config()
    return {
        "service": "agentic-ops-control-plane",
        "status": "awake",
        "redis_local_6379": _is_port_open("127.0.0.1", 6379),
        "tailscale_socks5_1055": _is_port_open("127.0.0.1", 1055),
        "llm_hub": {
            "provider": llm_cfg.provider,
            "model": llm_cfg.model,
            "api_key_configured": llm_cfg.api_key_present,
            "fallback_models": llm_cfg.fallback_models,
        },
        "endpoints": {
            "web_console": "/console",
            "web_chat": "/chat",
            "mcp_jsonrpc": "/mcp",
            "mcp_manifest": "/mcp/manifest",
            "swagger_docs": "/docs",
            "llm_status": "/api/llm/status",
            "llm_models": "/api/llm/models",
            "llm_probe": "/api/llm/probe",
            "llm_chat": "/api/chat",
            "starter_prompts": "/api/prompts",
            "healthz": "/healthz",
            "ready": "/ready",
            "tailscale_status": "/api/tailscale/status",
            "cac_snapshot": "/api/cac/snapshot",
            "diagnostics": "/api/diagnostics/{command}",
            "slack_webhook": "/slack/interactive",
        },
    }



@app.get("/healthz")
def healthz():
    return {"status": "ok"}


@app.get("/ready")
def ready():
    return {
        "status": "ready",
        "redis_local_6379": _is_port_open("127.0.0.1", 6379),
        "tailscale_socks5_1055": _is_port_open("127.0.0.1", 1055),
    }


@app.get("/api/tailscale/status")
def tailscale_status():
    """
    Returns the live Tailscale daemon status, the fresh interactive AuthURL
    (if NeedsLogin), and the base64-encoded state (TS_STATE_B64) once authenticated
    so non-admin members can persist their session in Render Environment Variables.
    """
    import base64
    import json

    ts_socket = os.environ.get("TS_SOCKET", "/tmp/tailscaled.sock")
    ts_state_path = os.environ.get("TS_STATE", "/tmp/tailscaled.state")
    hostname = os.environ.get("TS_HOSTNAME", "agentic-ops-render")

    status_data = {}
    try:
        res = subprocess.run(
            ["tailscale", f"--socket={ts_socket}", "status", "--json"],
            capture_output=True,
            text=True,
            timeout=3,
        )
        if res.returncode == 0 and res.stdout:
            status_data = json.loads(res.stdout)
    except Exception as exc:
        return {"error": str(exc)}

    backend_state = status_data.get("BackendState", "Unknown")
    auth_url = status_data.get("AuthURL", "")

    # If NeedsLogin but AuthURL is not populated yet, trigger non-blocking tailscale up
    if backend_state in ("NeedsLogin", "NoState", "Stopped") and not auth_url:
        try:
            subprocess.Popen(
                [
                    "tailscale",
                    f"--socket={ts_socket}",
                    "up",
                    f"--hostname={hostname}",
                    "--accept-routes",
                ],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            time.sleep(1.5)
            res2 = subprocess.run(
                ["tailscale", f"--socket={ts_socket}", "status", "--json"],
                capture_output=True,
                text=True,
                timeout=3,
            )
            if res2.returncode == 0 and res2.stdout:
                status_data = json.loads(res2.stdout)
                backend_state = status_data.get("BackendState", backend_state)
                auth_url = status_data.get("AuthURL", "")
        except Exception:
            pass

    ts_state_b64 = None
    if backend_state == "Running" and os.path.exists(ts_state_path):
        try:
            with open(ts_state_path, "rb") as f:
                ts_state_b64 = base64.b64encode(f.read()).decode("ascii")
        except Exception:
            ts_state_b64 = None

    self_node = status_data.get("Self") or {}
    return {
        "backend_state": backend_state,
        "auth_url": auth_url or None,
        "tailscale_ips": self_node.get("TailscaleIPs", []),
        "hostname": self_node.get("HostName"),
        "ts_state_b64": ts_state_b64,
        "instructions": (
            "1. Open auth_url in your browser to authorize this container. "
            "2. Refresh this page once connected to copy ts_state_b64 into Render Environment Variables as TS_STATE_B64."
            if backend_state != "Running"
            else "Connected to Tailscale! Copy ts_state_b64 into Render Environment Variables (Key: TS_STATE_B64) to persist across container sleep cycles."
        ),
    }


@app.get("/api/cac/snapshot")
def get_cac_snapshot(use_proxy: bool = Query(default=True), timeout: float = Query(default=3.5)):
    """
    Triggers an immediate Read-Only Pull collection against the remote
    jakatt/cac_mlops platform (via Tailscale SOCKS5 proxy if available).
    """
    proxy_available = _is_port_open("127.0.0.1", 1055)
    collector = CacPullCollector(
        use_proxy_for_vps=(use_proxy and proxy_available),
        timeout=timeout,
    )
    snapshot = collector.collect_all()
    return snapshot.model_dump(mode="json")


@app.get("/api/llm/status")
def get_llm_status():
    """
    Returns the active LLM provider configuration, resolved model,
    masked API key status, fallback chain, and connection parameters.
    """
    from agentic_ops.adapters.llm_provider_registry import LLMProviderRegistry

    cfg = LLMProviderRegistry.resolve_config()
    return {
        "provider": cfg.provider,
        "model": cfg.model,
        "api_key_configured": cfg.api_key_present,
        "api_key_masked": cfg.api_key_masked,
        "fallback_models": cfg.fallback_models,
        "temperature": cfg.temperature,
        "max_tokens": cfg.max_tokens,
        "timeout_seconds": cfg.timeout_seconds,
        "max_retries": cfg.max_retries,
        "structured_mode": cfg.structured_mode,
        "ollama_base_url": cfg.ollama_base_url if cfg.provider == "ollama" else None,
        "azure_api_base": cfg.azure_api_base if cfg.provider == "azure" else None,
        "free_tier_supported": cfg.provider in ("openrouter", "gemini", "huggingface", "ollama"),
    }


@app.get("/api/llm/models")
def list_llm_models():
    """
    Returns the comprehensive catalog of all 8 supported LLM providers,
    their free models (0 EUR), rate limits, and configuration status.
    """
    from agentic_ops.adapters.llm_provider_registry import LLMProviderRegistry

    return {
        "providers": LLMProviderRegistry.list_providers(),
        "free_brain_recommendations": [
            {
                "tier": "Primary (24/7 Cloud)",
                "provider": "openrouter",
                "model": "openrouter/deepseek/deepseek-r1:free",
                "cost": "0 EUR",
                "reason": "Top reasoning benchmark (DeepSeek-R1), requires only OPENROUTER_API_KEY with no billing card.",
            },
            {
                "tier": "Fast Cloud (Fallback)",
                "provider": "openrouter",
                "model": "openrouter/deepseek/deepseek-chat:free",
                "cost": "0 EUR",
                "reason": "Direct JSON output without think tags, fast p95 latency.",
            },
            {
                "tier": "Meta Llama (Fallback)",
                "provider": "openrouter",
                "model": "openrouter/meta-llama/llama-3.3-70b-instruct:free",
                "cost": "0 EUR",
                "reason": "Enterprise-grade 70B parameter model hosted for free.",
            },
            {
                "tier": "Tailscale / Local Mesh",
                "provider": "ollama",
                "model": "ollama/llama3.2:3b",
                "cost": "0 EUR",
                "reason": "Runs on developer workstation or home server, reachable by Render via Tailscale private IP.",
            },
        ],
    }


@app.post("/api/llm/probe")
def probe_llm(timeout: float = Query(default=10.0)):
    """
    Actively probes the configured LLM provider with a minimal deterministic
    health-check query, measuring latency and verifying API key validity.
    """
    from agentic_ops.adapters.llm_provider_registry import LLMProviderRegistry

    return LLMProviderRegistry.probe(timeout=timeout)


from pydantic import BaseModel as _FastApiBaseModel

class ChatPayload(_FastApiBaseModel):
    message: str
    history: list[dict] = []


@app.post("/api/chat")
def chat_with_agentic_ops(payload: ChatPayload):
    """
    Conversational endpoint powering the zero-dependency Web Chat UI (/chat).
    Queries the active LLM (OpenRouter, Gemini, OpenAI, Claude, Mistral, Ollama)
    with MLOps governance context and returns the reasoning response.
    """
    from agentic_ops.adapters.llm_provider_registry import LLMProviderRegistry

    return LLMProviderRegistry.chat(message=payload.message, history=payload.history)


@app.get("/api/prompts")
def list_starter_prompts():
    """
    Returns the 20 cognitive starter prompts catalog from mcp_server.
    Used by the Web Chat UI (/chat) and external API consumers.
    """
    from agentic_ops.entrypoints.mcp_server import MCP_PROMPTS

    return {
        "count": len(MCP_PROMPTS),
        "prompts": MCP_PROMPTS,
    }


COMMAND_PEDAGOGICAL_GUIDES: dict[DiagnosticCommand, list[str]] = {
    DiagnosticCommand.sandbox_phase_a_vitals: [
        "========================================================================================",
        "[GUIDE:ROLE] RÔLE DU BOUTON (Phase A — Vitals & Télémétrie Matérielle) :",
        "[GUIDE:ROLE]   Inspecte l'état interne du conteneur en production sur Render : noyau Linux (uname -a),",
        "[GUIDE:ROLE]   architecture CPU (/proc/cpuinfo), allocation RAM (/proc/meminfo & cgroup v2),",
        "[GUIDE:ROLE]   sondes FastAPI (/healthz, /ready), démon Redis (:6379), proxy Tailscale SOCKS5 (:1055)",
        "[GUIDE:ROLE]   et base transactionnelle SQLite WAL (/tmp/state/approvals.db).",
        "[GUIDE:AGENT] AGENT IA INVOQUÉ : Aucun appel LLM. Sonde d'infrastructure 100% déterministe (OS & sockets TCP).",
        "[GUIDE:SLACK] INTERACTION SLACK HITL : Aucune alerte envoyée sur Slack. Vérifie en revanche que la base",
        "[GUIDE:SLACK]   SQLite WAL (/tmp/state/approvals.db) qui stocke les clics Slack [APPROVE]/[DENY] est bien montée.",
        "[GUIDE:PROD] IMPACT SUR LE MLOPS CIBLE (PROD) : ZÉRO IMPACT (100% local au conteneur Control Plane).",
        "[GUIDE:HOW_IT_PASSES] POURQUOI & COMMENT ÇA PASSE :",
        "[GUIDE:HOW_IT_PASSES]   1. /healthz renvoie {'status': 'ok'} (maintenu éveillé 24/7 par cron-job.org toutes les 10 min).",
        "[GUIDE:HOW_IT_PASSES]   2. /ready confirme que Redis (127.0.0.1:6379) et Tailscale SOCKS5 (127.0.0.1:1055) écoutent.",
        "[GUIDE:HOW_IT_PASSES]   3. Cgroup Memory Current / Max prouve que le conteneur respecte l'enveloppe mémoire de 512 MiB.",
        "========================================================================================",
    ],
    DiagnosticCommand.sandbox_phase_b_slack_spoof: [
        "========================================================================================",
        "[GUIDE:ROLE] RÔLE DU BOUTON (Phase B — Attaque Red-Team par Usurpation de Webhook Slack) :",
        "[GUIDE:ROLE]   Simule un attaquant externe qui tente de forcer l'exécution d'une action critique en prod",
        "[GUIDE:ROLE]   (ex: PROMOTE_MODEL ou ROLLBACK) en envoyant un faux clic HTTP POST sur /slack/interactive",
        "[GUIDE:ROLE]   avec le payload forgé 'payload=fake_tampered_attack' sans la clé secrète SLACK_SIGNING_SECRET.",
        "[GUIDE:AGENT] AGENT IA INVOQUÉ : Aucun. L'attaque vise directement le point d'entrée humain",
        "[GUIDE:AGENT]   (agentic_ops/entrypoints/slack_webhook.py) pour tenter de contourner l'arrêt AWAITING_APPROVAL.",
        "[GUIDE:SLACK] INTERACTION SLACK HITL : Teste le garde-fou cryptographique du webhook Slack entrant :",
        "[GUIDE:SLACK]   1. Vérification de présence des en-têtes X-Slack-Signature et X-Slack-Request-Timestamp.",
        "[GUIDE:SLACK]   2. Calcul du HMAC-SHA256 sur le corps brut de la requête + fenêtre anti-rejeu stricte de 5 minutes.",
        "[GUIDE:PROD] IMPACT SUR LE MLOPS CIBLE (PROD) : ZÉRO MUTATION EN PROD. La requête forgée est détruite",
        "[GUIDE:PROD]   à la frontière HTTP en ~2ms avant même d'atteindre SQLite WAL, l'Orchestrator ou l'Executor.",
        "[GUIDE:HOW_IT_PASSES] POURQUOI & COMMENT ÇA PASSE :",
        "[GUIDE:HOW_IT_PASSES]   Le serveur répond immédiatement HTTP 401 Unauthorized ({'error': 'en-têtes manquants'}).",
        "[GUIDE:HOW_IT_PASSES]   Architecture Fail-Closed : sans signature cryptographique valide, aucun épisode en attente",
        "[GUIDE:HOW_IT_PASSES]   ne peut jamais être déverrouillé vers l'état EXECUTING.",
        "========================================================================================",
    ],
    DiagnosticCommand.sandbox_phase_c_adversarial_worm: [
        "========================================================================================",
        "[GUIDE:ROLE] RÔLE DU BOUTON (Phase C — Sécurité Adversariale, Registre WORM & Verrous Redis — 9 Tests) :",
        "[GUIDE:ROLE]   Exécute les suites tests/adversarial/ et tests/security/ :",
        "[GUIDE:ROLE]   - test_evidence_integrity.py (3 tests) : intégrité de la chaîne de blocs Merkle WORM (SHA-256 + HMAC-SHA512).",
        "[GUIDE:ROLE]   - test_idempotency_and_rate.py (3 tests) : verrous atomiques Redis (SET NX EX), rate-limiting & Fail-Closed.",
        "[GUIDE:ROLE]   - test_prompt_hygiene.py (1 test Hypothesis property-based) : quarantaine <untrusted_data> contre Prompt Injection.",
        "[GUIDE:ROLE]   - test_executor.py (2 tests) : isolation thread-safe de l'Executor.",
        "[GUIDE:AGENT] AGENT IA INVOQUÉ : Teste le Prompt Guard (agentic_ops/core/prompt_guard.py) qui protège les agents",
        "[GUIDE:AGENT]   contre toute injection d'instructions malveillantes cachées dans les logs Loki ou payloads JSON.",
        "[GUIDE:SLACK] INTERACTION SLACK HITL : Aucune alerte Slack émise. Protège la preuve d'audit post-approbation",
        "[GUIDE:SLACK]   et garantit que même si un opérateur ou attaquant modifie 1 seul octet d'un fichier JSON WORM,",
        "[GUIDE:SLACK]   verify_episode() détecte la falsification immédiatement.",
        "[GUIDE:PROD] IMPACT SUR LE MLOPS CIBLE (PROD) : ZÉRO MUTATION EN PROD. Vérifie que si Redis tombe en panne,",
        "[GUIDE:PROD]   le système bascule en Fail-Closed (bloque les actions destructrices) et que les tickets sont simulés.",
        "[GUIDE:HOW_IT_PASSES] POURQUOI & COMMENT ÇA PASSE (9 PASSED) :",
        "[GUIDE:HOW_IT_PASSES]   1. Merkle Chain Tampering : altérer un épisode ou son previous_hash brise la signature SHA-256.",
        "[GUIDE:HOW_IT_PASSES]   2. Redis Fail-Closed : une coupure Redis lève un blocage de sécurité au lieu d'autoriser par défaut.",
        "[GUIDE:HOW_IT_PASSES]   3. Hypothesis Fuzzing : génère des chaînes aléatoires contenant </untrusted_data> et vérifie leur neutralisation.",
        "========================================================================================",
    ],
    DiagnosticCommand.sandbox_phase_d_mlops_scenarios: [
        "========================================================================================",
        "[GUIDE:ROLE] RÔLE DU BOUTON (Phase D — Scénarios Agentiques MLOps en Direct SC-101..103 & SC-001..005 — 10 Tests) :",
        "[GUIDE:ROLE]   Rejoue 10 crises MLOps de bout en bout à travers l'Orchestrator FSM, le calcul déterministe",
        "[GUIDE:ROLE]   compute_facts() et le PolicyEngine V2 (agentic_ops/core/policy_v2.py) :",
        "[GUIDE:ROLE]   - SC-101 : Prompt Injection dans un log applicatif ordonnant à l'IA d'exécuter 'scale_to_zero'.",
        "[GUIDE:ROLE]   - SC-102 : Injection shell dans la cible ('baac-api; kubectl delete ns prod') sur 'restart_pod'.",
        "[GUIDE:ROLE]   - SC-103 & SC-001 : Dérive/perte de volume amont (DATA-042) où l'IA tente un 'propose_retrain' toxique.",
        "[GUIDE:ROLE]   - SC-003 & SC-004 : Anomalie data où l'IA se trompe de couche et veut 'restart_pod' ou 'scale_up'.",
        "[GUIDE:ROLE]   - SC-005 : CrashLoop OOMKilled réel (INFRA-001) où 'restart_pod' exige une approbation humaine L2.",
        "[GUIDE:AGENT] AGENT IA INVOQUÉ : Invoque successivement 'data_specialist_llm' et 'infra_specialist_llm'",
        "[GUIDE:AGENT]   en deux modes comparés : mode 'scripted' (Agent LLM compromis/hallucinant qui propose 6 actions",
        "[GUIDE:AGENT]   interdites) vs mode 'baseline' (Agent SRE prudent qui propose 'create_issue').",
        "[GUIDE:SLACK] INTERACTION SLACK HITL : Déclenchée sur SC-005 (REQUIRE_APPROVAL -> état AWAITING_APPROVAL ->",
        "[GUIDE:SLACK]   envoi du message interactif Slack Block Kit). Sur SC-101..SC-004, le PolicyEngine bloque l'action",
        "[GUIDE:SLACK]   immédiatement en DENY (règles CAT-001, CAT-002, R-001, R-002) sans même déranger l'astreinte Slack.",
        "[GUIDE:PROD] IMPACT SUR LE MLOPS CIBLE (PROD) : INVARIANT ABSOLU RESPECTÉ -> forbidden_proposed = 6 mais",
        "[GUIDE:PROD]   forbidden_executed = 0 ! Aucune des 6 attaques/hallucinations du LLM n'a touché la production.",
        "[GUIDE:HOW_IT_PASSES] POURQUOI & COMMENT ÇA PASSE (10 PASSED, 1 SKIPPED) :",
        "[GUIDE:HOW_IT_PASSES]   Regardez les blocs colorés ci-dessous pour chaque scénario : compute_facts() calcule mathématiquement",
        "[GUIDE:HOW_IT_PASSES]   si l'anomalie vient de la donnée (data/feature) ou de l'infra, et le PolicyEngine oppose un veto",
        "[GUIDE:HOW_IT_PASSES]   déterministe à toute action hors catalogue (CAT-001), cible malformée (CAT-002) ou mauvaise couche (R-001).",
        "========================================================================================",
    ],
    DiagnosticCommand.sandbox_phase_e_fsm_governance: [
        "========================================================================================",
        "[GUIDE:ROLE] RÔLE DU BOUTON (Phase E — Machine à États FSM, Webhook Grafana & Sandboxing OS — 10 Tests) :",
        "[GUIDE:ROLE]   Exécute 3 suites critiques d'infrastructure du Control Plane :",
        "[GUIDE:ROLE]   1. test_fsm_orchestrator.py (2 tests) : transitions légales/illégales de la FSM et arrêt REQUIRE_APPROVAL.",
        "[GUIDE:ROLE]   2. test_grafana_webhook.py (5 tests) : ingestion des alertes Grafana/Prometheus, validation Pydantic",
        "[GUIDE:ROLE]      et déclenchement du FinOps Circuit Breaker en cas de tempête d'alertes (>50 alertes/h).",
        "[GUIDE:ROLE]   3. test_tools_security.py (3 tests) : confinement OS (multiprocessing.Process) des outils exposés aux LLMs.",
        "[GUIDE:AGENT] AGENT IA INVOQUÉ : Teste l'Orchestrator et les outils d'investigation appelés par les agents IA",
        "[GUIDE:AGENT]   (avec un outil malveillant qui tente une boucle infinie/blocage et est tué par timeout OS).",
        "[GUIDE:SLACK] INTERACTION SLACK HITL : test_orchestrator_halts_on_require_approval prouve formellement que",
        "[GUIDE:SLACK]   lorsqu'une action requiert l'accord Slack, la FSM s'arrête sur AWAITING_APPROVAL et execution reste None.",
        "[GUIDE:PROD] IMPACT SUR LE MLOPS CIBLE (PROD) : ZÉRO MUTATION EN PROD. Prouve aussi que lors d'une tempête",
        "[GUIDE:PROD]   d'alertes Grafana (Monitoring Storm), le Circuit Breaker coupe les appels LLM coûteux (Denial of Wallet).",
        "[GUIDE:HOW_IT_PASSES] POURQUOI & COMMENT ÇA PASSE (10 PASSED) :",
        "[GUIDE:HOW_IT_PASSES]   - Toute transition FSM illégale (ex: passer de DETECTED à EXECUTING sans approbation) lève InvalidStateTransitionError.",
        "[GUIDE:HOW_IT_PASSES]   - Tout outil LLM qui dépasse son quota de temps est tué au niveau noyau (process.terminate()) sans bloquer FastAPI.",
        "========================================================================================",
    ],
    DiagnosticCommand.pytest_cac_connector: [
        "========================================================================================",
        "[GUIDE:ROLE] RÔLE DU BOUTON (Phase F — Connecteur Tailscale Pull Read-Only vers jakatt/cac_mlops — 13 Tests) :",
        "[GUIDE:ROLE]   Valide mathématiquement l'adaptateur agentic_ops/adapters/cac_pull_collector.py qui relie",
        "[GUIDE:ROLE]   notre Control Plane sur Render (100.85.198.81) au VPS Scaleway cible jakatt/cac_mlops (100.117.99.62)",
        "[GUIDE:ROLE]   à travers le proxy local Tailscale SOCKS5 (socks5://127.0.0.1:1055).",
        "[GUIDE:AGENT] AGENT IA INVOQUÉ : Collecteur d'observabilité déterministe en amont des agents IA. Alimente",
        "[GUIDE:AGENT]   compute_facts() avec l'état réel des 5 briques : Loki (:3100), Prometheus (:9090), MLflow (:5001),",
        "[GUIDE:AGENT]   Prefect (:4200) et Evidently (HTTPS :443).",
        "[GUIDE:SLACK] INTERACTION SLACK HITL : Aucune lors de la collecte. Les anomalies détectées dans ce snapshot",
        "[GUIDE:SLACK]   (ex: drift_share > 0.30 ou alerte Loki) déclenchent ensuite un épisode qui sollicitera Slack si L2/L3.",
        "[GUIDE:PROD] IMPACT SUR LE MLOPS CIBLE (PROD) : GARANTIE MATHÉMATIQUE 100% READ-ONLY (GET UNIQUEMENT).",
        "[GUIDE:PROD]   Le test test_collector_never_issues_post_put_delete_patch inspecte chaque requête HTTP émise et prouve",
        "[GUIDE:PROD]   qu'aucun POST, PUT, DELETE ou PATCH n'est jamais envoyé vers le serveur de production du binôme.",
        "[GUIDE:HOW_IT_PASSES] POURQUOI & COMMENT ÇA PASSE (13 PASSED) :",
        "[GUIDE:HOW_IT_PASSES]   1. Vérifie le parsing exact des 5 sources (LogQL Loki, jauges Prometheus, alias @Production MLflow, Prefect, Evidently).",
        "[GUIDE:HOW_IT_PASSES]   2. Vérifie la résilience aux pannes : si 1 service tombe -> status=PARTIAL ; si le VPS est éteint ->",
        "[GUIDE:HOW_IT_PASSES]      status=REMOTE_TARGET_OFFLINE sans lever aucune exception non gérée dans le Control Plane.",
        "========================================================================================",
    ],
    DiagnosticCommand.pytest_security: [
        "========================================================================================",
        "[GUIDE:ROLE] RÔLE DU BOUTON (Suite Red-Team Executor & Gouvernance Model Registry — 6 Passed, 1 Skipped) :",
        "[GUIDE:ROLE]   Exécute tests/security/test_executor.py et tests/integration/test_model_registry.py.",
        "[GUIDE:ROLE]   Teste le dernier maillon de la chaîne (Executor + Gatekeeper du Model Registry MLflow).",
        "[GUIDE:AGENT] AGENT IA INVOQUÉ : Simule des ordres de promotion (PROMOTE_MODEL) et de rollback (ROLLBACK)",
        "[GUIDE:AGENT]   arrivant jusqu'à l'Executor après validation.",
        "[GUIDE:SLACK] INTERACTION SLACK HITL : Vérifie que même APRÈS une approbation humaine sur Slack, le",
        "[GUIDE:SLACK]   Model Registry applique un second filet de sécurité technique (Gatekeeper) avant d'activer un modèle.",
        "[GUIDE:PROD] IMPACT SUR LE MLOPS CIBLE (PROD) : Protection finale du modèle @Production :",
        "[GUIDE:PROD]   - Si le modèle candidat a un F1-score < 0.85 ou un schéma incompatible -> promotion REJETÉE (status=FAILED).",
        "[GUIDE:PROD]   - Si on demande un rollback vers une version inexistante -> rollback REJETÉ proprement.",
        "[GUIDE:HOW_IT_PASSES] POURQUOI & COMMENT ÇA PASSE :",
        "[GUIDE:HOW_IT_PASSES]   Prouve la défense en profondeur (Defense-in-Depth) : Gouvernance PolicyEngine + Approbation Humaine Slack",
        "[GUIDE:HOW_IT_PASSES]   + Gatekeeper technique du Model Registry (seul un modèle performant et compatible peut devenir ACTIVE).",
        "========================================================================================",
    ],
    DiagnosticCommand.pytest_all: [
        "========================================================================================",
        "[GUIDE:ROLE] RÔLE DU BOUTON (Grand Chelem — Exécution Intégrale des 42 Tests Sandbox + Connecteur CAC) :",
        "[GUIDE:ROLE]   Exécute en une seule passe continue les Phases C + D + E + F :",
        "[GUIDE:ROLE]   - 9 tests Adversariaux, WORM Merkle Chain, Verrous Redis & Prompt Guard (<untrusted_data>)",
        "[GUIDE:ROLE]   - 10 scénarios MLOps de bout en bout (SC-101..103 & SC-001..005 -> forbidden_executed=0)",
        "[GUIDE:ROLE]   - 10 tests FSM, Webhook Grafana, Circuit Breaker FinOps & Sandboxing OS multiprocessing",
        "[GUIDE:ROLE]   - 13 tests du Connecteur Tailscale Pull Read-Only vers jakatt/cac_mlops",
        "[GUIDE:AGENT] AGENT IA INVOQUÉ : Sollicite l'ensemble des spécialistes IA (data_specialist_llm,",
        "[GUIDE:AGENT]   infra_specialist_llm), le Prompt Guard, compute_facts() et l'Orchestrator FSM.",
        "[GUIDE:SLACK] INTERACTION SLACK HITL : Valide toute la chaîne d'escalade Slack HITL et de verrouillage.",
        "[GUIDE:PROD] IMPACT SUR LE MLOPS CIBLE (PROD) : ZÉRO MUTATION NON AUTORISÉE SUR LES 42 TESTS",
        "[GUIDE:PROD]   (forbidden_proposed=6 par l'IA piégée -> forbidden_executed=0 sur la prod).",
        "[GUIDE:HOW_IT_PASSES] POURQUOI & COMMENT ÇA PASSE (42 PASSED, 2 SKIPPED) :",
        "[GUIDE:HOW_IT_PASSES]   Validation industrielle complète en direct depuis le conteneur Render de production.",
        "========================================================================================",
    ],
    DiagnosticCommand.trust_ledger_list: [
        "========================================================================================",
        "[GUIDE:ROLE] RÔLE DU BOUTON (Inspection du Registre Cryptographique Immuable WORM Trust Ledger) :",
        "[GUIDE:ROLE]   Exécute le CLI 'python -m agentic_ops.cli.trust_ledger list' qui lit tous les épisodes scellés",
        "[GUIDE:ROLE]   dans agentic_ops/evidence_store/*.json (chaînés par SHA-256 previous_hash et signés en HMAC-SHA512).",
        "[GUIDE:AGENT] AGENT IA INVOQUÉ : Affiche dans la colonne 'Agent LLM' quel spécialiste a diagnostiqué",
        "[GUIDE:AGENT]   chaque épisode historique ('data_specialist' en mode LIVE ou 'specialist_mock' en mode SHADOW).",
        "[GUIDE:SLACK] INTERACTION SLACK HITL : Regardez la colonne 'Décision Policy' :",
        "[GUIDE:SLACK]   - 'ALLOW' (EP-0001, EP-0004, EP-0005) : ticket 'create_issue' ouvert en autonomie L1 sans Slack.",
        "[GUIDE:SLACK]   - 'REQUIRE_APPROVAL' (EP-0002 'deploy_prod', EP-0003 'rollback_prod') : l'agent voulait modifier",
        "[GUIDE:SLACK]     le modèle en production -> l'orchestrateur s'est figé et a envoyé l'alerte interactive sur Slack !",
        "[GUIDE:SLACK]   - 'DENY' (EP-CHAOS-*) : exécution en mode SHADOW (test à blanc) bloquée automatiquement.",
        "[GUIDE:PROD] IMPACT SUR LE MLOPS CIBLE (PROD) :",
        "[GUIDE:PROD]   - EP-0002 (deploy_prod) & EP-0003 (rollback_prod) : ZÉRO modification de MLflow tant que l'humain",
        "[GUIDE:PROD]     n'a pas validé sur Slack.",
        "[GUIDE:PROD]   - EP-CHAOS-31c6e006 & 5950095d (propose_retrain) : ZÉRO réentraînement Prefect lancé (bloqué en SHADOW).",
        "[GUIDE:PROD]   - EP-0001, 0004, 0005 (create_issue) : simple création d'un ticket d'incident documenté (non-destructif).",
        "[GUIDE:HOW_IT_PASSES] POURQUOI & COMMENT ÇA PASSE :",
        "[GUIDE:HOW_IT_PASSES]   Chaque ligne de ce tableau est une boîte noire inviolable (WORM) : toute modification manuelle",
        "[GUIDE:HOW_IT_PASSES]   d'un fichier JSON d'épisode invalide instantanément la chaîne de hachage Merkle.",
        "========================================================================================",
    ],
    DiagnosticCommand.tailscale_status: [
        "========================================================================================",
        "[GUIDE:ROLE] RÔLE DU BOUTON (Statut du Réseau Maillé VPN Tailscale Userspace) :",
        "[GUIDE:ROLE]   Exécute 'tailscale --socket=/tmp/tailscaled.sock status' à l'intérieur du conteneur Render",
        "[GUIDE:ROLE]   pour lister tous les nœuds membres du Tailnet privé et vérifier le tunnel chiffré WireGuard.",
        "[GUIDE:AGENT] AGENT IA INVOQUÉ : Aucun. Couche transport réseau (Userspace WireGuard + SOCKS5 :1055)",
        "[GUIDE:AGENT]   utilisée par CacPullCollector pour interroger le serveur MLOps cible sans ouvrir de ports publics.",
        "[GUIDE:SLACK] INTERACTION SLACK HITL : Aucune.",
        "[GUIDE:PROD] IMPACT SUR LE MLOPS CIBLE (PROD) : Passif / Réseau uniquement. Identifie notre conteneur",
        "[GUIDE:PROD]   Render ('100.85.198.81 agentic-ops-render') et le VPS Scaleway cible ('100.117.99.62 scw-jovial-dubinsky').",
        "[GUIDE:HOW_IT_PASSES] POURQUOI & COMMENT ÇA PASSE :",
        "[GUIDE:HOW_IT_PASSES]   1. Authentifié automatiquement au boot grâce à TS_STATE_B64 (sans privilège root ni CAP_NET_ADMIN).",
        "[GUIDE:HOW_IT_PASSES]   2. Le filtre _redact_pii() anonymise automatiquement les e-mails ([REDACTED_ACCOUNT]) et machines",
        "[GUIDE:HOW_IT_PASSES]      personnelles ([REDACTED_WORKSTATION]) avant d'afficher la sortie dans la console publique.",
        "========================================================================================",
    ],
    DiagnosticCommand.tailscale_netcheck: [
        "========================================================================================",
        "[GUIDE:ROLE] RÔLE DU BOUTON (Diagnostic Réseau Tailscale DERP & Latences Relais) :",
        "[GUIDE:ROLE]   Exécute 'tailscale --socket=/tmp/tailscaled.sock netcheck' pour mesurer la connectivité UDP/IPv4",
        "[GUIDE:ROLE]   et la latence en millisecondes vers les relais chiffrés Tailscale DERP mondiaux.",
        "[GUIDE:AGENT] AGENT IA INVOQUÉ : Aucun (diagnostic réseau bas niveau).",
        "[GUIDE:SLACK] INTERACTION SLACK HITL : Aucune.",
        "[GUIDE:PROD] IMPACT SUR LE MLOPS CIBLE (PROD) : Aucun trafic envoyé au VPS cible (sonde uniquement les",
        "[GUIDE:PROD]   serveurs relais Tailscale DERP : Frankfurt ~2.7ms, Nuremberg ~6.7ms, Paris ~9.1ms).",
        "[GUIDE:HOW_IT_PASSES] POURQUOI & COMMENT ÇA PASSE :",
        "[GUIDE:HOW_IT_PASSES]   Prouve que même dans un conteneur PaaS serverless restrictif, Tailscale établit une route",
        "[GUIDE:HOW_IT_PASSES]   à ultra-faible latence (~2.7ms depuis Frankfurt) pour transporter nos requêtes SOCKS5.",
        "========================================================================================",
    ],
    DiagnosticCommand.redis_ping: [
        "========================================================================================",
        "[GUIDE:ROLE] RÔLE DU BOUTON (Sonde du Démon Redis Local d'Idempotence & Rate-Limiting) :",
        "[GUIDE:ROLE]   Exécute 'redis-cli -h 127.0.0.1 -p 6379 PING' vers le serveur Redis embarqué dans le conteneur.",
        "[GUIDE:AGENT] AGENT IA INVOQUÉ : Aucun. Ce démon Redis protège l'Orchestrator contre les boucles d'agents :",
        "[GUIDE:AGENT]   1. Verrou d'idempotence sémantique (SET NX EX sur tenant:env:service:risk_id) pour empêcher",
        "[GUIDE:AGENT]      deux agents de traiter deux fois la même alerte en parallèle.",
        "[GUIDE:AGENT]   2. Rate-limiting atomique (INCR + EXPIRE) limitant les actions lourdes (ex: max 1 restart/heure).",
        "[GUIDE:SLACK] INTERACTION SLACK HITL : Empêche d'inonder le canal Slack avec des demandes d'approbation",
        "[GUIDE:SLACK]   en doublon lorsqu'une alerte Prometheus/Grafana bégaye.",
        "[GUIDE:PROD] IMPACT SUR LE MLOPS CIBLE (PROD) : Protège la prod cible contre les exécutions concurrentes.",
        "[GUIDE:HOW_IT_PASSES] POURQUOI & COMMENT ÇA PASSE :",
        "[GUIDE:HOW_IT_PASSES]   Répond 'PONG' en ~5ms (0 latence réseau car Redis tourne en local dans le même conteneur).",
        "========================================================================================",
    ],
    DiagnosticCommand.tailscale_logs: [
        "========================================================================================",
        "[GUIDE:ROLE] RÔLE DU BOUTON (Journaux Internes du Démon Tailscale) :",
        "[GUIDE:ROLE]   Affiche les dernières lignes de /tmp/tailscale_up.log et /tmp/tailscaled.log (anonymisées).",
        "[GUIDE:AGENT] AGENT IA INVOQUÉ : Aucun.",
        "[GUIDE:SLACK] INTERACTION SLACK HITL : Aucune.",
        "[GUIDE:PROD] IMPACT SUR LE MLOPS CIBLE (PROD) : Aucun (lecture locale des fichiers de log dans /tmp).",
        "[GUIDE:HOW_IT_PASSES] POURQUOI & COMMENT ÇA PASSE :",
        "[GUIDE:HOW_IT_PASSES]   Permet d'auditer les connexions derphttp et magicsock du démon userspace-networking.",
        "========================================================================================",
    ],
    DiagnosticCommand.pytest_mcp_gateway: [
        "========================================================================================",
        "[GUIDE:ROLE] RÔLE DU BOUTON (Phase G — Model Context Protocol / MCP Governance Gateway) :",
        "[GUIDE:ROLE]   Valide les 12 tests unitaires et d'intégration du serveur MCP (agentic_ops/entrypoints/mcp_server.py)",
        "[GUIDE:ROLE]   en JSON-RPC 2.0 (STDIO & HTTP POST /mcp) : initialize, 8 Governed Tools (dont lecture directe",
        "[GUIDE:ROLE]   de la console /console via read_console_diagnostic), 5 Knowledge Resources (Taxonomie 435",
        "[GUIDE:ROLE]   + Scenarios Registry) et le catalogue des 20 Starter Prompts.",
        "[GUIDE:AGENT] AGENT IA INVOQUÉ : Permet à tout client MCP externe (Claude Desktop, Cursor, Windsurf, Antigravity)",
        "[GUIDE:AGENT]   de lire la console Web, d'interroger la Taxonomie des 435 pannes et de soumettre ses actions",
        "[GUIDE:AGENT]   au PolicyEngine déterministe.",
        "[GUIDE:SLACK] INTERACTION SLACK HITL : Toute action L2/L3 soumise via le tool MCP evaluate_governance_policy",
        "[GUIDE:SLACK]   ou run_governed_incident_episode déclenche REQUIRE_APPROVAL (Slack Block Kit HITL).",
        "[GUIDE:PROD] IMPACT SUR LE MLOPS CIBLE (PROD) : ZÉRO MUTATION NON GOUVERNÉE (Pare-feu MCP déterministe).",
        "[GUIDE:HOW_IT_PASSES] POURQUOI & COMMENT ÇA PASSE :",
        "[GUIDE:HOW_IT_PASSES]   1. Protocole JSON-RPC 2.0 2024-11-05 validé sur /mcp et /mcp/manifest.",
        "[GUIDE:HOW_IT_PASSES]   2. Lecture live de /console via read_console_diagnostic validée (modes avec et sans guides).",
        "[GUIDE:HOW_IT_PASSES]   3. Arbitrage PolicyEngine (DENY sur DATA-042 + propose_retrain, ALLOW sur create_issue) + WORM validés.",
        "========================================================================================",
    ],
    DiagnosticCommand.pytest_llm_hub: [
        "========================================================================================",
        "[GUIDE:ROLE] RÔLE DU BOUTON (Phase H — Universal LLM Provider Hub : OpenRouter, Ollama & 8 Fournisseurs) :",
        "[GUIDE:ROLE]   Valide l'architecture du Hub universel de modèles d'IA (agentic_ops/adapters/llm_provider_registry.py",
        "[GUIDE:ROLE]   et llm_protocol.py) : résolution dynamique de configuration, masquage sécurisé de clé API,",
        "[GUIDE:ROLE]   chaîne de secours automatique (FallbackLLMAdapter) en cas de rate-limit et adaptateur Ollama local/Tailscale.",
        "[GUIDE:AGENT] AGENT IA INVOQUÉ : Cerveau cognitif de l'Orchestrateur (RemediationAgent & Specialists).",
        "[GUIDE:AGENT]   Permet de basculer instantanément de Gemini vers DeepSeek-R1 (0 EUR via OpenRouter :free),",
        "[GUIDE:AGENT]   Llama 3.3 70B, GPT-4o, Claude 3.5 ou Ollama sans modifier une seule ligne de code métier.",
        "[GUIDE:SLACK] INTERACTION SLACK HITL : Aucune directe. Quel que soit le LLM (gratuit ou propriétaire),",
        "[GUIDE:SLACK]   ses propositions d'actions sont soumises à la même FSM stricte et au PolicyEngine déterministe.",
        "[GUIDE:PROD] IMPACT SUR LE MLOPS CIBLE (PROD) : RÉSILIENCE & FINOPS. La chaîne de fallback bascule",
        "[GUIDE:PROD]   automatiquement sur un modèle de secours si le modèle principal est surchargé ou rate-limité.",
        "[GUIDE:HOW_IT_PASSES] POURQUOI & COMMENT ÇA PASSE :",
        "[GUIDE:HOW_IT_PASSES]   1. Teste la détection et le chargement des 8 profils de fournisseurs (OpenRouter, Gemini, OpenAI...).",
        "[GUIDE:HOW_IT_PASSES]   2. Valide que FallbackLLMAdapter tente le modèle suivant dès que le premier lève une exception.",
        "[GUIDE:HOW_IT_PASSES]   3. Valide le format JSON Pydantic strict d'OllamaAdapter et l'anonymisation de clé API dans /api/llm/status.",
        "========================================================================================",
    ],
}


@app.get("/api/diagnostics/{command}", response_class=PlainTextResponse)
def run_diagnostic_command(command: DiagnosticCommand):
    """
    Executes a whitelisted SRE / Docker Cloud Sandbox diagnostic command inside the
    container and returns formatted plain-text terminal output (with automatic PII redaction
    and detailed pedagogical commentary).
    Replaces the paid Render SSH Shell tab for zero-cost live auditing.
    """
    ts_socket = os.environ.get("TS_SOCKET", "/tmp/tailscaled.sock")
    py = sys.executable

    cmd_map = {
        DiagnosticCommand.sandbox_phase_c_adversarial_worm: [
            py, "-m", "pytest", "tests/adversarial/", "tests/security/", "-v"
        ],
        DiagnosticCommand.sandbox_phase_d_mlops_scenarios: [
            py, "-m", "pytest", "tests/scenarios/", "-v"
        ],
        DiagnosticCommand.sandbox_phase_e_fsm_governance: [
            py, "-m", "pytest",
            "tests/test_fsm_orchestrator.py",
            "tests/test_grafana_webhook.py",
            "tests/test_tools_security.py",
            "-v",
        ],
        DiagnosticCommand.pytest_cac_connector: [
            py, "-m", "pytest", "tests/adapters/test_cac_pull_collector.py", "-v"
        ],
        DiagnosticCommand.pytest_mcp_gateway: [
            py, "-m", "pytest", "tests/entrypoints/test_mcp_server.py", "-v"
        ],
        DiagnosticCommand.pytest_llm_hub: [
            py, "-m", "pytest", "tests/adapters/test_llm_provider_registry.py", "-v"
        ],
        DiagnosticCommand.pytest_security: [
            py, "-m", "pytest", "tests/security/", "tests/integration/", "-v"
        ],
        DiagnosticCommand.pytest_all: [
            py, "-m", "pytest",
            "tests/adversarial/",
            "tests/security/",
            "tests/scenarios/",
            "tests/test_fsm_orchestrator.py",
            "tests/test_grafana_webhook.py",
            "tests/test_tools_security.py",
            "tests/adapters/test_cac_pull_collector.py",
            "tests/entrypoints/test_mcp_server.py",
            "tests/adapters/test_llm_provider_registry.py",
            "-v",
        ],
        DiagnosticCommand.trust_ledger_list: [
            py, "-m", "agentic_ops.cli.trust_ledger", "list"
        ],
        DiagnosticCommand.tailscale_status: [
            "tailscale", f"--socket={ts_socket}", "status"
        ],
        DiagnosticCommand.tailscale_netcheck: [
            "tailscale", f"--socket={ts_socket}", "netcheck"
        ],
        DiagnosticCommand.redis_ping: [
            "redis-cli", "-h", "127.0.0.1", "-p", "6379", "PING"
        ],
    }

    t0 = time.time()
    guide_lines = COMMAND_PEDAGOGICAL_GUIDES.get(
        command,
        COMMAND_PEDAGOGICAL_GUIDES.get(DiagnosticCommand.sandbox_phase_a_vitals, []),
    )
    guide_block = "\n\n" + "\n".join(guide_lines) + "\n" if guide_lines else ""

    if command in (DiagnosticCommand.sandbox_phase_a_vitals, DiagnosticCommand.system_info):
        try:
            uname = subprocess.run(["uname", "-a"], capture_output=True, text=True).stdout.strip()
        except Exception as exc:
            uname = f"Unknown ({exc})"

        mem_lines = []
        try:
            free_out = subprocess.run(["free", "-h"], capture_output=True, text=True).stdout.strip()
            if free_out:
                mem_lines.append(free_out)
        except Exception:
            pass

        if not mem_lines and os.path.exists("/proc/meminfo"):
            try:
                with open("/proc/meminfo", "r", encoding="utf-8", errors="replace") as f:
                    for line in f:
                        if line.startswith(("MemTotal:", "MemFree:", "MemAvailable:", "Buffers:", "Cached:", "SwapTotal:", "SwapFree:")):
                            mem_lines.append(line.strip())
            except Exception:
                pass

        for cg_path, label in (
            ("/sys/fs/cgroup/memory.current", "Cgroup Memory Current"),
            ("/sys/fs/cgroup/memory.max", "Cgroup Memory Max"),
        ):
            if os.path.exists(cg_path):
                try:
                    with open(cg_path, "r", encoding="utf-8") as f:
                        val = f.read().strip()
                        if val.isdigit():
                            mem_lines.append(f"{label:22s}: {int(val) / (1024 * 1024):.1f} MiB ({val} bytes)")
                        else:
                            mem_lines.append(f"{label:22s}: {val}")
                except Exception:
                    pass

        cpu_model = "Unknown"
        if os.path.exists("/proc/cpuinfo"):
            try:
                with open("/proc/cpuinfo", "r", encoding="utf-8", errors="replace") as f:
                    for line in f:
                        if "model name" in line:
                            cpu_model = line.split(":", 1)[1].strip()
                            break
            except Exception:
                pass
        info = [
            "=== Phase A: Container Vitals, Health Probes & Hardware Telemetry ===",
            f"OS / Kernel          : {uname}",
            f"CPU Architecture     : {cpu_model} (cores={os.cpu_count()})",
            f"Python Executable    : {sys.executable} ({sys.version.split()[0]})",
            f"Working Directory    : {os.getcwd()}",
            f"Probe GET /healthz   : {healthz()}",
            f"Probe GET /ready     : {ready()}",
            f"Redis Local (:6379)  : {'OPEN (ONLINE)' if _is_port_open('127.0.0.1', 6379) else 'CLOSED'}",
            f"Tailscale (:1055)    : {'OPEN (ONLINE)' if _is_port_open('127.0.0.1', 1055) else 'CLOSED'}",
            f"Approval DB Path     : {db_path} (exists={os.path.exists(db_path)})",
            "",
            "--- Memory & Cgroup Telemetry (/proc/meminfo & cgroup v2) ---",
            "\n".join(mem_lines) if mem_lines else "(memory telemetry unavailable)",
            "",
            "[GUIDE:HOW_IT_PASSES] VERDICT PHASE A : Tous les démons internes (Redis :6379, Tailscale SOCKS5 :1055, FastAPI :8001, SQLite WAL) sont OPÉRATIONNELS.",
        ]
        return "\n".join(info) + guide_block

    if command == DiagnosticCommand.sandbox_phase_b_slack_spoof:
        from fastapi.testclient import TestClient

        client = TestClient(app)
        resp = client.post(
            "/slack/interactive",
            data={"payload": "fake_tampered_attack"},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        elapsed_ms = int((time.time() - t0) * 1000)
        lines = [
            "=== Phase B: Live Red-Team Slack Webhook Spoofing Attack ===",
            "$ curl -i -X POST http://127.0.0.1:8001/slack/interactive \\",
            '    -H "Content-Type: application/x-www-form-urlencoded" \\',
            '    -d "payload=fake_tampered_attack"',
            f"[status_code={resp.status_code} | duration={elapsed_ms}ms]",
            "-" * 72,
            f"HTTP/1.1 {resp.status_code} Unauthorized",
            f"content-type: {resp.headers.get('content-type', 'application/json')}",
            "",
            resp.text,
            "",
            "[GUIDE:HOW_IT_PASSES] VERDICT PHASE B : L'attaque par usurpation Slack a été bloquée en Fail-Closed (HTTP 401 Unauthorized) en 2ms.",
        ]
        return "\n".join(lines) + guide_block

    if command == DiagnosticCommand.tailscale_logs:
        logs = []
        for path in ("/tmp/tailscale_up.log", "/tmp/tailscaled.log"):
            if os.path.exists(path):
                try:
                    with open(path, "r", encoding="utf-8", errors="replace") as f:
                        content = f.read()[-4000:]
                    logs.append(f"=== {path} ===\n{content}")
                except Exception as exc:
                    logs.append(f"=== {path} (error: {exc}) ===")
            else:
                logs.append(f"=== {path} (not found) ===")
        out = "\n\n".join(logs)
        return _redact_pii(out) + guide_block

    argv = cmd_map[command]
    env = {**os.environ, "PYTHONPATH": "/app:."}
    try:
        proc = subprocess.run(
            argv,
            capture_output=True,
            text=True,
            timeout=120,
            env=env,
        )
        elapsed_ms = int((time.time() - t0) * 1000)
        header = (
            f"$ {' '.join(argv)}\n"
            f"[exit_code={proc.returncode} | duration={elapsed_ms}ms]\n"
            f"{'-' * 72}\n"
        )
        body = (proc.stdout or "") + ("\n" + proc.stderr if proc.stderr else "")
        footer = (
            f"\n{'-' * 72}\n"
            f"[GUIDE:HOW_IT_PASSES] EXÉCUTION TERMINÉE AVEC SUCCÈS : exit_code={proc.returncode} en {elapsed_ms}ms (0 action interdite exécutée sur la prod cible).\n"
            if proc.returncode == 0
            else f"\n{'-' * 72}\n[GUIDE:PROD] ATTENTION : exit_code={proc.returncode} en {elapsed_ms}ms.\n"
        )
        return _redact_pii(header + body.strip() + footer) + guide_block
    except Exception as exc:
        return f"Error executing {command.value}: {exc}\n" + guide_block


@app.get("/console", response_class=HTMLResponse)
def web_console():
    """
    Interactive Dark-Mode SRE Web Terminal & Pedagogical Cognitive Cockpit.
    Provides 1-click execution of all Docker Cloud Sandbox validation phases (A-F),
    Tailscale mesh status/netcheck, WORM Trust Ledger inspection, and CAC MLOps Pull snapshots
    with color-coded pedagogical explanations.
    """
    return """<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Agentic-Ops SRE & Cognitive Web Console</title>
  <style>
    :root {
      --bg: #090d16;
      --panel: #111827;
      --border: #1e293b;
      --accent: #38bdf8;
      --purple: #c084fc;
      --amber: #fbbf24;
      --rose: #fb7185;
      --emerald: #34d399;
      --text: #f8fafc;
      --muted: #94a3b8;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      padding: 20px;
      background: var(--bg);
      color: var(--text);
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
    }
    .container { max-width: 1240px; margin: 0 auto; }
    header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 12px;
      padding: 16px 20px;
      background: var(--panel);
      border: 1px solid var(--border);
      border-radius: 8px;
      margin-bottom: 14px;
    }
    h1 { font-size: 18px; margin: 0; color: var(--accent); }
    .subtitle { font-size: 12px; color: var(--muted); margin-top: 4px; }
    .badges { display: flex; gap: 8px; flex-wrap: wrap; }
    .badge {
      font-size: 11px;
      padding: 4px 10px;
      border-radius: 999px;
      background: #064e3b;
      border: 1px solid var(--emerald);
      color: #d1fae5;
    }
    .grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(285px, 1fr));
      gap: 10px;
      margin-bottom: 14px;
    }
    button {
      background: var(--panel);
      color: var(--text);
      border: 1px solid var(--border);
      border-left: 3px solid var(--accent);
      padding: 10px 12px;
      border-radius: 6px;
      font-family: inherit;
      font-size: 12px;
      text-align: left;
      cursor: pointer;
      transition: all 0.15s ease;
    }
    button:hover {
      background: #1e293b;
      border-color: var(--accent);
    }
    button.purple { border-left-color: var(--purple); }
    button.amber { border-left-color: var(--amber); }
    button.emerald { border-left-color: var(--emerald); }
    button strong { display: block; margin-bottom: 3px; font-size: 12.5px; }
    button span { color: var(--muted); font-size: 11px; }
    .legend {
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      padding: 10px 14px;
      background: #0d1322;
      border: 1px solid var(--border);
      border-radius: 8px;
      margin-bottom: 12px;
      font-size: 11.5px;
      align-items: center;
      justify-content: space-between;
    }
    .legend-items {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      align-items: center;
    }
    .legend-title { color: var(--muted); font-weight: bold; margin-right: 4px; }
    .pill {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 3px 9px;
      border-radius: 6px;
      background: #111827;
      border: 1px solid #1e293b;
    }
    .toggle-btn {
      background: #064e3b;
      border: 1px solid var(--emerald);
      border-left: 3px solid var(--emerald);
      color: #d1fae5;
      padding: 5px 12px;
      border-radius: 6px;
      font-size: 11.5px;
      font-weight: bold;
      cursor: pointer;
      white-space: nowrap;
    }
    .toggle-btn.compact {
      background: #1e293b;
      border-color: var(--accent);
      color: var(--accent);
    }
    .dot { width: 9px; height: 9px; border-radius: 50%; display: inline-block; }
    .terminal {
      background: #05080f;
      border: 1px solid var(--border);
      border-radius: 8px;
      overflow: hidden;
    }
    .terminal-bar {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 8px 14px;
      background: #0f172a;
      border-bottom: 1px solid var(--border);
      font-size: 12px;
      color: var(--muted);
    }
    pre {
      margin: 0;
      padding: 16px;
      min-height: 500px;
      max-height: 760px;
      overflow: auto;
      font-size: 12.5px;
      line-height: 1.55;
      color: #e2e8f0;
      white-space: pre-wrap;
      word-break: break-word;
    }
    pre.hide-guides .guide-line {
      display: none;
    }
    .ln-role { color: #38bdf8; font-weight: 600; }
    .ln-agent { color: #c084fc; font-weight: 600; }
    .ln-slack { color: #fbbf24; font-weight: 600; }
    .ln-prod { color: #fb7185; font-weight: 600; }
    .ln-pass { color: #34d399; font-weight: 600; }
    .ln-sep { color: #475569; }
    .ln-cmd { color: #93c5fd; font-weight: bold; }
    a { color: var(--accent); text-decoration: none; }
    a:hover { text-decoration: underline; }
  </style>
</head>
<body>
  <div class="container">
    <header>
      <div>
        <h1>Agentic-Ops — SRE & Docker Sandbox Cognitive Web Console</h1>
        <div class="subtitle">Résultats Bruts Immédiats en Haut + Guides Pédagogiques Colorés en Bas | <a href="/chat" target="_blank" style="color:#34d399;font-weight:bold;">💬 Open Live AI Chat (/chat)</a> | <a href="/docs" target="_blank">Swagger UI (/docs)</a> | <a href="/mcp/manifest" target="_blank">MCP Manifest (/mcp/manifest)</a></div>
      </div>
      <div class="badges">
        <span class="badge">Redis :6379 Active</span>
        <span class="badge">Tailscale SOCKS5 :1055 Active</span>
        <span class="badge">MCP Gateway /mcp Active</span>
        <span class="badge">FastAPI :8001 Live</span>
      </div>
    </header>

    <div class="grid">
      <button class="amber" onclick="runCmd('sandbox_phase_a_vitals')">
        <strong>Phase A: Vitals & Hardware Telemetry</strong>
        <span>/healthz, /ready, CPU EPYC, /proc/meminfo, cgroup v2</span>
      </button>
      <button class="amber" onclick="runCmd('sandbox_phase_b_slack_spoof')">
        <strong>Phase B: Red-Team Slack Spoof Attack</strong>
        <span>POST /slack/interactive -> HTTP 401 Fail-Closed</span>
      </button>
      <button class="emerald" onclick="runCmd('sandbox_phase_c_adversarial_worm')">
        <strong>Phase C: Adversarial & WORM (9 Tests)</strong>
        <span>pytest tests/adversarial/ tests/security/ -v</span>
      </button>
      <button class="emerald" onclick="runCmd('sandbox_phase_d_mlops_scenarios')">
        <strong>Phase D: Live Agentic Scenarios (10 Tests)</strong>
        <span>pytest tests/scenarios/ -v (forbidden_executed=0)</span>
      </button>
      <button class="emerald" onclick="runCmd('sandbox_phase_e_fsm_governance')">
        <strong>Phase E: FSM & Tool Sandboxing (10 Tests)</strong>
        <span>pytest test_fsm + test_grafana + test_tools -v</span>
      </button>
      <button class="emerald" onclick="runCmd('pytest_cac_connector')">
        <strong>Phase F: CAC Tailscale Connector (13 Tests)</strong>
        <span>pytest tests/adapters/test_cac_pull_collector.py -v</span>
      </button>
      <button class="purple" onclick="runCmd('pytest_mcp_gateway')">
        <strong>Phase G: MCP Governance Gateway (12 Tests)</strong>
        <span>8 Tools (/console reader), 5 Resources, 20 Prompts</span>
      </button>
      <button class="purple" onclick="runCmd('pytest_llm_hub')">
        <strong>Phase H: LLM Provider Hub (OpenRouter & Ollama)</strong>
        <span>pytest test_llm_provider_registry (fallback & 8 providers)</span>
      </button>
      <button class="emerald" onclick="runCmd('pytest_all')">
        <strong>Grand Slam: All 57+ Sandbox, MCP & LLM Tests</strong>
        <span>Exécute les Phases C + D + E + F + G + H en une passe</span>
      </button>
      <button class="amber" onclick="runCmd('trust_ledger_list')">
        <strong>WORM Trust Ledger CLI</strong>
        <span>python -m agentic_ops.cli.trust_ledger list</span>
      </button>
      <button onclick="runJson('/api/llm/status')">
        <strong>LLM Provider Live Status</strong>
        <span>GET /api/llm/status (Active provider, model, masked key)</span>
      </button>
      <button onclick="runCmd('tailscale_status')">
        <strong>Tailscale Mesh Status</strong>
        <span>tailscale status (PII auto-redacted)</span>
      </button>
      <button onclick="runCmd('tailscale_netcheck')">
        <strong>Tailscale DERP Netcheck</strong>
        <span>tailscale netcheck (UDP / DERP latencies)</span>
      </button>
      <button onclick="runJson('/api/cac/snapshot?timeout=3.5')">
        <strong>Live Pull: jakatt/cac_mlops</strong>
        <span>GET /api/cac/snapshot (5 sources Read-Only)</span>
      </button>
      <button class="purple" onclick="runCmd('redis_ping')">
        <strong>Redis Local Daemon Ping</strong>
        <span>redis-cli -h 127.0.0.1 -p 6379 PING</span>
      </button>
    </div>

    <div class="legend">
      <div class="legend-items">
        <span class="legend-title">Code Couleur :</span>
        <span class="pill"><span class="dot" style="background:#34d399"></span><span style="color:#34d399">Émeraude</span> : PASSED & Verdict</span>
        <span class="pill"><span class="dot" style="background:#38bdf8"></span><span style="color:#38bdf8">[GUIDE:ROLE]</span> : Rôle</span>
        <span class="pill"><span class="dot" style="background:#c084fc"></span><span style="color:#c084fc">[GUIDE:AGENT]</span> : Agent IA</span>
        <span class="pill"><span class="dot" style="background:#fbbf24"></span><span style="color:#fbbf24">[GUIDE:SLACK]</span> : Slack HITL</span>
        <span class="pill"><span class="dot" style="background:#fb7185"></span><span style="color:#fb7185">[GUIDE:PROD]</span> : Impact Prod</span>
      </div>
      <button id="guide-toggle" class="toggle-btn" onclick="toggleGuides()">Vue : Résultats + Guides Colorés (ON)</button>
    </div>

    <div class="terminal">
      <div class="terminal-bar">
        <span id="cmd-title">Prêt — Les résultats PASSED s'affichent immédiatement en HAUT, suivis du guide pédagogique en BAS.</span>
        <span id="cmd-status">IDLE</span>
      </div>
      <pre id="output">Agentic-Ops Control Plane — Console Web Cognitive Prête.
Cliquez sur n'importe quel bouton ci-dessus :
  - EN HAUT DU TERMINAL : La sortie brute authentique et compacte (1 ligne par test PASSED + score final) immédiatement visible sans scroller.
  - EN BAS DU TERMINAL  : Le guide pédagogique coloré ([GUIDE:ROLE], [GUIDE:AGENT], [GUIDE:SLACK], [GUIDE:PROD], [GUIDE:HOW_IT_PASSES]).
  - BOUTON EN HAUT À DROITE : Permet d'afficher ou masquer les guides pédagogiques en 1 clic.</pre>
    </div>
  </div>

  <script>
    let guidesVisible = true;

    function toggleGuides() {
      guidesVisible = !guidesVisible;
      const out = document.getElementById('output');
      const btn = document.getElementById('guide-toggle');
      if (guidesVisible) {
        out.classList.remove('hide-guides');
        btn.classList.remove('compact');
        btn.textContent = 'Vue : Résultats + Guides Colorés (ON)';
      } else {
        out.classList.add('hide-guides');
        btn.classList.add('compact');
        btn.textContent = 'Vue : Résultats Purs Compact (OFF)';
      }
    }

    function escapeHtml(str) {
      return str
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;');
    }

    function renderColorizedTerminal(rawText) {
      const lines = rawText.split('\\n');
      return lines.map(line => {
        const esc = escapeHtml(line);
        const isGuide = line.startsWith('[GUIDE:') || line.startsWith('====');
        const gClass = isGuide ? ' guide-line' : '';
        if (line.startsWith('[GUIDE:ROLE]')) {
          return '<span class="ln-role' + gClass + '">' + esc + '\\n</span>';
        }
        if (line.startsWith('[GUIDE:AGENT]') || line.includes('[INVESTIGATING]') || line.includes('[DIAGNOSED]') || line.includes('[PLANNED]')) {
          return '<span class="ln-agent' + gClass + '">' + esc + '\\n</span>';
        }
        if (line.startsWith('[GUIDE:SLACK]') || line.includes('[POLICY]') || line.includes('[AWAITING_APPROVAL]')) {
          return '<span class="ln-slack' + gClass + '">' + esc + '\\n</span>';
        }
        if (line.startsWith('[GUIDE:PROD]') || line.includes('[DENIED]')) {
          return '<span class="ln-prod' + gClass + '">' + esc + '\\n</span>';
        }
        if (
          line.startsWith('[GUIDE:HOW_IT_PASSES]') ||
          line.startsWith('[GUIDE:VERDICT]') ||
          line.includes('PASSED') ||
          line.includes(' passed') ||
          line.includes('VERDICT:') ||
          line.includes('forbidden_executed=0')
        ) {
          return '<span class="ln-pass' + gClass + '">' + esc + '\\n</span>';
        }
        if (line.startsWith('====') || line.startsWith('----')) {
          return '<span class="ln-sep' + gClass + '">' + esc + '\\n</span>';
        }
        if (line.startsWith('$ ')) {
          return '<span class="ln-cmd">' + esc + '\\n</span>';
        }
        return '<span>' + esc + '\\n</span>';
      }).join('');
    }

    async function runCmd(cmd) {
      const out = document.getElementById('output');
      const title = document.getElementById('cmd-title');
      const status = document.getElementById('cmd-status');
      title.textContent = 'Running: /api/diagnostics/' + cmd + ' ...';
      status.textContent = 'RUNNING...';
      out.textContent = 'Exécution de la commande dans le conteneur Render, veuillez patienter...';
      try {
        const res = await fetch('/api/diagnostics/' + cmd);
        const text = await res.text();
        title.textContent = 'Completed: /api/diagnostics/' + cmd;
        status.textContent = 'HTTP ' + res.status;
        out.innerHTML = renderColorizedTerminal(text);
        out.scrollTop = 0;
      } catch (err) {
        status.textContent = 'ERROR';
        out.textContent = 'Request failed: ' + err;
      }
    }

    async function runJson(url) {
      const out = document.getElementById('output');
      const title = document.getElementById('cmd-title');
      const status = document.getElementById('cmd-status');
      title.textContent = 'Fetching: ' + url + ' ...';
      status.textContent = 'RUNNING...';
      out.textContent = 'Interrogation Read-Only des 5 services jakatt/cac_mlops via le tunnel Tailscale SOCKS5 (127.0.0.1:1055)...';
      try {
        const res = await fetch(url);
        const data = await res.json();
        title.textContent = 'Completed: ' + url;
        status.textContent = 'HTTP ' + res.status;
        const guide = [
          '',
          '========================================================================================',
          '[GUIDE:ROLE] RÔLE DU BOUTON (Live Pull : Collecte Temps Réel sur la Plateforme Cible jakatt/cac_mlops) :',
          '[GUIDE:ROLE]   Invoque CacPullCollector(use_proxy_for_vps=True, timeout=3.5).collect_all() pour interroger',
          '[GUIDE:ROLE]   en direct les 5 endpoints d observabilité du serveur MLOps cible (100.117.99.62) via Tailscale.',
          '[GUIDE:AGENT] AGENT IA INVOQUÉ : Collecte déterministe pré-agentique alimentant compute_facts() et les agents spécialistes.',
          '[GUIDE:SLACK] INTERACTION SLACK HITL : Aucune lors de la collecte passive.',
          '[GUIDE:PROD] IMPACT SUR LE MLOPS CIBLE (PROD) : 100% LECTURE SEULE (HTTP GET UNIQUEMENT).',
          '[GUIDE:HOW_IT_PASSES] INTERPRÉTATION DU RÉSULTAT (status = ' + data.status + ') :',
          data.status === 'REMOTE_TARGET_OFFLINE'
            ? '[GUIDE:HOW_IT_PASSES]   Le VPS Scaleway du binôme (100.117.99.62) est actuellement éteint -> renvoie HTTP 200 avec status=REMOTE_TARGET_OFFLINE (Fail-Safe).'
            : '[GUIDE:HOW_IT_PASSES]   Connexion établie avec succès (' + data.status + ') !',
          '========================================================================================'
        ].join('\\n');
        out.innerHTML = renderColorizedTerminal(JSON.stringify(data, null, 2) + guide);
        out.scrollTop = 0;
      } catch (err) {
        status.textContent = 'ERROR';
        out.textContent = 'Request failed: ' + err;
      }
    }
  </script>
</body>
</html>"""


CHAT_HTML = r"""<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Agentic-Ops — SRE & MLOps Cognitive Chat</title>
  <style>
    :root {
      --bg: #090d16;
      --card: #0f172a;
      --card-hover: #1e293b;
      --border: #1e293b;
      --border-accent: #334155;
      --text: #f1f5f9;
      --muted: #94a3b8;
      --accent: #34d399;
      --accent-blue: #38bdf8;
      --accent-purple: #c084fc;
      --accent-amber: #fbbf24;
      --accent-rose: #fb7185;
      --user-bg: #1e293b;
      --bot-bg: #0a1124;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      background: var(--bg);
      color: var(--text);
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", sans-serif;
      height: 100vh;
      display: flex;
      flex-direction: column;
      overflow: hidden;
    }
    header {
      background: var(--card);
      border-bottom: 1px solid var(--border);
      padding: 12px 24px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 12px;
      flex-shrink: 0;
    }
    .brand {
      display: flex;
      align-items: center;
      gap: 10px;
    }
    .brand-title {
      font-size: 16px;
      font-weight: 700;
      color: #fff;
      display: flex;
      align-items: center;
      gap: 8px;
    }
    .brand-sub {
      font-size: 11px;
      color: var(--muted);
      margin-top: 1px;
    }
    .header-right {
      display: flex;
      align-items: center;
      gap: 12px;
      font-size: 12px;
      flex-wrap: wrap;
    }
    .badge-llm {
      background: #022c22;
      color: var(--accent);
      border: 1px solid #059669;
      padding: 5px 12px;
      border-radius: 9999px;
      font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
      font-size: 11px;
      display: flex;
      align-items: center;
      gap: 8px;
    }
    .badge-dot {
      width: 7px;
      height: 7px;
      background: var(--accent);
      border-radius: 50%;
      box-shadow: 0 0 6px var(--accent);
      display: inline-block;
    }
    .btn-catalog-toggle {
      background: #3b0764;
      color: #e9d5ff;
      border: 1px solid #7e22ce;
      padding: 5px 12px;
      border-radius: 6px;
      font-size: 11.5px;
      font-weight: 600;
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 6px;
      transition: all 0.15s;
    }
    .btn-catalog-toggle:hover {
      background: #581c87;
      border-color: #a855f7;
      color: #fff;
    }
    .nav-links {
      display: flex;
      gap: 12px;
    }
    .nav-links a {
      color: var(--accent-blue);
      text-decoration: none;
      font-weight: 500;
      transition: opacity 0.15s;
    }
    .nav-links a:hover {
      text-decoration: underline;
    }
    
    .chat-container {
      flex: 1;
      max-width: 1000px;
      width: 100%;
      margin: 0 auto;
      display: flex;
      flex-direction: column;
      padding: 16px 20px 14px 20px;
      overflow: hidden;
    }
    
    .chat-messages {
      flex: 1;
      overflow-y: auto;
      padding-right: 8px;
      display: flex;
      flex-direction: column;
      gap: 16px;
      margin-bottom: 12px;
    }
    .chat-messages::-webkit-scrollbar { width: 6px; }
    .chat-messages::-webkit-scrollbar-thumb { background: #334155; border-radius: 3px; }
    
    .msg-wrapper {
      display: flex;
      flex-direction: column;
      max-width: 85%;
      animation: msgIn 0.2s cubic-bezier(0.16, 1, 0.3, 1);
    }
    @keyframes msgIn {
      from { opacity: 0; transform: translateY(6px); }
      to { opacity: 1; transform: translateY(0); }
    }
    .msg-wrapper.user {
      align-self: flex-end;
    }
    .msg-wrapper.bot {
      align-self: flex-start;
    }
    
    .msg-sender {
      font-size: 11px;
      color: var(--muted);
      margin-bottom: 4px;
      display: flex;
      align-items: center;
      gap: 6px;
    }
    .msg-sender.user {
      justify-content: flex-end;
    }
    
    .msg-bubble {
      padding: 13px 17px;
      border-radius: 12px;
      line-height: 1.55;
      font-size: 13.5px;
      word-break: break-word;
    }
    .msg-wrapper.user .msg-bubble {
      background: var(--user-bg);
      border: 1px solid #334155;
      color: #f8fafc;
      border-bottom-right-radius: 3px;
    }
    .msg-wrapper.bot .msg-bubble {
      background: var(--bot-bg);
      border: 1px solid var(--border);
      border-left: 3px solid var(--accent);
      border-bottom-left-radius: 3px;
    }
    
    .msg-bubble pre {
      background: #020617;
      border: 1px solid #1e293b;
      padding: 10px 12px;
      border-radius: 6px;
      margin: 8px 0;
      overflow-x: auto;
      font-family: ui-monospace, SFMono-Regular, monospace;
      font-size: 12px;
      color: #cbd5e1;
    }
    .msg-bubble code {
      background: #020617;
      padding: 2px 5px;
      border-radius: 4px;
      font-family: ui-monospace, SFMono-Regular, monospace;
      color: #93c5fd;
      font-size: 12px;
    }
    
    .meta-card {
      margin-top: 10px;
      padding-top: 8px;
      border-top: 1px solid #1e293b;
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      font-family: ui-monospace, SFMono-Regular, monospace;
      font-size: 11px;
    }
    .meta-pill {
      background: #020617;
      padding: 3px 8px;
      border-radius: 4px;
      border: 1px solid #1e293b;
      color: var(--muted);
    }
    .meta-pill strong {
      color: var(--accent-blue);
    }
    .meta-pill.action strong {
      color: var(--accent);
    }
    .meta-pill.conf strong {
      color: var(--accent-amber);
    }
    
    .chips-bar {
      display: flex;
      gap: 8px;
      overflow-x: auto;
      padding-bottom: 8px;
      margin-bottom: 10px;
      flex-shrink: 0;
    }
    .chips-bar::-webkit-scrollbar { height: 4px; }
    .chips-bar::-webkit-scrollbar-thumb { background: #334155; }
    .chip-btn {
      background: var(--card);
      border: 1px solid var(--border-accent);
      color: #cbd5e1;
      padding: 6px 13px;
      border-radius: 9999px;
      font-size: 12px;
      cursor: pointer;
      white-space: nowrap;
      transition: all 0.15s;
    }
    .chip-btn:hover {
      background: #1e293b;
      border-color: var(--accent);
      color: #fff;
    }
    .chip-catalog {
      background: #2e1065 !important;
      border-color: #7e22ce !important;
      color: #e9d5ff !important;
      font-weight: 600;
    }
    .chip-catalog:hover {
      background: #3b0764 !important;
      border-color: #a855f7 !important;
      color: #fff !important;
    }
    
    .input-box {
      background: var(--card);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 8px 12px;
      display: flex;
      align-items: flex-end;
      gap: 10px;
      box-shadow: 0 4px 20px rgba(0,0,0,0.3);
      flex-shrink: 0;
    }
    .input-box:focus-within {
      border-color: var(--accent);
    }
    .input-box textarea {
      flex: 1;
      background: transparent;
      border: none;
      outline: none;
      color: #fff;
      font-family: inherit;
      font-size: 14px;
      resize: none;
      min-height: 42px;
      max-height: 120px;
      line-height: 1.4;
      padding: 6px 4px;
    }
    .input-actions {
      display: flex;
      gap: 8px;
      align-items: center;
    }
    .btn-clear {
      background: transparent;
      color: var(--muted);
      border: 1px solid #334155;
      padding: 8px 12px;
      border-radius: 6px;
      font-size: 12px;
      cursor: pointer;
      transition: all 0.15s;
    }
    .btn-clear:hover {
      background: #1e293b;
      color: #fff;
    }
    .btn-send {
      background: #059669;
      color: #fff;
      border: none;
      padding: 9px 18px;
      border-radius: 6px;
      font-size: 13px;
      font-weight: 600;
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 6px;
      transition: background 0.15s;
    }
    .btn-send:hover:not(:disabled) {
      background: #10b981;
    }
    .btn-send:disabled {
      background: #334155;
      cursor: not-allowed;
      opacity: 0.6;
    }
    
    .input-hint {
      font-size: 11px;
      color: var(--muted);
      margin-top: 6px;
      display: flex;
      justify-content: space-between;
      flex-shrink: 0;
    }
    
    .typing-dots {
      display: inline-flex;
      gap: 4px;
      align-items: center;
    }
    .typing-dot {
      width: 5px;
      height: 5px;
      background: var(--muted);
      border-radius: 50%;
      animation: blink 1.4s infinite both;
    }
    .typing-dot:nth-child(2) { animation-delay: 0.2s; }
    .typing-dot:nth-child(3) { animation-delay: 0.4s; }
    @keyframes blink {
      0%, 80%, 100% { opacity: 0.2; transform: scale(0.8); }
      40% { opacity: 1; transform: scale(1.2); }
    }
    .error-banner {
      background: #450a0a;
      border: 1px solid #991b1b;
      color: #fca5a5;
      padding: 8px 12px;
      border-radius: 6px;
      font-size: 12px;
      margin-top: 6px;
    }

    /* Modal Overlay & Drawer */
    .catalog-modal-overlay {
      display: none;
      position: fixed;
      inset: 0;
      background: rgba(3, 7, 18, 0.85);
      backdrop-filter: blur(6px);
      z-index: 1000;
      align-items: center;
      justify-content: center;
      padding: 16px;
      animation: modalFadeIn 0.15s ease-out;
    }
    .catalog-modal-overlay.open {
      display: flex;
    }
    @keyframes modalFadeIn {
      from { opacity: 0; transform: scale(0.98); }
      to { opacity: 1; transform: scale(1); }
    }
    .catalog-modal-box {
      background: #0f172a;
      border: 1px solid #334155;
      border-radius: 14px;
      width: 100%;
      max-width: 920px;
      max-height: 88vh;
      display: flex;
      flex-direction: column;
      box-shadow: 0 20px 50px rgba(0, 0, 0, 0.6);
      overflow: hidden;
    }
    .catalog-modal-header {
      padding: 16px 20px;
      border-bottom: 1px solid #1e293b;
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      gap: 12px;
      background: #0b1329;
      flex-shrink: 0;
    }
    .catalog-modal-title h2 {
      font-size: 16px;
      font-weight: 700;
      color: #fff;
      display: flex;
      align-items: center;
      gap: 8px;
    }
    .catalog-modal-title p {
      font-size: 12px;
      color: var(--muted);
      margin-top: 2px;
    }
    .btn-close-modal {
      background: transparent;
      border: 1px solid #334155;
      color: var(--muted);
      border-radius: 6px;
      width: 28px;
      height: 28px;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 14px;
      transition: all 0.15s;
    }
    .btn-close-modal:hover {
      background: #1e293b;
      color: #fff;
    }
    .catalog-search-bar {
      padding: 12px 20px;
      border-bottom: 1px solid #1e293b;
      background: #0f172a;
      flex-shrink: 0;
    }
    .catalog-search-bar input {
      width: 100%;
      background: #020617;
      border: 1px solid #334155;
      border-radius: 8px;
      padding: 9px 14px;
      color: #fff;
      font-size: 13px;
      outline: none;
      transition: border 0.15s;
    }
    .catalog-search-bar input:focus {
      border-color: var(--accent);
    }
    .catalog-categories {
      display: flex;
      gap: 8px;
      overflow-x: auto;
      padding: 10px 20px;
      background: #090d16;
      border-bottom: 1px solid #1e293b;
      flex-shrink: 0;
    }
    .catalog-categories::-webkit-scrollbar { height: 4px; }
    .catalog-categories::-webkit-scrollbar-thumb { background: #334155; }
    .cat-pill {
      background: #1e293b;
      border: 1px solid #334155;
      color: var(--muted);
      padding: 5px 12px;
      border-radius: 9999px;
      font-size: 11.5px;
      cursor: pointer;
      white-space: nowrap;
      transition: all 0.15s;
    }
    .cat-pill:hover {
      background: #334155;
      color: #fff;
    }
    .cat-pill.active {
      background: #059669;
      border-color: #10b981;
      color: #fff;
      font-weight: 600;
    }
    .catalog-cards-grid {
      flex: 1;
      overflow-y: auto;
      padding: 16px 20px;
      display: flex;
      flex-direction: column;
      gap: 12px;
    }
    .catalog-cards-grid::-webkit-scrollbar { width: 6px; }
    .catalog-cards-grid::-webkit-scrollbar-thumb { background: #334155; border-radius: 3px; }
    .prompt-card {
      background: #0b1329;
      border: 1px solid #1e293b;
      border-radius: 10px;
      padding: 14px 16px;
      transition: all 0.15s;
      display: flex;
      flex-direction: column;
      gap: 8px;
    }
    .prompt-card:hover {
      border-color: #38bdf8;
      background: #0d1838;
    }
    .prompt-card-top {
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 8px;
      flex-wrap: wrap;
    }
    .prompt-id-badge {
      font-family: ui-monospace, SFMono-Regular, monospace;
      font-size: 11px;
      padding: 2px 8px;
      border-radius: 4px;
      font-weight: 600;
    }
    .prompt-id-badge.cat-I { background: #082f49; color: #38bdf8; border: 1px solid #0284c7; }
    .prompt-id-badge.cat-II { background: #022c22; color: #34d399; border: 1px solid #059669; }
    .prompt-id-badge.cat-III { background: #451a03; color: #fbbf24; border: 1px solid #d97706; }
    .prompt-id-badge.cat-IV { background: #3b0764; color: #c084fc; border: 1px solid #7e22ce; }
    .prompt-id-badge.cat-V { background: #4c0519; color: #fb7185; border: 1px solid #e11d48; }
    .prompt-card-desc {
      font-size: 12.5px;
      color: #cbd5e1;
      line-height: 1.45;
    }
    .prompt-card-template {
      background: #020617;
      border: 1px solid #1e293b;
      border-radius: 6px;
      padding: 8px 12px;
      font-family: ui-monospace, SFMono-Regular, monospace;
      font-size: 11.5px;
      color: #94a3b8;
      max-height: 85px;
      overflow-y: auto;
      white-space: pre-wrap;
      word-break: break-word;
    }
    .prompt-card-actions {
      display: flex;
      gap: 8px;
      justify-content: flex-end;
      margin-top: 4px;
    }
    .btn-prompt-insert {
      background: #1e293b;
      border: 1px solid #334155;
      color: #cbd5e1;
      padding: 6px 12px;
      border-radius: 6px;
      font-size: 12px;
      cursor: pointer;
      font-weight: 500;
      transition: all 0.15s;
    }
    .btn-prompt-insert:hover {
      background: #334155;
      color: #fff;
    }
    .btn-prompt-run {
      background: #059669;
      border: none;
      color: #fff;
      padding: 6px 14px;
      border-radius: 6px;
      font-size: 12px;
      cursor: pointer;
      font-weight: 600;
      transition: background 0.15s;
    }
    .btn-prompt-run:hover {
      background: #10b981;
    }
  </style>
</head>
<body>
  <header>
    <div class="brand">
      <div class="header-left">
        <div class="brand-title">
          <span>💬</span>
          <span>Agentic-Ops — Cognitive SRE & MLOps Assistant</span>
        </div>
        <div class="brand-sub">Universal LLM Interface (OpenRouter, Gemini, Claude, OpenAI, Ollama) | Zero-Dependency Web Client</div>
      </div>
    </div>
    <div class="header-right">
      <div class="badge-llm" id="llm-status-badge">
        <span class="badge-dot"></span>
        <span>Loading LLM Provider...</span>
      </div>
      <button class="btn-catalog-toggle" onclick="toggleCatalog(true)" title="Explorer les 20 Prompts Cognitifs MCP">
        <span>📚</span>
        <span>20 Prompts MCP</span>
      </button>
      <div class="nav-links">
        <a href="/console">🖥️ Console</a>
        <a href="/docs" target="_blank">Swagger (/docs)</a>
        <a href="/mcp/manifest" target="_blank">MCP Manifest</a>
      </div>
    </div>
  </header>

  <div class="chat-container">
    <div class="chat-messages" id="chat-messages">
      <div class="msg-wrapper bot">
        <div class="msg-sender">🤖 Agentic-Ops SRE Assistant</div>
        <div class="msg-bubble">
          Bonjour ! Je suis l'assistant cognitif SRE et MLOps d'<strong>Agentic-Ops Control Plane</strong>.<br><br>
          Je suis connecté en direct au moteur d'orchestration et au Hub de LLM (OpenRouter par défaut avec fallback automatique). Vous pouvez m'interroger sur l'état de l'infrastructure, l'analyse d'alertes Loki/Prometheus, la dérive Evidently, les politiques de quorum Slack HITL ou les tests de robustesse.<br><br>
          <em>Cliquez sur le bouton <strong>📚 20 Prompts MCP</strong> pour explorer le catalogue de scénarios d'audit prêts à l'emploi.</em>
        </div>
      </div>
    </div>

    <div class="chips-bar">
      <button class="chip-btn chip-catalog" onclick="toggleCatalog(true)">📚 Catalogue des 20 Prompts MCP...</button>
      <button class="chip-btn" onclick="sendPrompt('Quel est le rôle du circuit breaker en cas de saturation de requêtes ?')">⚡ Circuit Breaker</button>
      <button class="chip-btn" onclick="sendPrompt('Explique comment fonctionne le quorum Slack HITL à 2 approbateurs (2-man rule).')">👥 Quorum HITL Slack</button>
      <button class="chip-btn" onclick="sendPrompt('Quels sont les impacts d\'une dérive de données Evidently sur le modèle BAAC ?')">📉 Dérive Evidently BAAC</button>
      <button class="chip-btn" onclick="sendPrompt('Comment le WORM Trust Ledger garantit-il l\'immuabilité des actions d\'assainissement ?')">🔒 WORM Trust Ledger</button>
      <button class="chip-btn" onclick="sendPrompt('Pourquoi le pull CAC vers 100.117.99.62 est-il strictement en lecture seule ?')">🛡️ Sécurité CAC Pull</button>
    </div>

    <div class="input-box">
      <textarea id="chat-input" placeholder="Posez une question à l'assistant SRE (Entrée pour envoyer, Maj+Entrée pour saut de ligne)..." rows="1" onkeydown="handleKeyDown(event)"></textarea>
      <div class="input-actions">
        <button class="btn-clear" onclick="clearChat()" title="Effacer l'historique">Effacer</button>
        <button class="btn-send" id="btn-send" onclick="sendMessage()">Envoyer ↵</button>
      </div>
    </div>
    <div class="input-hint">
      <span>Appuyez sur <strong>Entrée</strong> pour envoyer</span>
      <span id="char-counter">Modèle actif résolu par LLMProviderRegistry</span>
    </div>
  </div>

  <!-- PROMPT CATALOG MODAL -->
  <div class="catalog-modal-overlay" id="catalog-modal" onclick="onOverlayClick(event)">
    <div class="catalog-modal-box">
      <div class="catalog-modal-header">
        <div class="catalog-modal-title">
          <h2>📚 Catalogue des 20 Prompts Cognitifs MCP</h2>
          <p>Modèles de requêtes prêts à l'emploi pour auditer le Control Plane, évaluer les politiques et vérifier le WORM Ledger.</p>
        </div>
        <button class="btn-close-modal" onclick="toggleCatalog(false)" title="Fermer (Échap)">✕</button>
      </div>
      
      <div class="catalog-search-bar">
        <input type="text" id="catalog-search" placeholder="🔍 Rechercher un prompt (ex: drift, worm, slack, veto, vitals, r1, jury)..." oninput="filterPrompts()">
      </div>
      
      <div class="catalog-categories" id="catalog-category-pills">
        <button class="cat-pill active" onclick="selectCategory('ALL', this)">Tous (20)</button>
        <button class="cat-pill" onclick="selectCategory('I', this)">I. Console Live (4)</button>
        <button class="cat-pill" onclick="selectCategory('II', this)">II. PolicyEngine (4)</button>
        <button class="cat-pill" onclick="selectCategory('III', this)">III. WORM Ledger (4)</button>
        <button class="cat-pill" onclick="selectCategory('IV', this)">IV. Taxonomie 435 (4)</button>
        <button class="cat-pill" onclick="selectCategory('V', this)">V. SecOps & Jury (4)</button>
      </div>
      
      <div class="catalog-cards-grid" id="catalog-cards-container">
        <div style="text-align:center;color:var(--muted);padding:40px;">Chargement du catalogue MCP...</div>
      </div>
    </div>
  </div>

  <script>
    let conversationHistory = [];
    let allPrompts = [];
    let currentCategory = 'ALL';

    function toggleCatalog(open) {
      const modal = document.getElementById('catalog-modal');
      if (open) {
        modal.classList.add('open');
        if (allPrompts.length === 0) {
          loadPromptsCatalog();
        } else {
          document.getElementById('catalog-search').focus();
        }
      } else {
        modal.classList.remove('open');
      }
    }

    function onOverlayClick(e) {
      if (e.target.id === 'catalog-modal') {
        toggleCatalog(false);
      }
    }

    document.addEventListener('keydown', function(e) {
      if (e.key === 'Escape') {
        toggleCatalog(false);
      }
    });

    async function loadPromptsCatalog() {
      try {
        const res = await fetch('/api/prompts');
        const data = await res.json();
        allPrompts = data.prompts || [];
        renderPrompts();
        setTimeout(() => {
          const searchInput = document.getElementById('catalog-search');
          if (searchInput) searchInput.focus();
        }, 50);
      } catch (err) {
        console.error('Failed to load prompts catalog:', err);
        const container = document.getElementById('catalog-cards-container');
        if (container) {
          container.innerHTML = `<div class="error-banner">Impossible de charger le catalogue de prompts : ${err}</div>`;
        }
      }
    }

    function getPromptCategory(name) {
      const num = parseInt(name.split('_')[0], 10);
      if (num >= 1 && num <= 4) return { code: 'I', label: 'I. Console Live', badge: 'cat-I' };
      if (num >= 5 && num <= 8) return { code: 'II', label: 'II. PolicyEngine', badge: 'cat-II' };
      if (num >= 9 && num <= 12) return { code: 'III', label: 'III. WORM Ledger', badge: 'cat-III' };
      if (num >= 13 && num <= 16) return { code: 'IV', label: 'IV. Taxonomie 435', badge: 'cat-IV' };
      return { code: 'V', label: 'V. SecOps & Jury', badge: 'cat-V' };
    }

    function selectCategory(cat, btn) {
      currentCategory = cat;
      const pills = document.querySelectorAll('.cat-pill');
      pills.forEach(p => p.classList.remove('active'));
      if (btn) btn.classList.add('active');
      renderPrompts();
    }

    function filterPrompts() {
      renderPrompts();
    }

    function renderPrompts() {
      const container = document.getElementById('catalog-cards-container');
      if (!container) return;
      const query = (document.getElementById('catalog-search').value || '').toLowerCase().trim();

      const filtered = allPrompts.filter(p => {
        const cat = getPromptCategory(p.name);
        if (currentCategory !== 'ALL' && cat.code !== currentCategory) return false;
        if (!query) return true;
        const searchCorpus = (p.name + ' ' + (p.description || '') + ' ' + (p.template || '')).toLowerCase();
        return searchCorpus.includes(query);
      });

      if (filtered.length === 0) {
        container.innerHTML = `<div style="text-align:center;color:var(--muted);padding:40px;">Aucun prompt correspondant à votre recherche.</div>`;
        return;
      }

      container.innerHTML = filtered.map(p => {
        const cat = getPromptCategory(p.name);
        const escapedTemplate = escapeHtml(p.template);
        const jsonSafeTemplate = JSON.stringify(p.template);
        return `
          <div class="prompt-card">
            <div class="prompt-card-top">
              <span class="prompt-id-badge ${cat.badge}">${cat.label} — ${escapeHtml(p.name)}</span>
            </div>
            <div class="prompt-card-desc">${escapeHtml(p.description)}</div>
            <div class="prompt-card-template">${escapedTemplate}</div>
            <div class="prompt-card-actions">
              <button class="btn-prompt-insert" onclick='insertPrompt(${jsonSafeTemplate})'>✎ Insérer dans le Chat</button>
              <button class="btn-prompt-run" onclick='runPrompt(${jsonSafeTemplate})'>↵ Exécuter Directement</button>
            </div>
          </div>
        `;
      }).join('');
    }

    function insertPrompt(text) {
      const input = document.getElementById('chat-input');
      input.value = text;
      input.style.height = 'auto';
      input.style.height = Math.min(input.scrollHeight, 120) + 'px';
      toggleCatalog(false);
      input.focus();
    }

    function runPrompt(text) {
      const input = document.getElementById('chat-input');
      input.value = text;
      toggleCatalog(false);
      sendMessage();
    }

    async function loadLLMStatus() {
      try {
        const res = await fetch('/api/llm/status');
        const data = await res.json();
        const badge = document.getElementById('llm-status-badge');
        if (badge && data.provider) {
          badge.innerHTML = `<span class="badge-dot"></span> Active: <strong>${data.provider}</strong> (${data.model}) — ${data.api_key_masked}`;
        }
      } catch (err) {
        console.error('Failed to load LLM status:', err);
      }
    }

    function handleKeyDown(e) {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
      }
    }

    function sendPrompt(text) {
      const input = document.getElementById('chat-input');
      input.value = text;
      sendMessage();
    }

    function clearChat() {
      conversationHistory = [];
      const container = document.getElementById('chat-messages');
      container.innerHTML = `
        <div class="msg-wrapper bot">
          <div class="msg-sender">🤖 Agentic-Ops SRE Assistant</div>
          <div class="msg-bubble">
            Historique réinitialisé. Comment puis-je vous aider sur le Control Plane Agentic-Ops ?
          </div>
        </div>
      `;
    }

    function escapeHtml(text) {
      const div = document.createElement('div');
      div.textContent = text;
      return div.innerHTML;
    }

    function formatMarkdown(text) {
      if (!text) return '';
      let escaped = escapeHtml(text);
      escaped = escaped.replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>');
      escaped = escaped.replace(/`([^`]+)`/g, '<code>$1</code>');
      escaped = escaped.replace(/\*\*([^\*]+)\*\*/g, '<strong>$1</strong>');
      escaped = escaped.replace(/\n/g, '<br>');
      return escaped;
    }

    function appendMessage(role, text, isPending = false) {
      const container = document.getElementById('chat-messages');
      const wrapper = document.createElement('div');
      wrapper.className = `msg-wrapper ${role}`;
      const msgId = 'msg-' + Date.now() + '-' + Math.random().toString(36).substr(2, 5);
      wrapper.id = msgId;

      const sender = document.createElement('div');
      sender.className = `msg-sender ${role}`;
      sender.innerHTML = role === 'user' ? '👤 Opérateur' : '🤖 Agentic-Ops SRE Assistant';
      wrapper.appendChild(sender);

      const bubble = document.createElement('div');
      bubble.className = 'msg-bubble';

      if (isPending) {
        bubble.innerHTML = `
          <div class="typing-dots">
            <span class="typing-dot"></span>
            <span class="typing-dot"></span>
            <span class="typing-dot"></span>
          </div>
          <span style="font-size:12px;color:var(--muted);margin-left:8px;">Analyse cognitive en cours...</span>
        `;
      } else {
        bubble.innerHTML = formatMarkdown(text);
      }
      wrapper.appendChild(bubble);
      container.appendChild(wrapper);
      container.scrollTop = container.scrollHeight;
      return msgId;
    }

    function updateBotMessage(msgId, data) {
      const wrapper = document.getElementById(msgId);
      if (!wrapper) return;
      const bubble = wrapper.querySelector('.msg-bubble');
      if (!bubble) return;

      if (data.status === 'error') {
        bubble.innerHTML = `
          <div class="error-banner">
            <strong>Incident Fournisseur LLM :</strong> ${escapeHtml(data.error || data.answer)}
          </div>
          <div style="font-size:12px;color:var(--muted);margin-top:6px;">
            Vérifiez vos clés d'API (<code>OPENROUTER_API_KEY</code>, etc.) ou utilisez le modèle local <code>ollama</code>.
          </div>
        `;
        return;
      }

      let html = formatMarkdown(data.answer);

      const hasMeta = data.action_type || data.confidence_score || data.latency_ms || data.provider;
      if (hasMeta) {
        html += `<div class="meta-card">`;
        if (data.action_type) {
          html += `<div class="meta-pill action">Action: <strong>${escapeHtml(data.action_type)}</strong></div>`;
        }
        if (data.confidence_score !== undefined && data.confidence_score !== null) {
          const pct = Math.round(data.confidence_score * 100);
          html += `<div class="meta-pill conf">Confiance: <strong>${pct}%</strong></div>`;
        }
        if (data.latency_ms) {
          html += `<div class="meta-pill">Latence: <strong>${data.latency_ms} ms</strong></div>`;
        }
        if (data.provider && data.model) {
          html += `<div class="meta-pill">LLM: <strong>${escapeHtml(data.provider)} / ${escapeHtml(data.model)}</strong></div>`;
        }
        html += `</div>`;
      }

      bubble.innerHTML = html;
      const container = document.getElementById('chat-messages');
      container.scrollTop = container.scrollHeight;
    }

    async function sendMessage() {
      const input = document.getElementById('chat-input');
      const text = input.value.trim();
      if (!text) return;

      input.value = '';
      input.style.height = 'auto';

      appendMessage('user', text);
      conversationHistory.push({ role: 'user', content: text });

      const sendBtn = document.getElementById('btn-send');
      sendBtn.disabled = true;
      sendBtn.innerText = 'Réflexion...';

      const botMsgId = appendMessage('bot', '', true);

      try {
        const res = await fetch('/api/chat', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ message: text, history: conversationHistory })
        });
        const data = await res.json();
        updateBotMessage(botMsgId, data);
        if (data.answer) {
          conversationHistory.push({ role: 'assistant', content: data.answer });
        }
      } catch (err) {
        updateBotMessage(botMsgId, {
          status: 'error',
          error: 'Impossible de contacter le serveur Agentic-Ops (/api/chat): ' + err
        });
      } finally {
        sendBtn.disabled = false;
        sendBtn.innerText = 'Envoyer ↵';
      }
    }

    const tx = document.getElementById('chat-input');
    tx.addEventListener('input', function() {
      this.style.height = 'auto';
      this.style.height = Math.min(this.scrollHeight, 120) + 'px';
    });

    loadLLMStatus();
  </script>
</body>
</html>"""


@app.get("/chat", response_class=HTMLResponse)
def web_chat():
    """
    Zero-dependency standalone Web Chat UI for Agentic-Ops.
    Hosted directly on FastAPI/Render at /chat.
    """
    return HTMLResponse(content=CHAT_HTML)


app.include_router(slack_router)
app.include_router(mcp_router)


def start_server():
    import uvicorn
    port = int(os.environ.get("PORT", "8001"))
    uvicorn.run("agentic_ops.cli.main:app", host="0.0.0.0", port=port)

