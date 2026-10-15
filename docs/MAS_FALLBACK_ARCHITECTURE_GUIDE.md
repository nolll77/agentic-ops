# Multi-Agent System (MAS) Fallback Architecture & Mapping Keys

> **Module Entrypoint**: [`agentic_ops/core/orchestrator.py`](file:///Users/nolll/Documents/car_acc/agentic-ops-core/agentic_ops/core/orchestrator.py), [`agentic_ops/adapters/llm_provider_registry.py`](file:///Users/nolll/Documents/car_acc/agentic-ops-core/agentic_ops/adapters/llm_provider_registry.py), [`agentic_ops/core/circuit_breaker.py`](file:///Users/nolll/Documents/car_acc/agentic-ops-core/agentic_ops/core/circuit_breaker.py), [`agentic_ops/core/policy_engine.py`](file:///Users/nolll/Documents/car_acc/agentic-ops-core/agentic_ops/core/policy_engine.py)
> **Governance Manifests**: [`autonomy_policy.yaml`](file:///Users/nolll/Documents/car_acc/agentic-ops-core/agentic_ops/governance/autonomy_policy.yaml), [`action_catalog.yaml`](file:///Users/nolll/Documents/car_acc/agentic-ops-core/agentic_ops/governance/action_catalog.yaml), [`risk_register.yaml`](file:///Users/nolll/Documents/car_acc/agentic-ops-core/agentic_ops/governance/risk_register.yaml)
> **Verification Test Suites**: [`tests/adapters/test_llm_provider_registry.py`](file:///Users/nolll/Documents/car_acc/agentic-ops-core/tests/adapters/test_llm_provider_registry.py), [`tests/scenarios/test_scenarios.py`](file:///Users/nolll/Documents/car_acc/agentic-ops-core/tests/scenarios/test_scenarios.py), [`tests/adapters/test_cac_pull_collector.py`](file:///Users/nolll/Documents/car_acc/agentic-ops-core/tests/adapters/test_cac_pull_collector.py)

---

## 1. Executive Summary & SRE Resilience Principles

An autonomous Multi-Agent System (MAS) operating in production cannot assume nominal conditions. In real-world enterprise infrastructure, external model providers rate-limit, networks partition, monitoring storms flood message buses, and autonomous agents risk cascading hallucinations.

In `Agentic-Ops`, resilience is not an afterthought: **the MAS architecture is structured around 5 cascading Fallback Layers**. Every layer enforces a deterministic fail-safe or fail-closed state, ensuring that:
1. Zero unhandled exceptions propagate to the caller or break FSM execution.
2. Zero unauthorized or unverified mutations execute in production (`0/6` forbidden actions executed across all tests).
3. The platform degrades gracefully to passive ticketing (`ActionType.CREATE_ISSUE`) or human-in-the-loop review (`DecisionEnum.REQUIRE_APPROVAL`) whenever an anomaly or budget breach occurs.

```text
+--------------------------------------------------------------------------------------------------+
| AGENTIC-OPS MAS ARCHITECTURE — 5 CASCADING FALLBACK LAYERS                                        |
+--------------------------------------------------------------------------------------------------+
|                                                                                                  |
| [1. COGNITIVE LAYER]      Primary Role LLM -> Fallback 1 -> Fallback 2 -> Provider Defaults     |
|                           (FallbackLLMAdapter / HTTP 429 & Timeout Failover)                     |
|                                                                                                  |
| [2. FINOPS & SECOPS]      Hourly Quota Exceeded -> CIRCUIT_BREAKER_FALLBACK                      |
|                           (Forces safe ActionType.CREATE_ISSUE / Zero LLM mutation)              |
|                                                                                                  |
| [3. SPECIALIST ROUTING]   MODEL_* -> ModelSpecialist | INFRA_* -> InfraSpecialist                |
|                           Unmatched Risk ID -> Fallback to DataSpecialist                        |
|                                                                                                  |
| [4. GOVERNANCE LAYER]     PolicyEngine Default: default_effect="deny" (Fail-Closed)              |
|                           Blast Radius > 0 -> Fallback from Auto-Allow to Slack HITL             |
|                                                                                                  |
| [5. NETWORK & TARGET]     Scaleway / Tailscale Remote Target Offline                             |
|                           -> RemoteServiceStatus.REMOTE_TARGET_OFFLINE (Zero crash, Safe-Lock)   |
|                                                                                                  |
+--------------------------------------------------------------------------------------------------+
```

---

## 2. Layer 1: Cognitive Model & Provider Fallbacks (`FallbackLLMAdapter`)

The cognitive reasoning engine is protected against rate-limiting (`HTTP 429 Too Many Requests`), provider outages, and timeouts by `FallbackLLMAdapter` in [`agentic_ops/adapters/llm_protocol.py`](file:///Users/nolll/Documents/car_acc/agentic-ops-core/agentic_ops/adapters/llm_protocol.py).

### A. Fallback Chain Mechanics
1. The primary model configured for the role is queried first (e.g., `openrouter/deepseek/deepseek-r1:free`).
2. If it raises any exception (`AuthenticationError`, `RateLimitError`, `TimeoutException`, `5xx`), `FallbackLLMAdapter` catches the error, records a failure metric in Prometheus, and immediately queries the next model in `LLM_FALLBACK_MODELS_{ROLE}`.
3. If no role-specific fallback chain is specified, it inherits the global `LLM_FALLBACK_MODELS`.
4. If no global fallback is configured and OpenRouter is used, it falls back to the catalog of free models (`profile["free_models"]`).

### B. Exact Mapping Keys
| Fallback Level | Configuration Key (Env Variable) | Fallback Target / Code Precedence |
| :--- | :--- | :--- |
| **Role Primary Model** | `LLM_MODEL_{ROLE}` | Falls back to global `LLM_MODEL` |
| **Global Primary Model** | `LLM_MODEL` | Falls back to `PROVIDER_PROFILES[provider]["default_model"]` |
| **Role Fallback Chain** | `LLM_FALLBACK_MODELS_{ROLE}` | Falls back to global `LLM_FALLBACK_MODELS` |
| **Global Fallback Chain** | `LLM_FALLBACK_MODELS` | Falls back to `PROVIDER_PROFILES[provider]["free_models"]` |
| **Role Provider Selector**| `LLM_PROVIDER_{ROLE}` | Falls back to `LLM_PROVIDER` $\rightarrow$ `"openrouter"` |

*Supported Role Values*: `{ROLE}` $\in$ `REMEDIATION`, `INFRA`, `DATA`, `MODEL`, `CHAT`.

---

## 3. Layer 2: FinOps & SecOps Circuit Breaker Fallback (`LLMCircuitBreaker`)

To prevent catastrophic token consumption loops during monitoring storms or recursive prompt injection attacks, [`LLMCircuitBreaker`](file:///Users/nolll/Documents/car_acc/agentic-ops-core/agentic_ops/core/circuit_breaker.py) continuously tracks LLM call frequency on a sliding hourly window.

### A. Degraded Mode Activation
- **Threshold**: Set by default to `max_calls_per_hour = 50`.
- **Condition**: If calls exceed the budget, `global_circuit_breaker.is_tripped()` becomes `True`.
- **Orchestrator Interception**: `Orchestrator.run()` halts normal specialist LLM diagnosis and swaps in a deterministic degraded diagnosis:
  ```python
  diagnosis = Diagnosis(
      risk_id=risk_id,
      agent="CIRCUIT_BREAKER_FALLBACK",
      confidence=1.0,
      findings=[Finding(description="LLM Circuit Breaker activé. Mode dégradé.")]
  )
  forced_action = ActionType.CREATE_ISSUE
  ```

### B. Exact Mapping Keys
| Architecture Component | Code Mapping Key | Value / Behavior Under Fallback |
| :--- | :--- | :--- |
| **Circuit Breaker State** | `global_circuit_breaker.is_tripped()` | `True` when budget breached, auto-resets when window cools |
| **Specialist Name** | `diagnosis.agent` | `"CIRCUIT_BREAKER_FALLBACK"` (zero LLM token spend) |
| **Remediation Action** | `forced_action` | `ActionType.CREATE_ISSUE` (strictly non-mutating) |
| **Prometheus Gauge** | `CIRCUIT_BREAKER_STATUS` | `1` (tripped) / `0` (healthy) |

---

## 4. Layer 3: Dynamic Specialist Routing Fallback (`Orchestrator._get_specialist`)

The `Orchestrator` dynamically selects the domain specialist based on the incoming `risk_id` taxonomy prefix.

### A. Routing Logic
1. If `MODEL` is in `risk_id.upper()` $\rightarrow$ Instantiates `ModelSpecialist(llm=_get_llm_for_role("model"))`.
2. If `INFRA` is in `risk_id.upper()` $\rightarrow$ Instantiates `InfraSpecialist(llm=_get_llm_for_role("infra"))`.
3. **Fallback Condition**: Any other risk prefix (e.g., `DATA_*`, `DRIFT_*`, custom unfamiliar risks) automatically falls back to `DataSpecialist(llm=_get_llm_for_role("data"))`.

### B. Exact Mapping Keys
| Risk Condition | Code Mapping Key | Specialist Agent Injected |
| :--- | :--- | :--- |
| Machine Learning Metric Risk | `"MODEL" in risk_id.upper()` | `ModelSpecialist` (`role="model"`) |
| Infrastructure / SRE Risk | `"INFRA" in risk_id.upper()` | `InfraSpecialist` (`role="infra"`) |
| **Unmatched Default Fallback** | **`else`** | **`DataSpecialist` (`role="data"`)** |

---

## 5. Layer 4: Governance & Policy Engine Fallbacks (`Fail-Closed`)

Autonomous agents propose actions via Pydantic `ActionIntent`. However, execution is strictly governed by `PolicyEngine` ([`agentic_ops/core/policy_engine.py`](file:///Users/nolll/Documents/car_acc/agentic-ops-core/agentic_ops/core/policy_engine.py)) and declarative YAML bundles.

### A. Fail-Closed Default Fallback
In [`autonomy_policy.yaml`](file:///Users/nolll/Documents/car_acc/agentic-ops-core/agentic_ops/governance/autonomy_policy.yaml), the policy file sets:
```yaml
schema_version: 2
default_effect: deny
```
If an action is requested and no explicit rule grants `ALLOW`, the engine defaults to `DecisionEnum.DENY`. The FSM transitions to `DENIED` with zero mutations allowed.

### B. Autonomy Downgrade to Human Gate (`REQUIRE_APPROVAL`)
- **L1 Actions** (Zero blast radius, fully reversible tickets like `create_issue`): `DecisionEnum.ALLOW` $\rightarrow$ FSM `RESOLVED`.
- **L2/L3 Actions** (Mutating infrastructure like `restart_pod`, `scale_up`): Fallback from autonomous execution to `DecisionEnum.REQUIRE_APPROVAL` $\rightarrow$ FSM `AWAITING_APPROVAL` (Slack modal with HMAC verification).
- **Upstream Data Corruption Rule (`R-001`)**: If an upstream data pipeline anomaly is detected, any LLM proposal attempting to mutate serving pods or retrain models is vetoed: fallback to `DecisionEnum.DENY`.

### C. Exact Mapping Keys
| Policy Condition | Mapping Key in YAML / Code | Governance Outcome |
| :--- | :--- | :--- |
| **Default Root Effect** | `default_effect: "deny"` | `DecisionEnum.DENY` (Fail-Closed) |
| **Mutating Action** | `effect: "require_approval"` | `DecisionEnum.REQUIRE_APPROVAL` (Slack HITL) |
| **Corrupted Telemetry** | `rule: "risk_register_forbids"` | `DecisionEnum.DENY` (Veto Amont overrides IA) |
| **Whitelisted Target Check** | `target_pattern: "^[a-z0-9_-]+$"` | Shell injection fails regex $\rightarrow$ `DecisionEnum.DENY` |

---

## 6. Layer 5: Network Partition & Remote Target Fallbacks (`CacPullCollector`)

When `Agentic-Ops` supervises a remote target (e.g., external VPS on Scaleway over Tailscale), network partitions or host outages can occur at any time.

### A. Exception Interception
[`CacPullCollector`](file:///Users/nolll/Documents/car_acc/agentic-ops-core/agentic_ops/adapters/cac_pull_collector.py) wraps all 5 remote telemetry sources (`Loki`, `Prometheus`, `MLflow`, `Prefect`, `Evidently`) in defensive try-except blocks catching `httpx.ConnectError`, `httpx.ConnectTimeout`, and `httpx.ReadTimeout`.

### B. Degradation Behavior
- Rather than throwing an unhandled exception or crashing FastAPI, the collector records `RemoteServiceStatus.REMOTE_TARGET_OFFLINE`.
- The snapshot endpoint returns `{"status": "offline"}` with HTTP 200.
- The governance engine activates a **Fail-Closed Execution Lock**: mutating actions targeting a disconnected service are blocked immediately.

### C. Exact Mapping Keys
| Network Event | Code Mapping Key | System Status |
| :--- | :--- | :--- |
| Connection Refused / Timeout | `httpx.ConnectError`, `httpx.TimeoutException` | Intercepted in `_safe_get()` |
| Collector Service Status | `RemoteServiceStatus.REMOTE_TARGET_OFFLINE` | `status = "offline"` |
| Target Ingestion Metadata | `metadata["status"]` | `"degraded"` / `"offline"` |
| Execution Gate | `target_is_reachable()` | `False` $\rightarrow$ Mutating action rejected |

---

## 7. Verification Test Coverage

The 5 fallback layers are validated across the test suite:

```bash
# 1. Test LLM Provider Registry Fallback Chains & Role Resolution (15 passed)
pytest tests/adapters/test_llm_provider_registry.py -v

# 2. Test CAC Connector Target Offline Resilience (13 passed)
pytest tests/adapters/test_cac_pull_collector.py -v

# 3. Test Policy Engine Fail-Closed & Veto Governance (20 passed)
pytest tests/policy/test_policy_engine.py -v

# 4. Test End-to-End Scenarios Proving Forbidden Execution is 0 (10 passed)
pytest tests/scenarios/test_scenarios.py -v
```
