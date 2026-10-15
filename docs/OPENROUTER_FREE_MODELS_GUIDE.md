# OpenRouter LLM Gateway & Free AI Agents Guide

> **Module Entrypoint**: `agentic_ops/adapters/llm_provider_registry.py` & `agentic_ops/adapters/llm_protocol.py`
> **Live Diagnostic Status**: `https://agentic-ops-5ebv.onrender.com/api/llm/status` | **Model Catalog**: `https://agentic-ops-5ebv.onrender.com/api/llm/models`
> **Automated Validation Suite**: `tests/adapters/test_llm_provider_registry.py` (`10 passed`)
> **Live Web Chat Interface**: `https://agentic-ops-5ebv.onrender.com/chat`

---

## 1. Architectural Overview: How OpenRouter Works in Agentic-Ops

In `Agentic-Ops`, the cognitive reasoning agents (`RemediationAgent`, `SpecialistAgent`) are completely decoupled from physical model providers.

OpenRouter acts as a **unified multi-model proxy and clearinghouse**:
- **Single Open Pipe (`0 EUR`)**: A single account and a single API key (`OPENROUTER_API_KEY`) grant immediate, unconstrained access to over 200+ models.
- **Zero Provider Configuration**: There is no need to enable individual models, request quotas from model creators, or configure endpoints on the OpenRouter dashboard. The pipe is completely open; specifying the model string dynamically selects the backend.
- **Zero Billing Risk**: If no credit card is linked to the OpenRouter account, requests targeting paid endpoints fail with `HTTP 402 Payment Required`. Any model tagged with `:free` incurs strictly **0.00 EUR** in input and output token fees.

```ansi
[1;34m+--------------------------------------------------------------------------------------------------+[0m
[1;34m|[0m AGENTIC-OPS CONTROL PLANE (FastAPI / FSM / RemediationAgent)                                      [1;34m|[0m
[1;34m+------------------------------------------------+-------------------------------------------------+[0m
[1;34m|[0m[1;34m|[0m
                                                 v
[1;34m+--------------------------------------------------------------------------------------------------+[0m
[1;34m|[0m LLM PROVIDER REGISTRY (agentic_ops/adapters/llm_provider_registry.py)                            [1;34m|[0m
[1;34m|[0m Resolves: LLM_PROVIDER=openrouter -> Profile, Sanitized Key (sk-or-***), Fallback Chain           [1;34m|[0m
[1;34m+------------------------------------------------+-------------------------------------------------+[0m
[1;34m|[0m[1;34m|[0m
                                                 v
[1;34m+--------------------------------------------------------------------------------------------------+[0m
[1;34m|[0m FALLBACK LLM ADAPTER (agentic_ops/adapters/llm_protocol.py)                                       [1;34m|[0m
[1;34m|[0m Sequential try: Primary -> Fallback 1 -> Fallback 2 (HTTP 429 / Timeout Interception)             [1;34m|[0m
[1;34m+------------------------------------------------+-------------------------------------------------+[0m
[1;34m|[0m[1;34m|[0m
                         OpenRouter HTTPS API Gateway (POST https://openrouter.ai/api/v1/chat/completions)
                                                 v
[1;34m+--------------------------------------------------------------------------------------------------+[0m
[1;34m|[0m OPENROUTER UNIFIED MODEL HUB (200+ Models Available via Single API Key)                          [1;34m|[0m
[1;34m|[0m                                                                                                  [1;34m|[0m
[1;34m|[0m [Google Gemma 4 Free]       [DeepSeek Reasoning]      [NVIDIA Nemotron Free]   [OpenRouter Router] [1;34m|[0m
[1;34m|[0m google/gemma-4-31b-it:[1;32mfree[0m  deepseek/deepseek-r1:[1;32mfree[0m nvidia/nemotron-3-nano... openrouter/[1;32mfree[0m    [1;34m|[0m
[1;34m|[0m (256k Context Window)       (Chain-of-Thought)        (Content Safety & CoT)   (Dynamic Failover)  [1;34m|[0m
[1;34m+--------------------------------------------------------------------------------------------------+[0m
```

---

## 2. Is Google Gemma Available for Agents?

**Yes.** Google Gemma is fully available on OpenRouter, including two high-capacity free-tier variants:

1. **`google/gemma-4-31b-it:free`**:
   - **Type**: Dense Instruction-Tuned model (`31 Billion` parameters).
   - **Context Window**: `262,144` tokens (256k).
   - **Cost**: `0.00 $` input / `0.00 $` output.
   - **Best Used For**: Deep root cause analysis, synthesizing complex logs from `Loki`, and formulating multi-step incident explanations.
2. **`google/gemma-4-26b-a4b-it:free`**:
   - **Type**: Mixture-of-Experts architecture (`26 Billion` total parameters, `4 Billion` active).
   - **Context Window**: `262,144` tokens (256k).
   - **Cost**: `0.00 $` input / `0.00 $` output.
   - **Best Used For**: Low-latency triage, JSON extraction, and high-frequency alerting.

To assign Gemma as the primary cognitive brain of `Agentic-Ops`, configure your environment:
```bash
LLM_PROVIDER=openrouter
LLM_MODEL=openrouter/google/gemma-4-31b-it:free
OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxxxxxxxxxx
```

---

## 3. Complete Catalog of 100% Free AI Models on OpenRouter (`:free`)

As queried directly against the OpenRouter API, the following **17 models** operate at **`0.00 $ / token`** (free tier):

| Model Identifier (`LLM_MODEL`) | Provider / Architecture | Context Length | Specialized Agent Capability |
| :--- | :--- | :--- | :--- |
| **`google/gemma-4-31b-it:free`** | Google (Dense Instruct) | `262,144` tokens | SRE log analysis, multi-source diagnosis, metric correlation. |
| **`google/gemma-4-26b-a4b-it:free`** | Google (Mixture-of-Experts) | `262,144` tokens | High-speed telemetry parsing, JSON formatting. |
| **`google/lyria-3-pro-preview`** | Google | `1,048,576` tokens | Ultra-large context window (1 Million tokens) exploratory analysis. |
| **`google/lyria-3-clip-preview`** | Google | `1,048,576` tokens | 1M context diagnostic buffer. |
| **`nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free`** | NVIDIA (Reasoning MoE) | `256,000` tokens | Chain-of-thought mathematical reasoning, root cause deduction. |
| **`nvidia/nemotron-3-super-120b-a12b:free`** | NVIDIA (High-Capacity MoE) | `262,144` tokens | Advanced architecture validation, high-reliability governance. |
| **`nvidia/nemotron-3-ultra-550b-a55b:free`** | NVIDIA (Massive MoE) | `1,000,000` tokens | Ultra-deep reasoning across historical incident archives. |
| **`nvidia/nemotron-3.5-lightning:free`** | NVIDIA | `1,000,000` tokens | Low-latency 1M token triage. |
| **`nvidia/nemotron-3.5-content-safety:free`** | NVIDIA | `128,000` tokens | Input sanitization, prompt injection guardrail. |
| **`cohere/north-mini-code:free`** | Cohere | `256,000` tokens | Python code review, patch analysis, configuration script validation. |
| **`liquid/lfm-2.5-2.6b:free`** | Liquid AI | `65,536` tokens | Compact neural architecture, minimal memory overhead. |
| **`poolside/laguna-s-2.1:free`** | Poolside | `262,144` tokens | Software engineering and code generation tasks. |
| **`poolside/laguna-xs-2.1:free`** | Poolside | `262,144` tokens | Lightweight software engineering assistant. |
| **`openrouter/free`** | OpenRouter Dynamic Router | `200,000` tokens | Automatic meta-routing to the highest-availability free model. |
| **`dots-studio/dots-3-note-preview:free`** | Dots Studio | `512,000` tokens | Long-form note taking and summary generation. |
| **`thinkingmachines/inkling:free`** | Thinking Machines | `1,048,576` tokens | Long-context experimental reasoning. |
| **`thinkingmachines/inkling-small:free`** | Thinking Machines | `1,048,576` tokens | Compact experimental reasoning model. |

---

## 4. Why Default to `deepseek/deepseek-r1:free`? Rationale & Trade-offs

The default configuration in `LLMProviderRegistry` is set to:
```python
"default_model": "openrouter/deepseek/deepseek-r1:free"
```

### The 3 Core Engineering Reasons:
1. **Deliberate Chain-of-Thought (CoT)**:
   - Diagnosing complex incidents (such as `DATA-042` feature drift or Kubernetes OOM loops) requires understanding causal dependencies (e.g., verifying whether an upstream sensor corrupted the data before attempting a model retraining).
   - Reasoning models explicitly think before answering, preventing hasty hallucinations and respecting deterministic governance rules like `R-001` (`upstream_masks_service`).
2. **Pydantic Schema Adherence**:
   - `Agentic-Ops` agents must output strictly valid JSON conforming to the `ActionIntent` contract (`action`, `target`, `rationale`, `declared_blast_radius`).
   - DeepSeek-R1 demonstrates one of the highest structural compliance rates among publicly accessible models.
3. **Radical Honesty: The Free Tier Pitfall**:
   - Because `deepseek-r1:free` is the most popular free reasoning model in the industry, it frequently hits concurrency rate limits (`HTTP 429`) during peak hours.
   - Rather than masking this instability, `Agentic-Ops` addresses it architecturally using **automated fallback failovers**.

---

## 5. Deterministic Failover Mechanics: How `FallbackLLMAdapter` Operates

When an incident strikes production, an agent cannot be left hanging due to an API quota limit. `Agentic-Ops` solves this via `FallbackLLMAdapter`:

```
                 Incoming Remediation Request
                              │
                              ▼
                  [ 1. Primary Model ]
             (e.g., google/gemma-4-31b-it:free)
                  ┌───────────┴───────────┐
                  │                       │
              Success ?                Failure ?
                  │             (HTTP 429 / Timeout / 5xx)
                  ▼                       │
         Validated JSON Contract          ▼
                                [ 2. Fallback Model 1 ]
                       (e.g., nvidia/nemotron-3-nano...:free)
                                  ┌───────┴───────┐
                                  │               │
                              Success ?        Failure ?
                                  │               │
                                  ▼               ▼
                         Validated Contract [ 3. Fallback Model 2 ]
                                            (e.g., openrouter/free)
```

### Step-by-Step Failover Sequence:
1. **Exponential Retry**: The primary model first undergoes up to 3 retry attempts via `tenacity` (backoff: 2 to 10 seconds) to absorb minor transport hiccups.
2. **Exception Interception**: If an unrecoverable exception (`RateLimitError`, `HTTP 429`, or gateway timeout) occurs, `FallbackLLMAdapter` catches the error.
3. **Sequential Failover**: The exact prompt (including system instructions and schema specifications) is immediately dispatched to the next adapter in `LLM_FALLBACK_MODELS`.
4. **Prometheus Telemetry**: Every call records individual metrics:
   - `agentic_ops_llm_requests_total{provider="openrouter", model="gemma-4-31b-it:free", status="error"}`
   - `agentic_ops_llm_requests_total{provider="openrouter", model="nemotron-3-nano...", status="success"}`
   - `agentic_ops_llm_latency_seconds{...}`
   This enables SRE teams to monitor live failover rates in Prometheus or Grafana.

---

---

## 6. Unified LLM Engine Architecture: Web Chat (`/chat`) vs. Autonomous Agents

A critical architectural question is whether the interactive Web Chat interface ([`/chat`](https://agentic-ops-5ebv.onrender.com/chat) / `POST /api/chat`) runs on a different or degraded model compared to the autonomous remediation agents (`RemediationAgent`, `SpecialistAgent`).

### A. Strict Engine Unification (Same Physical LLM & Factory)
In `Agentic-Ops`, **both the autonomous agents and the conversational Web Chat utilize the EXACT same LLM adapter and resolution factory**:
```python
# From agentic_ops/adapters/llm_provider_registry.py
@staticmethod
def chat(message: str, history: list[dict] | None = None) -> dict:
    adapter = LLMProviderRegistry.build_adapter_from_env()
    ...
```
- If `LLM_MODEL=openrouter/google/gemma-4-31b-it:free` is configured, **Gemma 31B powers both the agents and the Web Chat**.
- Swapping the active provider or model immediately switches the entire platform simultaneously.

```ansi
[1;34m+--------------------------------------------------------------------------------------------------+[0m
[1;34m|[0m UNIFIED COGNITIVE BACKBONE TOPOLOGY                                                              [1;34m|[0m
[1;34m+--------------------------------------------------------------------------------------------------+[0m
[1;34m|[0m                                                                                                  [1;34m|[0m
[1;34m|[0m [Autonomous MLOps Agents]                        [Interactive Web Chat (/chat)]                 [1;34m|[0m
[1;34m|[0m - [1;35mRemediationAgent[0m (FSM Diagnostic)              - Human SRE Operator Interface                 [1;34m|[0m
[1;34m|[0m - SpecialistAgent (Root Cause Analysis)          - 20 MCP Cognitive Starter Prompts Modal       [1;34m|[0m
[1;34m|[0m                                                                                                  [1;34m|[0m
[1;34m|[0m                                \                /                                                [1;34m|[0m
[1;34m|[0m                                 \              /                                                 [1;34m|[0m
[1;34m|[0m                                  v            v                                                  [1;34m|[0m
[1;34m|[0m[1;34m                   +--------------------------------------------+                                 [0m[1;34m|[0m
[1;34m|[0m                   | LLMProviderRegistry.build_adapter_from_env |                                 [1;34m|[0m
[1;34m|[0m[1;34m                   +---------------------+----------------------+                                 [0m[1;34m|[0m
[1;34m|[0m                                         |                                                        [1;34m|[0m
[1;34m|[0m                                         v                                                        [1;34m|[0m
[1;34m|[0m[1;34m                   +--------------------------------------------+                                 [0m[1;34m|[0m
[1;34m|[0m                   | FallbackLLMAdapter (Auto-Failover Chain)   |                                 [1;34m|[0m
[1;34m|[0m[1;34m                   +---------------------+----------------------+                                 [0m[1;34m|[0m
[1;34m|[0m                                         |                                                        [1;34m|[0m
[1;34m|[0m                                         v                                                        [1;34m|[0m
[1;34m|[0m[1;34m                   +--------------------------------------------+                                 [0m[1;34m|[0m
[1;34m|[0m                   | OpenRouter Gateway (:[1;32mfree[0m 24/7 Cloud Hub)  |                                 [1;34m|[0m
[1;34m|[0m[1;34m                   +--------------------------------------------+                                 [0m[1;34m|[0m
[1;34m+--------------------------------------------------------------------------------------------------+[0m
```

### B. Is the Fallback Chain Also Active for the Web Chat?
**Yes, unconditionally.**
Because `build_adapter_from_env()` wraps the primary model in `FallbackLLMAdapter`, all conversational queries submitted to `/chat` inherit full failover protection:
1. If the primary model encounters an `HTTP 429 Too Many Requests` (OpenRouter rate limit) or a timeout, the chat interface does not crash or return a 500 error.
2. `FallbackLLMAdapter` transparently catches the error and resubmits the user's message to the fallback model (e.g., `nvidia/nemotron...:free`, then `openrouter/free`).
3. The human operator receives their answer seamlessly with accurate latency and model metadata.

### C. The 4 MLOps Rationale Pillars for Engine Unification:
1. **Zero Cognitive Divergence**: If an operator discusses an ongoing incident in `/chat` while the autonomous `RemediationAgent` investigates in the background, both must interpret logs and data contracts identically. Running two different models would introduce contradictory diagnoses.
2. **Strict Schema Contract Enforced (`_ChatResponse`)**: Even in free conversational mode, the chat endpoint parses the LLM output into a validated Pydantic contract (`answer`, `action_type`, `confidence_score`, `rationale`). This powers the SRE action metadata cards in the UI.
3. **Consolidated FinOps & Zero-Cost Quotas**: Pointing both interfaces to the same OpenRouter or Ollama gateway simplifies credential management, keeps billing at strictly **0.00 EUR**, and unifies Prometheus latency and token tracking under a single dashboard metric (`agentic_ops_llm_requests_total`).
4. **Single-Point Environment Configuration**: SREs never need to update disconnected configurations for conversational tools versus autonomous routines; setting `LLM_MODEL` updates all platform touchpoints in one place.

---

## 7. Zero-Cost Configuration Best Practice

To achieve continuous 24/7 autonomous governance without ever incurring billing costs, set the following configuration in your `.env` file:

```bash
# 1. Primary provider
LLM_PROVIDER=openrouter

# 2. Primary model (High-capacity reasoning with Gemma)
LLM_MODEL=openrouter/google/gemma-4-31b-it:free

# 3. Ordered fallback chain (NVIDIA reasoning -> OpenRouter dynamic router)
LLM_FALLBACK_MODELS=openrouter/nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free,openrouter/openrouter/free

# 4. Temperature set to 0.0 for deterministic outputs
LLM_TEMPERATURE=0.0
LLM_MAX_TOKENS=1024
LLM_TIMEOUT_SECONDS=30
LLM_MAX_RETRIES=3

# 5. OpenRouter API Key (free tier, no credit card required)
OPENROUTER_API_KEY=sk-or-v1-your-key-here
```

### Verification Commands:
```bash
# Check resolved model and active fallback chain
curl -s https://agentic-ops-5ebv.onrender.com/api/llm/status | jq .

# Send a live latency ping through the configured gateway
curl -s -X POST https://agentic-ops-5ebv.onrender.com/api/llm/probe | jq .

# Verify the test suite covering the fallback mechanism
pytest tests/adapters/test_llm_provider_registry.py -v
```

---

## 8. Multi-LLM Cognitive Specialization by Agent Role

Different SRE and MLOps tasks present conflicting cognitive requirements:
- Diagnosing a memory leak or a saturated pod requires ingesting thousands of lines of kernel and `Loki` logs (requiring massive context length).
- Calculating a blast radius and proposing a remediation action requires deliberate step-by-step mathematical reasoning and chain-of-thought verification.
- Validating data contracts and covariance matrices requires low latency and strict schema compliance.
- Interactive SRE web chat requires fast, conversational interaction without internal `<think>` blocks.

To solve this, `Agentic-Ops` implements **Cognitive Specialization by Role** inside `LLMProviderRegistry`:

```ansi
[1;34m+--------------------------------------------------------------------------------------------------+[0m
[1;34m|[0m AGENTIC-OPS CONTROL PLANE — COGNITIVE MULTI-LLM TOPOLOGY                                         [1;34m|[0m
[1;34m+--------------------------------------------------------------------------------------------------+[0m
[1;34m|[0m                                                                                                  [1;34m|[0m
[1;34m|[0m [1;35m[Remediation Coordinator][0m ----> role="remediation" ----> LLM_MODEL_REMEDIATION                  [1;34m|[0m
[1;34m|[0m (Deep Reasoning & CoT)          Fallback: LLM_MODEL      (Default: deepseek-r1:free)             [1;34m|[0m
[1;34m|[0m                                                                                                  [1;34m|[0m
[1;34m|[0m [1;35m[Infra Specialist][0m -----------> role="infra" ----------> LLM_MODEL_INFRA                        [1;34m|[0m
[1;34m|[0m (256k Context Window Logs)      Fallback: LLM_MODEL      (Default: gemma-4-31b-it:free)          [1;34m|[0m
[1;34m|[0m                                                                                                  [1;34m|[0m
[1;34m|[0m [1;35m[Data Specialist][0m ------------> role="data" -----------> LLM_MODEL_DATA                         [1;34m|[0m
[1;34m|[0m (Evidently & Covariance)        Fallback: LLM_MODEL      (Default: gemma-4-26b-a4b-it:free)      [1;34m|[0m
[1;34m|[0m                                                                                                  [1;34m|[0m
[1;34m|[0m [1;35m[Model Specialist][0m -----------> role="model" ----------> LLM_MODEL_MODEL                        [1;34m|[0m
[1;34m|[0m (MLflow F1 Drift & Metrics)     Fallback: LLM_MODEL      (Default: llama-3.3-70b-instruct:free)  [1;34m|[0m
[1;34m|[0m                                                                                                  [1;34m|[0m
[1;34m|[0m [1;35m[Web Chat SRE Assistant][0m -----> role="chat" -----------> LLM_MODEL_CHAT                         [1;34m|[0m
[1;34m|[0m (Interactive Low Latency)       Fallback: LLM_MODEL      (Default: deepseek-chat:free)           [1;34m|[0m
[1;34m|[0m                                                                                                  [1;34m|[0m
[1;34m+--------------------------------------------------------------------------------------------------+[0m
```

### Precedence Hierarchy:
1. **Role Specific**: `LLM_MODEL_{ROLE}`, `LLM_FALLBACK_MODELS_{ROLE}`, `LLM_PROVIDER_{ROLE}`
2. **Global Fallback**: `LLM_MODEL`, `LLM_FALLBACK_MODELS`, `LLM_PROVIDER`
3. **Provider Profile Default**: `PROVIDER_PROFILES[provider]["default_model"]`

### Prometheus Fine-Grained Observability:
All requests record the agent role label:
- `agentic_ops_llm_requests_total{role="infra", provider="openrouter", model="gemma-4-31b-it", status="success"}`
- `agentic_ops_llm_latency_seconds{role="remediation", provider="openrouter", model="deepseek-r1"}`
- `agentic_ops_llm_tokens_total{role="data", provider="openrouter", model="gemma-4-26b-a4b", token_type="total"}`

### Live Inspection:
The active topology across all 5 roles is exposed via `GET /api/llm/status` under the `roles_topology` key.

