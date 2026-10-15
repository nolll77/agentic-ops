# Multi-Agent System (MAS) Agent Selection & Default Routing Architecture

> **Module Entrypoint**: [`agentic_ops/core/orchestrator.py`](file:///Users/nolll/Documents/car_acc/agentic-ops-core/agentic_ops/core/orchestrator.py), [`agentic_ops/core/specialist.py`](file:///Users/nolll/Documents/car_acc/agentic-ops-core/agentic_ops/core/specialist.py), [`agentic_ops/core/model_specialist.py`](file:///Users/nolll/Documents/car_acc/agentic-ops-core/agentic_ops/core/model_specialist.py), [`agentic_ops/core/infra_specialist.py`](file:///Users/nolll/Documents/car_acc/agentic-ops-core/agentic_ops/core/infra_specialist.py), [`agentic_ops/core/remediation_agent.py`](file:///Users/nolll/Documents/car_acc/agentic-ops-core/agentic_ops/core/remediation_agent.py)
> **Cognitive Provider Registry**: [`agentic_ops/adapters/llm_provider_registry.py`](file:///Users/nolll/Documents/car_acc/agentic-ops-core/agentic_ops/adapters/llm_provider_registry.py)
> **Verification Test Suites**: [`tests/adapters/test_llm_provider_registry.py`](file:///Users/nolll/Documents/car_acc/agentic-ops-core/tests/adapters/test_llm_provider_registry.py), [`tests/scenarios/test_scenarios.py`](file:///Users/nolll/Documents/car_acc/agentic-ops-core/tests/scenarios/test_scenarios.py)

---

## 1. Architectural Philosophy: Separation of Cognitive Concerns (SoC)

In production MLOps and SRE environments, deploying a monolithic, single-agent system that handles detection, investigation, planning, and user interaction creates critical architectural anti-patterns:
1. **Cognitive Overfitting & Hallucination Risk**: An agent tasked simultaneously with parsing high-volume system logs and formulating high-stakes rollback plans suffers from conflicting context window priorities.
2. **Lack of Judicial Separation (Judge vs. Executioner Anti-Pattern)**: If the agent diagnosing an anomaly also possesses unilateral authority to execute destructive mutations, false positives trigger immediate outages.
3. **Sub-optimal Cost & Latency Allocation**: Routing basic tabular schema validation through a 671-billion parameter DeepSeek-R1 reasoning model is economically wasteful and operationally sluggish.

To resolve these challenges, `Agentic-Ops` implements a **Multi-Agent System (MAS)** architected on two non-negotiable principles:
- **Strict Separation of Diagnostic Investigation and Remediation Planning**: Specialists investigate anomalies and emit a typed `Diagnosis` contract. The `RemediationAgent` receives this factual evidence out-of-band and formulates an `ActionIntent` proposal.
- **Deterministic Risk Taxonomy Routing with Safe Defaults**: Agent assignment is governed by explicit taxonomic routing rules in `Orchestrator._get_specialist()`. Any unknown or unclassified incident is captured by the default fallback specialist.

```text
+--------------------------------------------------------------------------------------------------+
| AGENTIC-OPS MAS AGENT TOPOLOGY & FLOW PIPELINE                                                   |
+--------------------------------------------------------------------------------------------------+
|                                                                                                  |
|                                       [Incoming Incident Signal]                                 |
|                                     (risk_id, signal_id, metrics)                                |
|                                                    |                                             |
|                                                    v                                             |
|                                   +----------------------------------+                           |
|                                   |  Orchestrator Routing Mechanism  |                           |
|                                   |     _get_specialist(risk_id)     |                           |
|                                   +----------------------------------+                           |
|                                                    |                                             |
|                    +-------------------------------+-------------------------------+             |
|                    |                               |                               |             |
|         "MODEL" in risk_id.upper()      "INFRA" in risk_id.upper()           Default / Fallback   |
|                    |                               |                               |             |
|                    v                               v                               v             |
|         +---------------------+         +---------------------+         +---------------------+  |
|         |   ModelSpecialist   |         |   InfraSpecialist   |         |   DataSpecialist    |  |
|         |  (role="model")     |         |  (role="infra")     |         |  (role="data")      |  |
|         |  MLflow / F1 Drift  |         |  Loki / Kernel Logs |         | [DEFAULT AGENT]     |  |
|         +---------------------+         +---------------------+         +---------------------+  |
|                    \                               |                               /             |
|                     \                              |                              /              |
|                      +-----------------------------+-----------------------------+               |
|                                                    |                                             |
|                                                    v Emits Diagnosis Contract                    |
|                                   +----------------------------------+                           |
|                                   |         RemediationAgent         |                           |
|                                   |       (role="remediation")       |                           |
|                                   |  Evaluates Blast Radius (CoT)    |                           |
|                                   +----------------------------------+                           |
|                                                    |                                             |
|                                                    v Emits ActionIntent Contract                 |
|                                   +----------------------------------+                           |
|                                   |           PolicyEngine           |                           |
|                                   |    (Zero-Trust OPA Gatekeeper)   |                           |
|                                   +----------------------------------+                           |
|                                                    |                                             |
|                    +-------------------------------+-------------------------------+             |
|                    |                                                               |             |
|                    v DecisionEnum.ALLOW                                            v             |
|         +---------------------+                                         +---------------------+  |
|         | ActionExecutor      |                                         | Slack HITL Workflow |  |
|         | (Safe Subprocess)   |                                         | (Awaiting Approval) |  |
|         +---------------------+                                         +---------------------+  |
|                                                                                                  |
| [Independent Conversational Track]                                                               |
| Web Chat Copilot (/chat) -> role="chat" (Fast-response, non-blocking operator interface)          |
+--------------------------------------------------------------------------------------------------+
```

---

## 2. Agent Catalog & Default Selection Breakdown

The MAS architecture defines 5 distinct agent roles across 3 operational layers:

| Agent Class / Role | Layer / Responsibility | Trigger / Routing Match | Default Assigned LLM Model | Override Env Variable |
| :--- | :--- | :--- | :--- | :--- |
| **`DataSpecialist`**<br>(`role="data"`) | Investigation: Data Quality & Schema Integrity | **MAS DEFAULT** / Any `risk_id` without `"MODEL"` or `"INFRA"` | `openrouter/google/gemma-4-26b-a4b-it:free` | `LLM_MODEL_DATA` |
| **`ModelSpecialist`**<br>(`role="model"`) | Investigation: ML Degradation & Concept Drift | `"MODEL" in risk_id.upper()` | `openrouter/meta-llama/llama-3.3-70b-instruct:free` | `LLM_MODEL_MODEL` |
| **`InfraSpecialist`**<br>(`role="infra"`) | Investigation: SRE, Kernel & Docker Compute | `"INFRA" in risk_id.upper()` | `openrouter/google/gemma-4-31b-it:free` | `LLM_MODEL_INFRA` |
| **`RemediationAgent`**<br>(`role="remediation"`) | Coordination: Blast Radius & Action Planning | Called systematically during FSM state `PLANNED` | `openrouter/deepseek/deepseek-r1:free` | `LLM_MODEL_REMEDIATION` |
| **`WebChatCopilot`**<br>(`role="chat"`) | Interface: Human Operator Assistance | Interactive endpoints (`/chat`, `POST /api/chat`) | `openrouter/deepseek/deepseek-chat:free` | `LLM_MODEL_CHAT` |

---

## 3. Deep Dive: Investigation Specialists

### A. The MAS Default Agent: `DataSpecialist` (`role="data"`)
- **Source Code**: [`agentic_ops/core/specialist.py`](file:///Users/nolll/Documents/car_acc/agentic-ops-core/agentic_ops/core/specialist.py)
- **Routing Precedence**: Catch-all default in `Orchestrator._get_specialist()`.
- **Why DataSpecialist is the Platform Default**:
  1. **Empirical MLOps Statistics**: Historical post-mortems show that over 80% of production ML failures originate in data pipelines (Pandera schema mutations, missing columns, upstream sensor drops, unannounced API changes in tabular inputs).
  2. **Safe Fallback Anchor**: If an external monitoring source transmits a custom, corrupted, or unclassified alert (e.g. `UNKNOWN_ANOMALY_42` or `CUSTOM_PIPELINE_STALL`), assigning it to `DataSpecialist` ensures that data integrity, missing fields, and distribution bounds are evaluated first before considering invasive model rollbacks or container restarts.
- **Prompt Architecture & Contract**: Injects observed signal metrics (`value`, `threshold`, `source`, `dimensions`) and produces a strictly typed `Diagnosis` contract with confidence score and evidence references.
- **Default Cognitive Profile**: `google/gemma-4-26b-a4b-it:free` — Fast, instruction-tuned, optimized for structured tabular reasoning without unnecessary thinking overhead.

### B. The ML Degredation Specialist: `ModelSpecialist` (`role="model"`)
- **Source Code**: [`agentic_ops/core/model_specialist.py`](file:///Users/nolll/Documents/car_acc/agentic-ops-core/agentic_ops/core/model_specialist.py)
- **Routing Precedence**: Activated when `"MODEL" in risk_id.upper()` (e.g. `MODEL_PERF_DEGRADATION`, `MODEL_CONCEPT_DRIFT`, `MODEL_PREDICTION_BIAS`).
- **Domain Focus**: Specializes in evaluating statistical performance shifts. In the BAAC road safety domain, this corresponds to tracking F1-Score degradation on minority classes (fatalities and severe injuries) against the MLflow Model Registry baseline.
- **Prompt Architecture & Contract**: Tailored to differentiate true concept drift (statistical divergence in $P(Y \mid X)$) from transient feature anomalies ($P(X)$).
- **Default Cognitive Profile**: `meta-llama/llama-3.3-70b-instruct:free` — High parameter capacity (70B) providing deep contextual understanding of statistical trade-offs and confusion matrices.

### C. The SRE & Compute Specialist: `InfraSpecialist` (`role="infra"`)
- **Source Code**: [`agentic_ops/core/infra_specialist.py`](file:///Users/nolll/Documents/car_acc/agentic-ops-core/agentic_ops/core/infra_specialist.py)
- **Routing Precedence**: Activated when `"INFRA" in risk_id.upper()` (e.g. `INFRA_OOM_KILLED`, `INFRA_LATENCY_SPIKE`, `INFRA_POSTGRES_MAX_CONN`).
- **Domain Focus**: System resources, networking, container lifecycles, and database health. Diagnoses PostgreSQL connection exhaustion, Redis locks, Docker memory pressure, and Tailscale mesh reachability.
- **Prompt Architecture & Contract**: Focuses on resource threshold breaches, socket saturation, and Linux kernel signals.
- **Default Cognitive Profile**: `google/gemma-4-31b-it:free` — Exceptional 256,000-token context window allowing raw ingestion of high-density Loki log streams without prior truncation.

---

## 4. Deep Dive: Coordination & Interaction Roles

### A. The Action Coordinator: `RemediationAgent` (`role="remediation"`)
- **Source Code**: [`agentic_ops/core/remediation_agent.py`](file:///Users/nolll/Documents/car_acc/agentic-ops-core/agentic_ops/core/remediation_agent.py)
- **Execution Point**: Triggered exclusively during FSM state `PLANNED` in `Orchestrator.run()`.
- **Architectural Safeguard (Anti-Bias Design)**:
  - Specialists are strictly forbidden from choosing or proposing actions. They only emit diagnostic findings.
  - The `RemediationAgent` acts as an independent magistrate: it reviews the findings, cross-examines the specialist's confidence score, and determines the most proportional remediation action (`INVESTIGATE`, `CREATE_ISSUE`, `PROPOSE_RETRAIN`, `ROLLBACK_PROD`, `ISOLATE_CONTAINER`).
  - It autonomously computes the `declared_blast_radius` (integer 0 to 5) and assesses operational reversibility before forwarding the intent to the `PolicyEngine`.
- **Default Cognitive Profile**: `deepseek/deepseek-r1:free` — Advanced Chain-of-Thought (CoT) reasoning model. Performs extensive multi-step reflection within `<think>` tags to calculate secondary impact risks before returning the validated `ActionIntent`.

### B. The Conversational Copilot: `WebChatCopilot` (`role="chat"`)
- **Source Code**: [`agentic_ops/cli/main.py`](file:///Users/nolll/Documents/car_acc/agentic-ops-core/agentic_ops/cli/main.py)
- **Execution Point**: Activated by HTTP `POST /api/chat` and `/chat`.
- **Operational Requirements**:
  - Requires low time-to-first-token (TTFT) and high interactivity for SRE operators.
  - Bypasses CoT reasoning loops to provide immediate answers, query WORM ledger records, and execute the 20 MCP starter prompts.
- **Default Cognitive Profile**: `deepseek/deepseek-chat:free` — High-speed conversational agent with zero thinking delay.

---

## 5. Fallback Hierarchy & Precedence Rules

When initializing any agent role, `LLMProviderRegistry.resolve_role_config(role)` applies a strict fallback hierarchy:

$$\text{Role Override} \;(\text{LLM\_MODEL\_\{ROLE\}}) \;\longrightarrow\; \text{Global Model} \;(\text{LLM\_MODEL}) \;\longrightarrow\; \text{Provider Default Model}$$

$$\text{Role Fallbacks} \;(\text{LLM\_FALLBACK\_MODELS\_\{ROLE\}}) \;\longrightarrow\; \text{Global Fallbacks} \;(\text{LLM\_FALLBACK\_MODELS}) \;\longrightarrow\; \text{Provider Free Models}$$

This guarantees that:
1. Omitting role-specific environment variables never causes a failure.
2. Every agent automatically inherits zero-cost fallback resilience.
3. Upstream orchestration code remains completely agnostic to provider and model selection.
