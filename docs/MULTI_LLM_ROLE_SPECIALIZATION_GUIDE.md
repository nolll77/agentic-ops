# Multi-LLM Role Specialization & Cognitive Topology Guide

> **Module Entrypoint**: [`agentic_ops/adapters/llm_provider_registry.py`](file:///Users/nolll/Documents/car_acc/agentic-ops-core/agentic_ops/adapters/llm_provider_registry.py) & [`agentic_ops/core/orchestrator.py`](file:///Users/nolll/Documents/car_acc/agentic-ops-core/agentic_ops/core/orchestrator.py)
> **Prometheus FinOps Metrics**: [`agentic_ops/adapters/llm_protocol.py`](file:///Users/nolll/Documents/car_acc/agentic-ops-core/agentic_ops/adapters/llm_protocol.py)
> **Live API Topology**: `GET /api/llm/status` (`roles_topology`)
> **Automated Validation Suite**: [`tests/adapters/test_llm_provider_registry.py`](file:///Users/nolll/Documents/car_acc/agentic-ops-core/tests/adapters/test_llm_provider_registry.py) (`15 passed`)

---

## 1. Executive Summary & Cognitive Rationale

In high-stakes SRE and MLOps production systems, deploying a single undifferentiated Large Language Model for all platform capabilities is an anti-pattern. Different tasks require radically conflicting cognitive profiles:

1. **Root-Cause Investigation across Logs (`infra`)**: Ingesting raw kernel logs, Loki stream dumps, or Tailscale interface metrics requires a massive context window (e.g., 256,000+ tokens) but does not require deep mathematical Chain-of-Thought (CoT).
2. **Remediation Planning & Blast Radius Veto (`remediation`)**: Calculating blast radius scores, formulating rollbacks, and verifying state reversibility requires deliberate step-by-step reasoning (e.g., DeepSeek-R1 CoT).
3. **Data Quality & Covariance Drift Triage (`data`)**: Validating Pandera schemas and Evidently drift matrices requires ultra-low latency, strict schema compliance, and zero superfluous token overhead.
4. **Machine Learning Model Degradation (`model`)**: Assessing MLflow F1-score drop against reference distributions demands the high-capacity parametric rigor of a 70B parameter model.
5. **Interactive Operator Web Chat (`chat`)**: Assisting the on-call human SRE via `/chat` requires conversational speed and pure text/JSON output without internal `<think>` reasoning envelopes.

`Agentic-Ops` solves this dilemma through **Cognitive Specialization by Role**: each agent is configured with the optimal model for its domain, maintains an independent fallback chain, and can still fall back to `LLM_MODEL` with **100% zero-breaking backward compatibility**.

---

## 2. Global Cognitive Architecture

```text
+--------------------------------------------------------------------------------------------------+
| AGENTIC-OPS CONTROL PLANE — COGNITIVE MULTI-LLM TOPOLOGY                                         |
+--------------------------------------------------------------------------------------------------+
|                                                                                                  |
| [Remediation Coordinator] ----> role="remediation" ----> LLM_MODEL_REMEDIATION                  |
| (Deep Reasoning & CoT)          Fallback: LLM_MODEL      (Default: deepseek-r1:free)             |
|                                                                                                  |
| [Infra Specialist] -----------> role="infra" ----------> LLM_MODEL_INFRA                        |
| (256k Context Window Logs)      Fallback: LLM_MODEL      (Default: gemma-4-31b-it:free)          |
|                                                                                                  |
| [Data Specialist] ------------> role="data" -----------> LLM_MODEL_DATA                         |
| (Evidently & Covariance)        Fallback: LLM_MODEL      (Default: gemma-4-26b-a4b-it:free)      |
|                                                                                                  |
| [Model Specialist] -----------> role="model" ----------> LLM_MODEL_MODEL                        |
| (MLflow F1 Drift & Metrics)     Fallback: LLM_MODEL      (Default: llama-3.3-70b-instruct:free)  |
|                                                                                                  |
| [Web Chat SRE Assistant] -----> role="chat" -----------> LLM_MODEL_CHAT                         |
| (Interactive Low Latency)       Fallback: LLM_MODEL      (Default: deepseek-chat:free)           |
|                                                                                                  |
+--------------------------------------------------------------------------------------------------+
```

---

## 3. Cognitive Profiles Matrix

| Role (`role`) | Primary Focus | Recommended 0 EUR Model | Context Window | Key Capability |
| :--- | :--- | :--- | :--- | :--- |
| **`remediation`** | Action Planning & Blast Radius | `openrouter/deepseek/deepseek-r1:free` | `64,000` tokens | Deep CoT reasoning, risk impact grading (`0-5`), strict reversibility checks. |
| **`infra`** | Loki Logs & Network Saturation | `openrouter/google/gemma-4-31b-it:free` | `262,144` tokens | Multi-page log ingestion, kernel trace anomaly extraction. |
| **`data`** | Evidently Drift & Schema Checks | `openrouter/google/gemma-4-26b-a4b-it:free` | `262,144` tokens | Fast Mixture-of-Experts JSON extraction, Pandera error parsing. |
| **`model`** | Model Drift & MLflow Evaluation | `openrouter/meta-llama/llama-3.3-70b-instruct:free` | `128,000` tokens | High-parameter benchmark evaluation, false positive suppression. |
| **`chat`** | Human SRE Copilot & Console UI | `openrouter/deepseek/deepseek-chat:free` | `64,000` tokens | Immediate interactive response, no `<think>` tags, structured metadata cards. |

---

## 4. Configuration Precedence & Zero-Breaking Contract

The platform resolves configuration through a strict 3-tier hierarchy:

```text
Tier 1: Role-Specific Environment Variables
  e.g. LLM_MODEL_INFRA, LLM_FALLBACK_MODELS_INFRA, LLM_PROVIDER_INFRA
                         │
                         ▼ (if not defined)
Tier 2: Global Environment Variables
  e.g. LLM_MODEL, LLM_FALLBACK_MODELS, LLM_PROVIDER
                         │
                         ▼ (if not defined)
Tier 3: Provider Profile Default
  e.g. PROVIDER_PROFILES["openrouter"]["default_model"]
```

### Practical Configuration Scenarios:

#### Scenario A: Global Uniform Brain (Classic Mode)
Only `LLM_MODEL` is declared. All 5 agent roles inherit the global model automatically:
```bash
LLM_PROVIDER=openrouter
LLM_MODEL=openrouter/deepseek/deepseek-r1:free
```

#### Scenario B: Hybrid Cognitive Mesh (Recommended)
Specific demanding roles are redirected to specialized models:
```bash
# Baseline global model
LLM_PROVIDER=openrouter
LLM_MODEL=openrouter/deepseek/deepseek-r1:free

# Infrastructure agent gets massive 256k context for Loki dumps
LLM_MODEL_INFRA=openrouter/google/gemma-4-31b-it:free

# Data specialist gets high-throughput MoE
LLM_MODEL_DATA=openrouter/google/gemma-4-26b-a4b-it:free

# Chat UI gets ultra-responsive non-thinking model
LLM_MODEL_CHAT=openrouter/deepseek/deepseek-chat:free
```

#### Scenario C: Multi-Provider Sovereignty
Different roles can target different providers (e.g., local Ollama for model evaluation, OpenRouter for cloud):
```bash
LLM_PROVIDER=openrouter
LLM_MODEL=openrouter/deepseek/deepseek-r1:free
LLM_PROVIDER_MODEL=ollama
LLM_MODEL_MODEL=ollama/llama3.2:3b
```

---

## 5. Implementation Details

### A. Dynamic Factory in `LLMProviderRegistry`
```python
# agentic_ops/adapters/llm_provider_registry.py
cfg = LLMProviderRegistry.resolve_role_config(role="infra")
adapter = LLMProviderRegistry.build_adapter_for_role(role="infra")
```
Every adapter is wrapped inside a `FallbackLLMAdapter` inheriting the role's specific fallback chain and passing `role="infra"` to Prometheus.

### B. Dependency Injection in `Orchestrator`
```python
# agentic_ops/core/orchestrator.py
def _get_specialist(self, risk_id: str):
    if "MODEL" in risk_id.upper():
        return ModelSpecialist(llm=self._get_llm_for_role("model"))
    elif "INFRA" in risk_id.upper():
        return InfraSpecialist(llm=self._get_llm_for_role("infra"))
    else:
        return DataSpecialist(llm=self._get_llm_for_role("data"))
```
When running unit tests or mocking, supplying `Orchestrator(..., llm=mock_llm)` or `Orchestrator(..., llm_by_role={"infra": mock_infra})` overrides dynamic resolution without modifying runtime code.

---

## 6. Fine-Grained Prometheus Observability & FinOps

Every LLM request records its role label in Prometheus metrics:

```promql
# Request rate per agent role
sum by (role, status) (rate(agentic_ops_llm_requests_total[5m]))

# P95 Latency per agent role
histogram_quantile(0.95, sum by (le, role) (rate(agentic_ops_llm_latency_seconds_bucket[5m])))

# Token consumption by role and type
sum by (role, token_type) (agentic_ops_llm_tokens_total)
```

---

## 7. Verification & Live Inspection Commands

```bash
# 1. Inspect live role topology
curl -s https://agentic-ops-5ebv.onrender.com/api/llm/status | jq .roles_topology

# 2. Run dedicated multi-LLM test suite
pytest tests/adapters/test_llm_provider_registry.py -v

# 3. Verify chat endpoint role wiring
pytest tests/entrypoints/test_chat_endpoint.py -v
```
