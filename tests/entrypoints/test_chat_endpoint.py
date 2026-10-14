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

