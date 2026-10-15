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

## 3. Cognitive Profiles Matrix & Deep Architectural Rationale

| Role (`role`) | Primary Focus | Default 0 EUR Model | Context Window | Key Capability |
| :--- | :--- | :--- | :--- | :--- |
| **`remediation`** | Action Planning & Blast Radius | `openrouter/deepseek/deepseek-r1:free` | `64,000` tokens | Deep CoT reasoning, risk impact grading (`0-5`), strict reversibility checks. |
| **`infra`** | Loki Logs & Network Saturation | `openrouter/google/gemma-4-31b-it:free` | `262,144` tokens | Multi-page log ingestion, kernel trace anomaly extraction without truncation. |
| **`data`** | Evidently Drift & Schema Checks | `openrouter/google/gemma-4-26b-a4b-it:free` | `262,144` tokens | Fast Mixture-of-Experts JSON extraction, Pandera error parsing at sub-second latency. |
| **`model`** | Model Drift & MLflow Evaluation | `openrouter/meta-llama/llama-3.3-70b-instruct:free` | `128,000` tokens | High-parameter benchmark evaluation, false positive suppression on minority classes. |
| **`chat`** | Human SRE Copilot & Console UI | `openrouter/deepseek/deepseek-chat:free` | `64,000` tokens | Immediate interactive response, no `<think>` tags, structured metadata cards. |

---

### Detailed Rationale for Each Agent's Default Model Selection

#### 1. RemediationAgent (`role="remediation"`) -> `DeepSeek-R1:free`
- **The Operational Challenge**: The remediation coordinator does not merely read logs; it holds the responsibility of deciding whether to trigger container restarts, pod evacuations, or production rollbacks. Proposing an uncalculated mutation can cascade a minor incident into a total platform outage.
- **Why DeepSeek-R1 is Non-Negotiable**: DeepSeek-R1 is an open-weights reasoning model that performs deliberate, multi-step Chain-of-Thought (CoT) reflection enclosed in `<think>...</think>` tags prior to delivering its JSON payload. This allows the model to perform out-of-band causal deduction:
  - *Dependency cross-check*: Does this latency spike originate from a database deadlock or from downstream queue starvation?
  - *Blast radius calibration*: It mathematically estimates the blast radius score ($0$ to $5$) and reversibility flag required by `ActionIntent` before passing the proposal to the `PolicyEngine`.
- **Verdict**: A fast, non-reasoning model would produce hasty, destructive action proposals; DeepSeek-R1 enforces judicial deliberation.

#### 2. InfraSpecialist (`role="infra"`) -> `Google Gemma-4 31B:free`
- **The Operational Challenge**: Infrastructure crashes (e.g. Linux kernel out-of-memory kills, TCP socket exhaustion, Docker container crash loops, PostgreSQL connection pool starvation) emit thousands of lines of dense, interleaved telemetry.
- **Why Gemma-4 31B is Non-Negotiable**: Standard LLMs truncate prompts at 8,000 or 16,000 tokens, inevitably dropping the root-cause stack trace located in the middle of a log dump. Gemma-4 31B features a massive **256,000-token context window**. It ingests raw Loki log streams, systemd journals, and kernel ring buffers in a single pass without pre-truncation, identifying the exact timestamp and thread where the hardware or networking boundary failed.
- **Verdict**: Context window capacity is the primary constraint in SRE debugging; 256k tokens eliminates telemetry blindness.

#### 3. DataSpecialist (`role="data"`) -> `Google Gemma-4 26B (MoE):free`
- **The Operational Challenge**: Data quality failures (e.g. Pandera contract breaches, missing categorical levels in the BAAC road accident tables, covariate drift detected by Evidently) require sub-second triage across structured schemas and statistical tables.
- **Why Gemma-4 26B is Non-Negotiable**: Data investigation requires high-throughput tabular comprehension, strict Pydantic JSON serialization, and minimal latency. Utilizing a 671B reasoning model for basic schema validation is economically wasteful and operationally sluggish. Gemma-4 26B uses an efficient Mixture-of-Experts (MoE) architecture that delivers immediate, deterministic diagnostics of drift matrices and schema anomalies with zero token waste.
- **Verdict**: Pure schema and distribution validation demands throughput and precision rather than philosophical contemplation; Gemma-4 26B delivers sub-second extraction.

#### 4. ModelSpecialist (`role="model"`) -> `Meta Llama 3.3 70B:free`
- **The Operational Challenge**: Machine learning models in production rarely fail with simple syntax errors; they fail through subtle statistical decay (concept drift, prediction distribution shifts, covariate degradation). In the BAAC road accident severity domain, the model must maintain high F1-Score sensitivity on sparse, critical minority classes (fatalities and severe injuries) against the MLflow reference baseline.
- **Why Llama 3.3 70B is Non-Negotiable**: Differentiating between genuine concept drift ($P(Y \mid X)$ shift requiring retraining) and transient input noise ($P(X)$ feature anomaly) requires strong mathematical and statistical reasoning capacity. With 70 billion parameters, Llama 3.3 provides the conceptual depth needed to interpret confusion matrices, evaluate ROC-AUC degradation, and suppress false-positive retraining proposals.
- **Verdict**: High parameter count is essential to prevent costly, unwarranted model retraining cycles.

#### 5. WebChatCopilot (`role="chat"`) -> `DeepSeek-Chat:free`
- **The Operational Challenge**: Unlike autonomous agents operating asynchronously in the background, the Web Chat interface (`/chat`) directly serves human SRE engineers and on-call operators in live operational war-rooms.
- **Why DeepSeek-Chat is Non-Negotiable**: If `DeepSeek-R1` were assigned to `/chat`, the operator would wait 10 to 25 seconds while the model generated hundreds of invisible `<think>` tokens before displaying the first word. `deepseek-chat:free` (DeepSeek-V3) operates without thinking envelopes, streaming tokens instantaneously (sub-second Time-to-First-Token) while providing full markdown formatting and immediate execution of the 20 MCP Cognitive Starter Prompts.
- **Verdict**: Human interaction requires instantaneous conversational streaming; DeepSeek-Chat provides immediate response times with zero cognitive lag.

---

## 4. Configuration Precedence & Zero-Breaking Contract

The platform resolves configuration through a strict 3-tier hierarchy that guarantees **Native Out-of-the-Box Specialization with Zero Mandatory Configuration**:

```text
Tier 1: Explicit Role Environment Variable (Granular Override)
  e.g. LLM_MODEL_INFRA, LLM_FALLBACK_MODELS_INFRA, LLM_PROVIDER_INFRA
                         │
                         ▼ (if not defined)
Tier 2: Global Environment Variable (Universal Override)
  e.g. LLM_MODEL, LLM_FALLBACK_MODELS, LLM_PROVIDER
                         │
                         ▼ (if not defined)
Tier 3: Native Role-Specialized Default Model (MAS Out-of-the-Box)
  e.g. ROLE_RECOMMENDED_MODELS[role]["model"] on OpenRouter
  - remediation: openrouter/deepseek/deepseek-r1:free
  - infra:       openrouter/google/gemma-4-31b-it:free
  - data:        openrouter/google/gemma-4-26b-a4b-it:free
  - model:       openrouter/meta-llama/llama-3.3-70b-instruct:free
  - chat:        openrouter/deepseek/deepseek-chat:free
                         │
                         ▼ (if provider is not OpenRouter and no role default)
Tier 4: Provider Default Model
  e.g. PROVIDER_PROFILES[provider]["default_model"]
```

### Practical Configuration Scenarios:

#### Scenario A: Native Distributed Mesh (Default Out-of-the-Box — 0 EUR)
Zero environment variables declared. Each agent automatically receives its specialized expert model:
- `RemediationAgent` runs on `deepseek-r1:free`
- `InfraSpecialist` runs on `gemma-4-31b-it:free` (256k context)
- `DataSpecialist` runs on `gemma-4-26b-a4b-it:free`
- `ModelSpecialist` runs on `llama-3.3-70b-instruct:free`
- `WebChatCopilot` runs on `deepseek-chat:free`

#### Scenario B: Universal Single-Model Override (Force All to One LLM)
Declaring `LLM_MODEL` forces all 5 agent roles to run on a single model (e.g., local Ollama or private OpenAI):
```bash
LLM_PROVIDER=openrouter
LLM_MODEL=openrouter/deepseek/deepseek-chat:free
```

#### Scenario C: Hybrid Cognitive Mesh (Granular Override)
Specific demanding roles are redirected to alternative specialized models:
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

#### Scenario D: Multi-Provider Sovereignty
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
