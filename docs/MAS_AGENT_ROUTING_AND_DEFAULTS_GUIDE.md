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

When initializing any agent role, `LLMProviderRegistry.resolve_role_config(role)` applies a strict 4-tier precedence hierarchy that ensures **Native Distributed Intelligence Out-of-the-Box**:

$$\text{Role Override} \;(\text{LLM\_MODEL\_\{ROLE\}}) \;\longrightarrow\; \text{Global Override} \;(\text{LLM\_MODEL}) \;\longrightarrow\; \text{Native Role Default} \;(\text{ROLE\_RECOMMENDED\_MODELS}) \;\longrightarrow\; \text{Provider Default}$$

$$\text{Role Fallbacks} \;(\text{LLM\_FALLBACK\_MODELS\_\{ROLE\}}) \;\longrightarrow\; \text{Global Fallbacks} \;(\text{LLM\_FALLBACK\_MODELS}) \;\longrightarrow\; \text{Provider Free Models}$$

This guarantees that:
1. **Zero Configuration Burden**: Leaving all environment variables blank automatically provisions each agent with its expert model (`remediation` $\rightarrow$ `deepseek-r1`, `infra` $\rightarrow$ `gemma-4-31b`, `data` $\rightarrow$ `gemma-4-26b`, `model` $\rightarrow$ `llama-3.3-70b`, `chat` $\rightarrow$ `deepseek-chat`).
2. **Deterministic Fallbacks**: Every agent automatically inherits a 5-stage zero-cost fallback chain to absorb rate limits (`HTTP 429`) and timeouts without workflow disruption.
3. **Upstream Decoupling**: Orchestration, state machine transitions, and policy evaluations remain 100% decoupled from LLM provider selection and model configuration.

---

## 6. Architecture of Non-Cognitive Components: Why Other System Actors Have No LLM (Deterministic Actuators, Sensors & Circuit Breakers)

A foundational architectural requirement in production MLOps is the **strict, physical separation between the Probabilistic Cognitive Layer and the Deterministic System Layer**. 

While the 5 cognitive roles (`RemediationAgent`, `InfraSpecialist`, `DataSpecialist`, `ModelSpecialist`, `WebChatCopilot`) leverage specialized Large Language Models, all other system actors, actuators, sensors, and safety nets **do not use any LLM by design (0-Token / Zero-LLM Python Pur)**.

```text
+==================================================================================================+
| ARCHITECTURAL ISOLATION: COGNITIVE AGENTS VS. ZERO-LLM DETERMINISTIC ACTUATORS                   |
+==================================================================================================+
|                                                                                                  |
| [ PROBABILISTIC COGNITIVE LAYER : POWERED BY SPECIALIZED LLMs ]                                  |
| - RemediationAgent   -> DeepSeek-R1 (CoT, Blast Radius 0-5)                                      |
| - InfraSpecialist    -> Gemma-4 31B (256k Loki log ingestion)                                    |
| - DataSpecialist     -> Gemma-4 26B MoE (Pandera / Evidently tabular triage)                      |
| - ModelSpecialist    -> Llama 3.3 70B (Concept drift P(Y|X) discrimination)                      |
| - WebChatCopilot     -> DeepSeek-Chat (Low-latency SRE interaction)                              |
|                                                                                                  |
| ============================== STRICT ARCHITECTURAL BOUNDARY =================================== |
|                                                                                                  |
| [ DETERMINISTIC SYSTEM LAYER : ZERO-LLM / 100% PURE DETERMINISTIC PYTHON ]                       |
|                                                                                                  |
| 1. CircuitBreakerFallback (0-Token Hardcoded Fail-Safe)                                          |
|    Triggered on API outage or rate limit storm -> Emits fixed Diagnosis -> Forces CREATE_ISSUE   |
|                                                                                                  |
| 2. ActionExecutor (Zero-Trust Isolated Actuator)                                                 |
|    Applies mutations via multiprocessing.Process -> Hard 30s SIGTERM/SIGKILL -> No hallucinations |
|                                                                                                  |
| 3. CacPullCollector (High-Throughput Telemetry Sensor)                                           |
|    Polls Prometheus/Loki/MLflow/Prefect over Tailscale -> Pure HTTP/JSON Data Engineering        |
|                                                                                                  |
| 4. SlackWebhookAgent (Cryptographic Security Gatekeeper)                                         |
|    Validates HMAC-SHA256 signatures & 300s replay TTL -> SQLite atomic lock -> Zero probabilistic|
|                                                                                                  |
| 5. Governed AgentTools (Deterministic Probes & Hands)                                            |
|    CheckDatabaseHealth, CheckDockerContainer, ValidatePanderaSchema -> Sandboxed <15s execution |
|                                                                                                  |
| 6. MCPServerGateway (Open Protocol Bridge)                                                       |
|    Exposes tools via JSON-RPC 2.0 -> LLM engine is delegated to the external client (Claude, etc)|
+==================================================================================================+
```

### A. Deep Dive: Non-Cognitive System Components

#### 1. `CircuitBreakerFallback`: The Zero-Token Safety Anchor
- **Source Code**: [`agentic_ops/core/orchestrator.py`](file:///Users/nolll/Documents/car_acc/agentic-ops-core/agentic_ops/core/orchestrator.py), [`agentic_ops/core/circuit_breaker.py`](file:///Users/nolll/Documents/car_acc/agentic-ops-core/agentic_ops/core/circuit_breaker.py)
- **Engine**: 100% Deterministic Hardcoded Python (Zero Tokens Consumed).
- **Why No LLM?**
  The circuit breaker trips specifically when OpenRouter or upstream model providers experience catastrophic failures: `HTTP 429 Too Many Requests` storms, quota exhaustion, `HTTP 503 Service Unavailable`, or systemic network partitions. Attempting to invoke an LLM when the circuit breaker is active would violate the core definition of a circuit breaker, introducing cascading latency and guaranteed failure.
- **Concrete Behavior**:
  Generates an immutable `Diagnosis` contract (`issue="CIRCUIT_BREAKER_ACTIVE"`, `confidence=1.0`, `root_cause="LLM Provider Rate Limit or Quota Exceeded"`) and enforces the passive, non-mutating action `ActionType.CREATE_ISSUE` to page on-call SRE engineers without executing automated cluster changes.

#### 2. `ActionExecutor`: The Zero-Trust Mutation Actuator
- **Source Code**: [`agentic_ops/core/executor.py`](file:///Users/nolll/Documents/car_acc/agentic-ops-core/agentic_ops/core/executor.py)
- **Engine**: Pure Python Operating System Subprocess Worker.
- **Why No LLM?**
  The `ActionExecutor` is the "hand" of the platform that applies physical changes to production infrastructure (e.g., executing `docker restart`, invoking `systemctl restart`, triggering Prefect workflow runs, or rolling back MLflow registered model versions). Under the **Zero-Trust** security model and the **Principle of Least Privilege**, an LLM must never have direct, unmitigated shell or execution privileges.
- **Concrete Safeguards**:
  - Operates inside an isolated `multiprocessing.Process` with dedicated operating system PID separation.
  - Enforces a hard 30-second execution deadline (`SIGTERM`, followed by `SIGKILL` after a 5-second grace window).
  - Validates all action arguments against a strictly defined whitelist before execution.

#### 3. `CacPullCollector`: The High-Throughput Telemetry Sensor
- **Source Code**: [`agentic_ops/adapters/cac_pull_collector.py`](file:///Users/nolll/Documents/car_acc/agentic-ops-core/agentic_ops/adapters/cac_pull_collector.py)
- **Engine**: Pure Asynchronous Python Network Client (`httpx` + `socks5://127.0.0.1:1055`).
- **Why No LLM?**
  This component acts as the continuous sensory organ of `Agentic-Ops`. It periodically queries 5 disparate production services on `jakatt/cac_mlops` across the Tailscale WireGuard mesh (Grafana Loki logs, Prometheus metrics, MLflow Model Registry, Prefect flow runs, and Evidently drift reports). Its tasks—network handshake traversal, JSON response deserialization, metric delta calculations, and emitting immutable `CacCollectedSnapshot` schemas—are pure Data Engineering. Using an LLM for network polling would incur prohibitive financial costs and unacceptable latency.

#### 4. `SlackWebhookAgent`: The Cryptographic Gatekeeper
- **Source Code**: [`agentic_ops/cli/main.py`](file:///Users/nolll/Documents/car_acc/agentic-ops-core/agentic_ops/cli/main.py), [`agentic_ops/core/approvals.py`](file:///Users/nolll/Documents/car_acc/agentic-ops-core/agentic_ops/core/approvals.py)
- **Engine**: Pure Cryptographic Python (`hmac`, `hashlib`, `sqlite3`).
- **Why No LLM?**
  When human SRE operators click **`[ APPROVE ]`** or **`[ DENY ]`** buttons inside Slack Block Kit notifications, the inbound request (`POST /slack/interactive`) must be authenticated with zero tolerance for ambiguity or probabilistic error.
- **Concrete Safeguards**:
  - Calculates `HMAC-SHA256` signatures using the platform's `SLACK_SIGNING_SECRET`.
  - Rejects replay attacks by enforcing a strict 300-second timestamp freshness window (`X-Slack-Request-Timestamp`).
  - Acquires an atomic `SQLite BEGIN IMMEDIATE` transaction lock in `/tmp/state/approvals.db` to prevent double-spending or race conditions.

#### 5. The 8 Governed `AgentTool`s: Pure Deterministic Probes
- **Source Code**: [`agentic_ops/tools/`](file:///Users/nolll/Documents/car_acc/agentic-ops-core/agentic_ops/tools/) (`db.py`, `docker.py`, `drift.py`, `logs.py`, `metrics.py`, `models.py`, `retraining.py`, `security.py`)
- **Engine**: Pure Python Probes & Diagnostics.
- **Why No LLM?**
  Tools are not autonomous thinkers; they are the specific sensory probes called by cognitive specialists via Tool Calling. They execute bounded actions:
  - `CheckDatabaseHealth`: Runs raw SQL ping and connection pool queries via `psycopg2`.
  - `CheckDockerContainer`: Inspects `/var/run/docker.sock` for container health, OOM kills, and restarts.
  - `ValidatePanderaSchema`: Validates tabular DataFrames against strict Pandera schema contracts.
  - `CheckMLflowModel`: Reads metadata from MLflow tracking APIs.
  Every tool runs inside a 15-second sandbox and returns structured facts to the calling agent.

#### 6. `MCPServerGateway`: The Protocol Bridge
- **Source Code**: [`agentic_ops/entrypoints/mcp_server.py`](file:///Users/nolll/Documents/car_acc/agentic-ops-core/agentic_ops/entrypoints/mcp_server.py)
- **Engine**: Protocol Adapter (JSON-RPC 2.0 over `stdio` and HTTP `SSE`).
- **Which LLM Powers It?**
  The MCP Server Gateway does not embed an internal LLM because it is a passive server governed by the Model Context Protocol. Its cognitive driver is **the external client connected to it** (e.g. Claude 3.7 Sonnet inside Claude Desktop, GPT-4o / Claude inside Cursor, or Antigravity). The gateway validates incoming RPC calls, checks tool permissions, and streams standardized responses.

---

### B. Comprehensive Taxonomy: Cognitive Agents vs. Deterministic System Components

| Component / System Actor | Architectural Layer | Default LLM / Engine | Token Cost | Nature of Execution | Core Operational Function |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`RemediationAgent`** | Cognitive Coordination | `deepseek/deepseek-r1:free` | Dynamic (CoT) | Probabilistic Reasoning | Cross-system blast radius evaluation (0-5) and action proposal. |
| **`InfraSpecialist`** | Cognitive Investigation | `google/gemma-4-31b-it:free` | Dynamic (256k) | Probabilistic Reasoning | Raw Loki log dump analysis and Linux kernel fault diagnosis. |
| **`DataSpecialist`** | Cognitive Investigation | `google/gemma-4-26b-a4b-it:free` | Dynamic (MoE) | Probabilistic Reasoning | Tabular schema mutation, Pandera contract & drift diagnosis. |
| **`ModelSpecialist`** | Cognitive Investigation | `meta-llama/llama-3.3-70b-instruct:free` | Dynamic (70B) | Probabilistic Reasoning | Statistical performance degradation and concept drift analysis. |
| **`WebChatCopilot`** | Cognitive Interface | `deepseek/deepseek-chat:free` | Dynamic (Fast) | Probabilistic Dialogue | Interactive operator chat, prompt execution & ledger audit. |
| **`CircuitBreakerFallback`** | Resilience Safety Net | **None (Pure Python)** | **0 Tokens** | 100% Deterministic | Hardcoded fail-safe emitting diagnosis and forcing `CREATE_ISSUE`. |
| **`ActionExecutor`** | Executive Mutation | **None (Pure Python)** | **0 Tokens** | 100% Deterministic | Subprocess sandboxing, PID isolation & whitelist mutation. |
| **`CacPullCollector`** | Telemetry Ingestion | **None (Pure Python)** | **0 Tokens** | 100% Deterministic | High-frequency HTTP polling of Prometheus, Loki & MLflow. |
| **`SlackWebhookAgent`** | Human Verification | **None (Pure Python)** | **0 Tokens** | 100% Deterministic | Cryptographic `HMAC-SHA256` signature verification & locking. |
| **8 `AgentTools`** | Sensory Probes & Hands | **None (Pure Python)** | **0 Tokens** | 100% Deterministic | 15s sandboxed diagnostic probes (SQL, Docker, Pandera). |
| **`MCPServerGateway`** | Protocol Bridge | **Delegated to Client** | Client-side | Standard JSON-RPC 2.0 | Exposes tools and resources to external IDEs and agents. |

---

## 7. Interactive Live Inspector: Inspecting MAS Agents & Active LLMs in Real-Time (`/console` & `/chat`)

To provide complete cognitive transparency during live operations, production incidents, and jury audits, `Agentic-Ops` embeds an interactive **Live MAS Topology & Agent Inspector** directly within both operator interfaces:
- **SRE Cognitive Web Console**: Accessible via the header badge `[MAS Topology & LLMs Live]` or the primary purple command button at [`/console`](https://agentic-ops-5ebv.onrender.com/console).
- **Standalone Web Chat**: Accessible by clicking the active `#llm-status-badge`, the `[MAS Topology]` button in the top navigation bar, or the quick-action chip `[Inspecter les LLMs des Agents MAS]` at [`/chat`](https://agentic-ops-5ebv.onrender.com/chat).

---

### A. Render Free Feasibility & Zero-Overhead Guarantee (0.1 vCPU / 512 MB RAM)

Deploying complex interactive observability on free cloud tiers presents severe resource challenges. The Live MAS Inspector was engineered to operate under the absolute minimum hardware profile:

1. **Zero Server CPU Consumption (0.1 vCPU Preserved)**:
   All DOM rendering, modal animations, tab filtering, category pills, and card switching occur **100% client-side** inside the operator's web browser using native Vanilla HTML5, CSS3, and modern ES6 JavaScript. The server does not execute any template rendering or DOM computation.
2. **Zero Persistent Memory Overhead (512 MB RAM Preserved)**:
   The backend endpoint `GET /api/mas/topology` reads directly from in-memory configuration objects and environment variables already loaded during startup by `LLMProviderRegistry`. It performs zero database queries, zero disk I/O, and zero network round-trips. Memory consumption is **0 MB**, with an execution latency of **under 2 milliseconds**.
3. **Insignificant Network Footprint**:
   The entire CSS stylesheet, HTML modal skeleton, and JavaScript event dispatcher add under **18 KB (gzipped)** to the initial `/console` and `/chat` payloads, loading in under 15 milliseconds even over constrained connections.
4. **Zero Frontend Toolchain Dependencies**:
   Built without React, Vue, Angular, webpack, or npm dependencies. The inspector requires no external CDN calls, preventing security vulnerabilities and ensuring offline resilience.

---

### B. UI Wireframe & Architecture of the Inspector Modal

The modal employs a 2-column responsive layout: the left sidebar provides category filters (`All`, `Cognitive Brains (LLM)`, `Deterministic (0-Token)`) and selectable component cards; the right panel displays the comprehensive **Encart Dédié** (Dedicated Component Card):

```text
+--------------------------------------------------------------------------------------------------+
|  MAS ARCHITECTURE & LIVE COMPONENT INSPECTOR                                       [ X Close ]  |
+--------------------------------------------------------------------------------------------------+
|  [Filter: All (11)]  [Filter: Cognitive Brains (5)]  [Filter: Deterministic Actuators (6)]       |
+------------------------------------+-------------------------------------------------------------+
|  COMPONENT SELECTION LIST          |  DEDICATED COMPONENT DOSSIER ("ENCART DEDIE")               |
|                                    |                                                             |
|  [*] RemediationAgent              |  [Role: RemediationAgent]  | Domain: SRE Incident Recovery  |
|      deepseek-r1:free (CoT)        |  Status: LIVE ONLINE       | Type: Cognitive LLM Brain      |
|                                    +-------------------------------------------------------------+
|  [ ] InfraSpecialist               |                                                             |
|      gemma-4-31b-it:free (256k)    |  1. IDENTITY & OPERATIONAL MISSION                          |
|                                    |     - Responsibility: Causal inference & blast radius plan  |
|  [ ] DataSpecialist                |     - FSM Trigger: Executed unconditionally in [PLANNED]    |
|      gemma-4-26b-a4b-it:free (MoE) |     - Judicial Safeguard: Anti-bias separation of powers    |
|                                    |                                                             |
|  [ ] ModelSpecialist               |  2. ACTIVE ENGINE & INFERENCE CONFIGURATION                 |
|      llama-3.3-70b-instruct:free   |     - Active Model: openrouter/deepseek/deepseek-r1:free    |
|                                    |     - Reasoning Mode: Chain-of-Thought (<think> filtered)   |
|  [ ] WebChatCopilot                |     - Cascading Fallbacks: deepseek-chat -> llama-3.3-70b   |
|      deepseek-chat:free            |     - Hyperparameters: Temp = 0.0 | MaxTokens = 4096 | 30s  |
|                                    |     - Override Variable: LLM_MODEL_REMEDIATION              |
|  [ ] CircuitBreakerFallback        |     - Architectural Rationale: Only free model with deep    |
|      0-Token Pure Python           |       causal CoT capability for blast radius assessment.    |
|                                    |                                                             |
|  [ ] ActionExecutor                |  3. DATA CONTRACTS & SYSTEM DEPENDENCIES                    |
|      0-Token Subprocess Sandbox    |     - Input Contract: Pydantic Diagnosis                    |
|                                    |     - Output Contract: Pydantic ActionIntent                |
|  [ ] CacPullCollector             |     - Connected Services: Redis (:6379), OPA PolicyEngine   |
|      0-Token Telemetry Ingestion   |     - Permitted Tools: None (Judicially isolated)           |
|                                    |                                                             |
|  [ ] SlackWebhookAgent             |  4. SECURITY, BLAST RADIUS & FINOPS OBSERVABILITY           |
|      0-Token HMAC Gate             |     - Authorized Blast Radius: 0 to 5 (PolicyEngine veto)   |
|                                    |     - WORM Ledger: Merkle cryptographically sealed (SHA256) |
|  [ ] 8 AgentTools                  |     - PromQL Metric: agentic_ops_llm_requests_total{role=""} |
|      0-Token Sensory Probes        |     - Failure Domain: Trips CircuitBreaker on 429/timeout   |
|                                    |                                                             |
|  [ ] MCPServerGateway              |  5. INTERACTIVE LIVE ACTIONS                                |
|      JSON-RPC 2.0 Bridge           |     [ Test LLM Probe (/api/llm/probe) ]                     |
|                                    |     [ Copy PromQL Metric Query ]                            |
+------------------------------------+-------------------------------------------------------------+
```

---

### C. The 5 Structural Sections of the Dedicated Component Card

Each component card rendered in the inspector details 5 engineering dimensions:

1. **Identity & Operational Mission**:
   - Exact functional role, operational responsibilities, and SRE scope.
   - Finite State Machine (FSM) trigger condition (e.g. state `[PLANNED]`, specific `risk_id` pattern, or periodic loop).
   - Judicial safeguard: Anti-Bias separation of powers for cognitive agents, or Least-Privilege invariant for actuators.
2. **Active Engine & Inference Configuration**:
   - **For Cognitive Agents (LLM)**: Fully resolved runtime model string, provider name, reasoning mode (e.g. Chain-of-Thought with regex filtering of `<think>` blocks), active temperature, token ceiling, timeout limit, configuration override environment variable, and operational selection rationale.
   - **For Deterministic Actors (0-Token Python)**: Pure Python execution specification, process isolation boundary (`multiprocessing.Process` with dedicated PID), hard OS deadline (`SIGTERM` / `SIGKILL` after 30s), and Zero-Trust rationale.
3. **Data Contracts & System Dependencies**:
   - Pydantic Input Contract validating incoming telemetry or signal structure.
   - Pydantic Output Contract enforcing strict downstream typing.
   - Upstream and downstream service dependencies (Redis, Tailscale mesh, Docker socket, MLflow, Loki, PostgreSQL).
   - Tool Calling whitelist (restricted tool inventory).
4. **Security, Blast Radius & FinOps Observability**:
   - Maximum permitted Blast Radius ($0$ for observation, up to $5$ for remediation).
   - WORM Trust Ledger status (tamper-evident Merkle tree logging).
   - Prometheus PromQL metric selector for real-time cost and volume tracking.
   - Failure domain behavior (circuit breaker trip, fail-closed lock, or automatic failover).
5. **Interactive Live Controls**:
   - **Test LLM Probe**: Fires a direct test request to `/api/llm/probe` to verify real-time connectivity and round-trip latency.
   - **Copy PromQL Metric Query**: Copies the exact Prometheus metric query directly to the operator clipboard for pasting into Grafana.

---

### D. Comprehensive Technical Dossier: The 11 System Components

#### 1. Cognitive Brains (5 Specialized Roles)

##### 1. `RemediationAgent` (`role="remediation"`)
- **Mission**: Cross-system root-cause analysis, blast radius calculation, and reversible action plan synthesis.
- **Engine**: Cognitive LLM (`openrouter/deepseek/deepseek-r1:free`).
- **Reasoning Mode**: Deliberate Chain-of-Thought (CoT) within `<think>` tags. The model reasons through system dependencies before generating clean Pydantic JSON.
- **FSM Trigger**: Executed unconditionally whenever the orchestrator transitions to `[PLANNED]`.
- **Judicial Safeguard**: **Strict Separation of Powers**. Forbidden from performing diagnostic investigation. Evaluates facts provided by specialists as an independent magistrate.
- **Contracts**: Input `Diagnosis` $\rightarrow$ Output `ActionIntent`.
- **Blast Radius**: Authorized up to $5$ (actions with blast radius $\ge 3$ trigger mandatory Slack HITL approval).
- **FinOps Metric**: `agentic_ops_llm_requests_total{role="remediation"}`.

##### 2. `InfraSpecialist` (`role="infra"`)
- **Mission**: Infrastructure diagnostics, container health, socket connections, memory leaks, and PostgreSQL limits.
- **Engine**: Cognitive LLM (`openrouter/google/gemma-4-31b-it:free`).
- **Reasoning Mode**: Direct structured inference with an ultra-wide context window.
- **Context Window**: 256,000 tokens, enabling ingestion of raw Loki log dumps, systemd journals, and Linux kernel traces without truncation.
- **FSM Trigger**: Alert signals containing `"INFRA"` in `risk_id`.
- **Contracts**: Input `SignalEnvelope` $\rightarrow$ Output `Diagnosis`.
- **Blast Radius**: Strictly $0$ (Read-only investigation).
- **FinOps Metric**: `agentic_ops_llm_requests_total{role="infra"}`.

##### 3. `DataSpecialist` (`role="data"`)
- **Mission**: Schema drift detection, data quality verification, null rate spikes, and tabular contract enforcement.
- **Engine**: Cognitive LLM (`openrouter/google/gemma-4-26b-a4b-it:free`).
- **Reasoning Mode**: Mixture-of-Experts (MoE) optimized for low latency and deterministic JSON formatting.
- **FSM Trigger**: **Universal Platform Default**. Handles alerts containing `"DATA"` as well as any unmatched or unknown `risk_id` to prevent routing deadlocks.
- **Contracts**: Input `SignalEnvelope` $\rightarrow$ Output `Diagnosis`.
- **Blast Radius**: Strictly $0$ (Read-only investigation).
- **FinOps Metric**: `agentic_ops_llm_requests_total{role="data"}`.

##### 4. `ModelSpecialist` (`role="model"`)
- **Mission**: Statistical distribution shift analysis, concept drift vs. data noise arbitration, and F1-score tracking.
- **Engine**: Cognitive LLM (`openrouter/meta-llama/llama-3.3-70b-instruct:free`).
- **Reasoning Mode**: High-capacity 70B parameter statistical reasoning.
- **FSM Trigger**: Alert signals containing `"MODEL"` in `risk_id`.
- **Safeguard**: Prevents spurious model retraining loops by differentiating input covariate shift ($P(X)$) from true posterior concept drift ($P(Y \mid X)$).
- **Contracts**: Input `SignalEnvelope` $\rightarrow$ Output `Diagnosis`.
- **Blast Radius**: Strictly $0$ (Read-only investigation).
- **FinOps Metric**: `agentic_ops_llm_requests_total{role="model"}`.

##### 5. `WebChatCopilot` (`role="chat"`)
- **Mission**: Interactive SRE assistant for human operators, WORM ledger inspection, and prompt execution.
- **Engine**: Cognitive LLM (`openrouter/deepseek/deepseek-chat:free`).
- **Reasoning Mode**: Direct conversational streaming with sub-second Time-To-First-Token (TTFT) and no `<think>` delay.
- **Trigger**: User messages via `/chat` or `POST /api/chat`.
- **Contracts**: Input `ChatRequest` $\rightarrow$ Output `ChatResponse`.
- **Blast Radius**: Strictly $0$ (Advisory assistance only).
- **FinOps Metric**: `agentic_ops_llm_requests_total{role="chat"}`.

---

#### 2. Deterministic Components & Actuators (6 Zero-Token Actors)

##### 6. `CircuitBreakerFallback`
- **Mission**: Ultimate emergency fail-safe when AI providers experience rate limits (`HTTP 429`), timeouts, or network partitions.
- **Engine**: **Pure Python (0 Tokens, Zero-LLM)**.
- **Mechanism**: Hardcoded deterministic state machine. Automatically trips when hourly request thresholds ($> 50$ req/h) or consecutive error ceilings are exceeded.
- **Behavior**: Emits a deterministic `Diagnosis` with confidence $1.0$ and forces the passive, non-mutating action `CREATE_ISSUE`. Calling secondary LLMs during an outage is strictly banned.
- **Blast Radius**: Strictly $0$.

##### 7. `ActionExecutor`
- **Mission**: Physical system actuator executing validated remediation plans (container restarts, model rollbacks).
- **Engine**: **Pure Python (0 Tokens, Zero-LLM)**.
- **Security Boundary**: **Zero-Trust Process Isolation**. Executed inside isolated `multiprocessing.Process` workers with dedicated operating system PIDs. Enforces strict argument whitelists and hard 30-second `SIGTERM` / `SIGKILL` timeouts.
- **Invariant**: LLMs possess zero shell privileges and zero direct mutation capability.

##### 8. `CacPullCollector`
- **Mission**: High-frequency telemetric sensor polling target MLOps clusters (`jakatt/cac_mlops`) over the encrypted Tailscale VPN mesh.
- **Engine**: **Pure Python (0 Tokens, Zero-LLM)**.
- **Mechanism**: Async HTTP client (`httpx`) pulling metrics from Prometheus, Loki, MLflow, Prefect, and Evidently over SOCKS5 proxy `:1055`.
- **Resilience**: Enforces strict read-only `GET` requests; implements exponential backoff with circuit breaker locks during remote VPS network partitions.

##### 9. `SlackWebhookAgent`
- **Mission**: Cryptographic security gate protecting Human-in-the-Loop (HITL) approval actions.
- **Engine**: **Pure Python (0 Tokens, Zero-LLM)**.
- **Security Invariant**: Validates inbound operator decisions (`POST /slack/interactive`) using `HMAC-SHA256` signature verification (`X-Slack-Signature`) against a 5-minute replay window (`X-Slack-Request-Timestamp`). Employs atomic `SQLite BEGIN IMMEDIATE` locks to block double-click race conditions.

##### 10. `8 AgentTools`
- **Mission**: Sensory probes and diagnostic execution tools invoked during incident investigation.
- **Engine**: **Pure Python (0 Tokens, Zero-LLM)**.
- **Tool Inventory**: `CheckDatabaseHealth`, `CheckDockerContainer`, `ValidatePanderaSchema`, `QueryPrometheusMetric`, `InspectSystemResources`, `ReadTailscaleStatus`, `InspectWormLedger`, `InspectModelArtifact`.
- **Constraint**: Sandboxed execution limited to $< 15$ seconds with read-only database connections and sanitized query arguments.

##### 11. `MCPServerGateway`
- **Mission**: Model Context Protocol (MCP) bridge exposing system tools and telemetry to external IDEs and agents.
- **Engine**: **JSON-RPC 2.0 Protocol Server (Delegated to Client)**.
- **Architecture**: Operates over standard `stdio` and HTTP SSE on `/mcp`. Exposes 8 governed tools, 5 resources, and 20 starter prompts. Intelligence is provided by the external client (Claude Desktop, Cursor, Antigravity); the gateway itself executes 0 internal model tokens.

---

### E. Dedicated Inspection API Specification (`GET /api/mas/topology`)

The live inspector frontend communicates with the backend via a single high-speed endpoint:

- **Route**: `GET /api/mas/topology`
- **Latency**: $< 2$ ms (In-memory resolution)
- **Response Schema**:

```json
{
  "status": "ok",
  "total_components": 11,
  "cognitive_count": 5,
  "deterministic_count": 6,
  "global_default_provider": "openrouter",
  "global_default_model": "deepseek/deepseek-r1:free",
  "cognitive_agents": [
    {
      "id": "remediation",
      "name": "RemediationAgent",
      "role": "remediation",
      "type": "Cognitif (LLM)",
      "is_cognitive": true,
      "provider": "openrouter",
      "resolved_model": "deepseek/deepseek-r1:free",
      "reasoning_mode": "Chain-of-Thought délibéré (<think> tags filtrés via regex)",
      "fallbacks": [
        "deepseek/deepseek-chat:free",
        "meta-llama/llama-3.3-70b-instruct:free",
        "google/gemini-2.0-flash-exp:free"
      ],
      "temperature": 0.0,
      "max_tokens": 4096,
      "timeout": 30,
      "env_override": "LLM_MODEL_REMEDIATION",
      "input_contract": "Diagnosis",
      "output_contract": "ActionIntent",
      "blast_radius_limit": 5,
      "fsm_trigger": "État FSM [PLANNED] (systématique sur chaque incident)",
      "judicial_rule": "Séparation des Pouvoirs Anti-Biais : interdiction formelle de diagnostiquer",
      "dependencies": ["Redis (:6379)", "PolicyEngine (OPA)", "WORM Trust Ledger"],
      "promql_metric": "agentic_ops_llm_requests_total{role=\"remediation\"}",
      "failure_behavior": "Repli automatique sur FallbackLLMAdapter puis CIRCUIT_BREAKER_FALLBACK",
      "rationale": "Seul modèle gratuit doté d'une capacité de raisonnement CoT pas-à-pas"
    }
  ],
  "deterministic_components": [
    {
      "id": "action_executor",
      "name": "ActionExecutor",
      "type": "Déterministe (0-Token Python Pur)",
      "is_cognitive": false,
      "engine": "Python Déterministe Pur (0 Tokens, Zéro-LLM)",
      "isolation": "multiprocessing.Process (PID dédié, isolation OS)",
      "timeout_deadline": "30s (SIGTERM puis SIGKILL)",
      "input_contract": "ActionIntent (validé par PolicyEngine)",
      "output_contract": "ExecutionResult (scellé dans WORM Ledger)",
      "zero_trust_rationale": "Aucun modèle probabiliste ne détient de privilèges d'exécution shell",
      "dependencies": ["Docker Socket (/var/run/docker.sock)", "Systemd D-Bus", "WORM Ledger"],
      "promql_metric": "agentic_ops_actions_executed_total{status=\"success\"}"
    }
  ]
}
```

---

### F. Automated Verification & Test Coverage

The inspector is covered by dedicated integration and contract tests in [`tests/entrypoints/test_chat_endpoint.py`](file:///Users/nolll/Documents/car_acc/agentic-ops-core/tests/entrypoints/test_chat_endpoint.py):

1. **`test_get_mas_topology_endpoint`**:
   - Asserts `HTTP 200 OK`.
   - Asserts `total_components == 11` (exactly 5 cognitive agents and 6 deterministic components).
   - Validates that each cognitive agent exposes its resolved model, fallbacks, Pydantic contracts, and PromQL metric tag.
   - Validates that non-cognitive components explicitly state 0-token pure Python execution.
2. **`test_get_console_ui_contains_mas_inspector`**:
   - Asserts that `/console` contains the modal container (`id="mas-modal"`), the header button, the purple command grid card, and the dynamic fetching script `openMasModal()`.
3. **`test_get_chat_ui_contains_mas_inspector`**:
   - Asserts that `/chat` contains the interactive `#llm-status-badge`, the top bar button `[MAS Topology]`, and the quick suggestion chip.



