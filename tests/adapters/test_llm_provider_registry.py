"""
Unit & Integration Tests — Universal LLM Provider Registry & Adapters
=====================================================================
Validates:
1. Environment variable resolution across all 8 provider profiles.
2. Secure API key masking (no clear-text keys in status outputs).
3. FallbackLLMAdapter sequential failover when primary model fails.
4. OllamaAdapter Pydantic validation via mocked HTTP response.
5. LLMProviderRegistry.list_providers() comprehensive catalogue.
"""

import os
from unittest.mock import MagicMock, patch
import pytest
from pydantic import BaseModel

from agentic_ops.adapters.llm_provider_registry import (
    LLMProviderRegistry,
    PROVIDER_PROFILES,
)
from agentic_ops.adapters.llm_protocol import (
    FallbackLLMAdapter,
    OllamaAdapter,
    _ProbeResponse,
)


class DummyAction(BaseModel):
    action: str
    target: str


class TestLLMProviderRegistry:
    def test_default_config_is_openrouter_free(self, monkeypatch):
        """When no env vars are set, defaults to OpenRouter DeepSeek-R1 free."""
        monkeypatch.delenv("LLM_PROVIDER", raising=False)
        monkeypatch.delenv("LLM_MODEL", raising=False)
        monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)

        cfg = LLMProviderRegistry.resolve_config()
        assert cfg.provider == "openrouter"
        assert ":free" in cfg.model
        assert cfg.api_key_present is False
        assert cfg.api_key_masked == "(absent)"
        assert len(cfg.fallback_models) > 0

    def test_api_key_masking_security(self, monkeypatch):
        """Ensures API keys are never exposed in clear-text."""
        monkeypatch.setenv("LLM_PROVIDER", "openrouter")
        monkeypatch.setenv("OPENROUTER_API_KEY", "sk-or-v1-abcdef1234567890abcdef")

        cfg = LLMProviderRegistry.resolve_config()
        assert cfg.api_key_present is True
        assert "sk-or-" in cfg.api_key_masked
        assert "def" in cfg.api_key_masked
        assert "1234567890" not in cfg.api_key_masked
        assert cfg.api_key_masked != "sk-or-v1-abcdef1234567890abcdef"

    def test_all_8_providers_are_registered(self):
        """Validates that all 8 supported providers have profiles."""
        expected = {
            "openrouter", "gemini", "openai", "anthropic",
            "azure", "mistral", "huggingface", "ollama"
        }
        assert set(PROVIDER_PROFILES.keys()) == expected

    def test_unknown_provider_graceful_fallback(self, monkeypatch):
        """If an unknown provider is specified, fall back to openrouter safely."""
        monkeypatch.setenv("LLM_PROVIDER", "nonexistent_provider_xyz")
        cfg = LLMProviderRegistry.resolve_config()
        assert cfg.provider == "openrouter"

    def test_list_providers_catalog(self, monkeypatch):
        """Verifies the catalog contains active flags and free models."""
        monkeypatch.setenv("LLM_PROVIDER", "ollama")
        providers = LLMProviderRegistry.list_providers()
        assert len(providers) == 8

        ollama_entry = next(p for p in providers if p["provider"] == "ollama")
        assert ollama_entry["active"] is True
        assert len(ollama_entry["free_models"]) > 0

        openrouter_entry = next(p for p in providers if p["provider"] == "openrouter")
        assert openrouter_entry["active"] is False
        assert len(openrouter_entry["free_models"]) >= 4

    def test_fallback_chain_on_primary_failure(self):
        """Verifies FallbackLLMAdapter tries the fallback when primary raises."""
        primary_mock = MagicMock()
        primary_mock.complete.side_effect = RuntimeError("Primary model rate limited (429)")

        fallback_mock = MagicMock()
        expected_response = DummyAction(action="create_issue", target="test-service")
        fallback_mock.complete.return_value = expected_response

        adapter = FallbackLLMAdapter(primary=primary_mock, fallbacks=[fallback_mock])

        result = adapter.complete(
            system="system prompt",
            user="user prompt",
            response_model=DummyAction,
            temperature=0.0,
        )

        assert primary_mock.complete.call_count == 1
        assert fallback_mock.complete.call_count == 1
        assert result.action == "create_issue"
        assert result.target == "test-service"

    def test_fallback_chain_all_failing_raises_runtime_error(self):
        """If all adapters fail, a descriptive RuntimeError is raised."""
        primary_mock = MagicMock()
        primary_mock.complete.side_effect = RuntimeError("Primary down")
        fb1_mock = MagicMock()
        fb1_mock.complete.side_effect = RuntimeError("Fallback 1 down")

        adapter = FallbackLLMAdapter(primary=primary_mock, fallbacks=[fb1_mock])

        with pytest.raises(RuntimeError, match="All 2 LLM adapters in the fallback chain failed"):
            adapter.complete(
                system="system",
                user="user",
                response_model=DummyAction,
            )

    @patch("httpx.Client")
    def test_ollama_adapter_mocked_success(self, mock_client_cls):
        """Validates OllamaAdapter parses JSON format into the response_model."""
        mock_resp = MagicMock()
        mock_resp.json.return_value = {
            "message": {"content": '{"action": "propose_retrain", "target": "baac_rf"}'}
        }
        mock_resp.raise_for_status.return_value = None

        mock_client = MagicMock()
        mock_client.post.return_value = mock_resp
        mock_client.__enter__.return_value = mock_client
        mock_client.__exit__.return_value = None
        mock_client_cls.return_value = mock_client

        adapter = OllamaAdapter(base_url="http://localhost:11434", model="llama3.2:3b")
        res = adapter.complete(
            system="system",
            user="user",
            response_model=DummyAction,
            temperature=0.0,
        )

        assert res.action == "propose_retrain"
        assert res.target == "baac_rf"

    def test_strip_think_tags_removes_r1_reasoning_blocks(self):
        """Verifies that <think>...</think> chain-of-thought blocks are cleanly stripped."""
        from agentic_ops.adapters.llm_protocol import _strip_think_tags

        raw_r1_output = """<think>
Here is my deep reasoning process.
I must propose a safe action for this incident.
The target is baac_rf.
</think>
```json
{
  "action": "create_issue",
  "target": "baac_rf"
}
```"""
        cleaned = _strip_think_tags(raw_r1_output)
        assert "<think>" not in cleaned
        assert "deep reasoning" not in cleaned
        assert cleaned == '{\n  "action": "create_issue",\n  "target": "baac_rf"\n}'

    @patch("httpx.Client")
    def test_ollama_adapter_handles_r1_with_think_tags(self, mock_client_cls):
        """Validates OllamaAdapter parses response even if model emits <think> blocks."""
        mock_resp = MagicMock()
        mock_resp.json.return_value = {
            "message": {
                "content": "<think>Analyzing root cause...</think>{\"action\": \"create_issue\", \"target\": \"baac-api\"}"
            }
        }
        mock_resp.raise_for_status.return_value = None

        mock_client = MagicMock()
        mock_client.post.return_value = mock_resp
        mock_client.__enter__.return_value = mock_client
        mock_client.__exit__.return_value = None
        mock_client_cls.return_value = mock_client

        adapter = OllamaAdapter(base_url="http://localhost:11434", model="deepseek-r1:7b")
        res = adapter.complete(
            system="system",
            user="user",
            response_model=DummyAction,
            temperature=0.0,
        )

        assert res.action == "create_issue"
        assert res.target == "baac-api"

    def test_role_config_resolution_with_custom_env(self, monkeypatch):
        """Validates that role-specific environment variables take precedence over global."""
        monkeypatch.setenv("LLM_MODEL", "openrouter/deepseek/deepseek-r1:free")
        monkeypatch.setenv("LLM_MODEL_INFRA", "openrouter/google/gemma-4-31b-it:free")
        monkeypatch.setenv("LLM_MODEL_DATA", "openrouter/google/gemma-4-26b-a4b-it:free")
        monkeypatch.setenv("LLM_MODEL_MODEL", "openrouter/meta-llama/llama-3.3-70b-instruct:free")
        monkeypatch.setenv("LLM_MODEL_CHAT", "openrouter/deepseek/deepseek-chat:free")

        infra_cfg = LLMProviderRegistry.resolve_role_config("infra")
        assert infra_cfg.model == "openrouter/google/gemma-4-31b-it:free"
        assert infra_cfg.extra_kwargs.get("is_specialized") is True

        data_cfg = LLMProviderRegistry.resolve_role_config("data")
        assert data_cfg.model == "openrouter/google/gemma-4-26b-a4b-it:free"
        assert data_cfg.extra_kwargs.get("is_specialized") is True

        chat_cfg = LLMProviderRegistry.resolve_role_config("chat")
        assert chat_cfg.model == "openrouter/deepseek/deepseek-chat:free"
        assert chat_cfg.extra_kwargs.get("is_specialized") is True

        # Unspecified role falls back to global LLM_MODEL
        remediation_cfg = LLMProviderRegistry.resolve_role_config("remediation")
        assert remediation_cfg.model == "openrouter/deepseek/deepseek-r1:free"
        assert remediation_cfg.extra_kwargs.get("is_specialized") is False

    def test_role_fallbacks_precedence(self, monkeypatch):
        """Verifies role-specific fallbacks override global fallbacks."""
        monkeypatch.setenv("LLM_FALLBACK_MODELS", "global/fb1,global/fb2")
        monkeypatch.setenv("LLM_FALLBACK_MODELS_INFRA", "infra/fb1,infra/fb2,infra/fb3")

        infra_cfg = LLMProviderRegistry.resolve_role_config("infra")
        assert infra_cfg.fallback_models == ["infra/fb1", "infra/fb2", "infra/fb3"]

        data_cfg = LLMProviderRegistry.resolve_role_config("data")
        assert data_cfg.fallback_models == ["global/fb1", "global/fb2"]

    def test_get_roles_topology_returns_all_supported_roles(self, monkeypatch):
        """Verifies get_roles_topology exposes all 5 roles and their recommendations."""
        monkeypatch.setenv("LLM_MODEL_INFRA", "openrouter/google/gemma-4-31b-it:free")
        topology = LLMProviderRegistry.get_roles_topology()

        expected_roles = {"remediation", "infra", "data", "model", "chat"}
        assert set(topology.keys()) == expected_roles

        assert topology["infra"]["model"] == "openrouter/google/gemma-4-31b-it:free"
        assert topology["infra"]["is_specialized"] is True
        assert "recommendation" in topology["infra"]
        assert topology["remediation"]["is_specialized"] is False

    @patch("agentic_ops.adapters.llm_protocol.LiteLLMAdapter.__init__", return_value=None)
    def test_build_adapter_for_role_applies_role_label(self, mock_litellm_init, monkeypatch):
        """Verifies build_adapter_for_role constructs LiteLLMAdapter with role parameter."""
        monkeypatch.setenv("LLM_PROVIDER", "openrouter")
        monkeypatch.setenv("LLM_MODEL_INFRA", "openrouter/google/gemma-4-31b-it:free")

        adapter = LLMProviderRegistry.build_adapter_for_role("infra")
        assert isinstance(adapter, FallbackLLMAdapter)
        # Check that LiteLLMAdapter was initialized with role="infra"
        _, kwargs = mock_litellm_init.call_args_list[0]
        assert kwargs.get("role") == "infra"

    def test_orchestrator_injects_specialized_roles(self):
        """Verifies Orchestrator resolves LLM per specialist role or uses llm_by_role."""
        from agentic_ops.core.orchestrator import Orchestrator

        mock_obs = MagicMock()
        mock_pe = MagicMock()
        mock_es = MagicMock()

        infra_llm = MagicMock()
        data_llm = MagicMock()
        model_llm = MagicMock()
        remediation_llm = MagicMock()

        orch = Orchestrator(
            observability=mock_obs,
            policy_engine=mock_pe,
            evidence_store=mock_es,
            llm_by_role={
                "infra": infra_llm,
                "data": data_llm,
                "model": model_llm,
                "remediation": remediation_llm,
            },
        )

        assert orch._get_llm_for_role("infra") is infra_llm
        assert orch._get_llm_for_role("data") is data_llm
        assert orch._get_llm_for_role("model") is model_llm
        assert orch._get_llm_for_role("remediation") is remediation_llm

        infra_spec = orch._get_specialist("SEC_INFRA_LEAK")
        assert infra_spec.llm is infra_llm

        data_spec = orch._get_specialist("DATA_DRIFT_EVIDENTLY")
        assert data_spec.llm is data_llm

        model_spec = orch._get_specialist("MODEL_F1_DROP")
        assert model_spec.llm is model_llm


