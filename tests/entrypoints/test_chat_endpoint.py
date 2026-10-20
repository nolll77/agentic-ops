"""
Unit & Integration Tests for the Agentic-Ops Standalone Web Chat UI (/chat) and API (/api/chat).
Verifies:
1. GET /chat returns 200 HTML with dark-mode styling and UI components.
2. GET / metadata exposes web_chat and llm_chat endpoints.
3. POST /api/chat successfully executes conversation with mocked or active LLM adapter.
4. Error resilience: graceful error response when LLM adapter raises.
"""

from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
import pytest

from agentic_ops.cli.main import app
from agentic_ops.adapters.llm_protocol import _ChatResponse


client = TestClient(app)


def test_get_chat_ui_returns_200_html():
    """GET /chat must serve the standalone web chat HTML with zero external JS dependencies."""
    resp = client.get("/chat")
    assert resp.status_code == 200
    assert "text/html" in resp.headers["content-type"]
    html = resp.text
    assert "Agentic-Ops — SRE & MLOps Cognitive Chat" in html
    assert "llm-status-badge" in html
    assert "chat-messages" in html
    assert "btn-send" in html
    assert "/api/chat" in html
    assert "/api/llm/status" in html


def test_root_endpoint_includes_chat_urls():
    """GET / must list both /chat (UI) and /api/chat (JSON API) in endpoints."""
    resp = client.get("/")
    assert resp.status_code == 200
    data = resp.json()
    assert "endpoints" in data
    assert data["endpoints"]["web_chat"] == "/chat"
    assert data["endpoints"]["llm_chat"] == "/api/chat"


@patch("agentic_ops.adapters.llm_provider_registry.LLMProviderRegistry.build_adapter_from_env")
def test_post_api_chat_success(mock_build_adapter):
    """POST /api/chat returns structured answer, action_type, and latency."""
    mock_adapter = MagicMock()
    mock_adapter.complete.return_value = _ChatResponse(
        answer="Alerte Loki résolue : libération du volume /var/log effectuée.",
        action_type="quarantine",
        confidence_score=0.98,
        rationale="Espace disque critique < 5%",
    )
    mock_build_adapter.return_value = mock_adapter

    payload = {
        "message": "Que faire en cas d'alerte disque Loki ?",
        "history": [{"role": "user", "content": "Bonjour"}]
    }
    resp = client.post("/api/chat", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert "Alerte Loki résolue" in data["answer"]
    assert data["action_type"] == "quarantine"
    assert data["confidence_score"] == 0.98
    assert data["latency_ms"] is not None
    assert data["provider"] is not None


@patch("agentic_ops.adapters.llm_provider_registry.LLMProviderRegistry.build_adapter_from_env")
def test_post_api_chat_error_resilience(mock_build_adapter):
    """POST /api/chat must return a clean error JSON rather than 500 when LLM fails."""
    mock_adapter = MagicMock()
    mock_adapter.complete.side_effect = RuntimeError("OpenRouter 429 Too Many Requests")
    mock_build_adapter.return_value = mock_adapter

    payload = {
        "message": "Crash test"
    }
    resp = client.post("/api/chat", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "error"
    assert "Erreur de communication" in data["answer"]
    assert "429" in data["error"]


def test_get_prompts_catalog_api():
    """GET /api/prompts must return the 20 cognitive starter prompts catalog."""
    resp = client.get("/api/prompts")
    assert resp.status_code == 200
    data = resp.json()
    assert data["count"] == 20
    assert len(data["prompts"]) == 20
    names = {p["name"] for p in data["prompts"]}
    assert "01_console_grand_slam_audit" in names
    assert "05_policy_veto_corrupted_sensor" in names
    assert "09_worm_ledger_chain_verification" in names
    assert "13_taxonomy_deep_search_drift" in names
    assert "20_executive_jury_defense_briefing" in names


def test_get_chat_ui_contains_prompts_catalog_elements():
    """GET /chat must contain the catalog modal, search bar, category tabs, and API hook."""
    resp = client.get("/chat")
    assert resp.status_code == 200
    html = resp.text
    assert "catalog-modal" in html
    assert "btn-catalog-toggle" in html
    assert "chip-catalog" in html
    assert "catalog-search" in html
    assert "catalog-categories" in html
    assert "/api/prompts" in html


def test_get_llm_status_includes_roles_topology():
    """GET /api/llm/status must expose the cognitive multi-LLM roles topology."""
    resp = client.get("/api/llm/status")
    assert resp.status_code == 200
    data = resp.json()
    assert "roles_topology" in data
    roles = data["roles_topology"]
    assert set(roles.keys()) == {"remediation", "infra", "data", "model", "chat"}
    for role_name in ("remediation", "infra", "data", "model", "chat"):
        assert "provider" in roles[role_name]
        assert "model" in roles[role_name]
        assert "fallback_models" in roles[role_name]
        assert "is_specialized" in roles[role_name]
        assert "recommendation" in roles[role_name]


def test_get_mas_topology_endpoint():
    """GET /api/mas/topology must return the 11 components (5 cognitive + 6 deterministic)."""
    resp = client.get("/api/mas/topology")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert data["total_components"] == 11
    assert data["cognitive_count"] == 5
    assert data["deterministic_count"] == 6

    # Verify cognitive agents
    cog_ids = {a["id"] for a in data["cognitive_agents"]}
    assert cog_ids == {"remediation", "infra", "data", "model", "chat"}
    for agent in data["cognitive_agents"]:
        assert agent["type"] == "cognitive"
        assert "active_model" in agent
        assert "selection_rationale" in agent
        assert "input_contract" in agent
        assert "output_contract" in agent
        assert "promql_metric" in agent

    # Verify deterministic components
    det_ids = {d["id"] for d in data["deterministic_components"]}
    assert det_ids == {"circuit_breaker", "executor", "cac_collector", "slack_webhook", "agent_tools", "mcp_gateway"}
    for comp in data["deterministic_components"]:
        assert comp["type"] == "deterministic"
        if comp["id"] != "mcp_gateway":
            assert "0 Tokens" in comp["engine"]
        else:
            assert "Délégué" in comp["engine"]
        assert "isolation" in comp


def test_get_console_ui_contains_mas_inspector():
    """GET /console must serve the MAS Inspector modal, button, and client-side triggers."""
    resp = client.get("/console")
    assert resp.status_code == 200
    html = resp.text
    assert 'id="mas-modal"' in html
    assert 'openMasModal()' in html
    assert "Topologie MAS & Inspecteur des LLMs" in html
    assert "/api/mas/topology" in html
    assert "fetchAdminApi('/api/diagnostics/' + cmd)" in html
    assert "adminApiErrorMessage(res.status, data)" in html
    assert "headers.set('x-api-key', pageAdminApiKey)" in html


def test_get_chat_ui_contains_mas_inspector():
    """GET /chat must serve the MAS Inspector modal, header button, and chip trigger."""
    resp = client.get("/chat")
    assert resp.status_code == 200
    html = resp.text
    assert 'id="mas-modal"' in html
    assert 'openMasModal()' in html
    assert "Topologie MAS" in html
    assert "/api/mas/topology" in html
    assert "async function fetchAdminApi(url, options = {})" in html
    assert "adminApiErrorMessage(res.status, data)" in html


def test_protected_routes_fail_closed_without_admin_auth(monkeypatch):
    """Protected admin routes (alerts, mcp) must fail closed without configured admin key."""
    for name in (
        "ADMIN_API_KEY",
        "ADMIN_API_KEY_PREVIOUS",
        "ENTRA_TENANT_ID",
        "ENTRA_API_AUDIENCE",
    ):
        monkeypatch.delenv(name, raising=False)

    response = client.get("/mcp/manifest")

    assert response.status_code == 503
    assert response.json() == {
        "detail": "administrative authentication is not configured"
    }
