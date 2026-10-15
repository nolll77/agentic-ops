# Target Outage & Network Resilience Guide (Scaleway / Tailscale Degradation)

> **Module Entrypoint**: `agentic_ops/adapters/cac_pull_collector.py` & `agentic_ops/cli/main.py`
> **Live Diagnostic Endpoint**: `https://agentic-ops-5ebv.onrender.com/api/cac/snapshot?timeout=3.5`
> **Live Tailscale Diagnostics**: `https://agentic-ops-5ebv.onrender.com/api/tailscale/status`
> **Automated Validation Suite**: `tests/adapters/test_cac_pull_collector.py` (`13 passed in 0.97s`)

---

## 1. The Core SRE Principle: Decoupling Brain from Muscle

In classical MLOps architectures, if the supervised server (the target cluster or VPS) goes down, the monitoring system crashes with unhandled network stack traces (`ConnectionRefusedError`, `ReadTimeout`).

In **`Agentic-Ops`**, the Control Plane is designed as an **autonomous, decoupled governance brain**:
- **Target Platform (The Muscle)**: The Scaleway VPS (`scw-jovial-dubinsky`, `100.117.99.62`) hosting `Loki`, `Prometheus`, `MLflow`, `Prefect`, and `FastAPI`.
- **Control Plane (The Brain)**: The Render cloud container (`agentic-ops-5ebv.onrender.com`, `100.85.198.81`) hosting the FSM orchestrator, policy engine, WORM trust ledger, LLM agents, and interactive Web Console.

```ansi
[1;34m+--------------------------------------------------------------------------------------------------+[0m
[1;34m|[0m SCENARIO: COLLEAGUE CRASHES SCALEWAY VPS OR CUTS TAILSCALE MESH                                  [1;34m|[0m
[1;34m+--------------------------------------------------------------------------------------------------+[0m
[1;34m|[0m[1;34m|[0m
                                (WireGuard Mesh Down or Scaleway 0 Vitals)
                                                 v
[1;34m+--------------------------------------------------------------------------------------------------+[0m
[1;34m|[0m AGENTIC-OPS CONTROL PLANE (STAYS 100% ONLINE & RESILIENT)                                         [1;34m|[0m
[1;34m|[0m                                                                                                  [1;34m|[0m
[1;34m|[0m 1. CacPullCollector intercepts error [1;36m->[0m Clean Pydantic status: REMOTE_TARGET_OFFLINE             [1;34m|[0m
[1;34m|[0m 2. ZERO Uncaught Exceptions [1;36m->[0m 0 crash, no 500 error on /api/cac/snapshot                         [1;34m|[0m
[1;34m|[0m 3. [1;32mPolicyEngine[0m switches to Fail-Closed [1;36m->[0m Prohibits destructive mutations on unreachable host   [1;34m|[0m
[1;34m|[0m 4. All 62 Tests & 36 War-Room Scenarios run locally inside container via synthetic blueprints   [1;34m|[0m
[1;34m|[0m 5. Interactive SRE Console (/console) and Web Chat (/chat) remain 100% available at [1;32m0 EUR[0m       [1;34m|[0m
[1;34m+--------------------------------------------------------------------------------------------------+[0m
```

---

## 2. Technical Anatomy of Network Failure Absorption (`CacPullCollector`)

The adapter [`agentic_ops/adapters/cac_pull_collector.py`](../agentic_ops/adapters/cac_pull_collector.py) queries 5 remote observability sources over the userspace SOCKS5 proxy (`127.0.0.1:1055`):
1. `loki_alerts`: LogQL query against Loki (`:3100`).
2. `prometheus`: Metric query for `cac_mlops_drift_share` (`:9090`).
3. `mlflow_model`: Active model metadata in MLflow Registry (`:5001`).
4. `prefect_flow_runs`: Recent pipeline executions in Prefect (`:4200`).
5. `drift_report`: Public HTTPS Evidently drift report.

### Exact Exception Interception Mechanics:
```python
# From agentic_ops/adapters/cac_pull_collector.py
except httpx.ConnectError as exc:
    logger.warning("CacPullCollector | %s | ConnectError : %s", key, exc)
    errors[key] = f"ConnectError: {exc}"
except httpx.TimeoutException as exc:
    logger.warning("CacPullCollector | %s | Timeout après %.0fs", key, self._timeout)
    errors[key] = f"Timeout: {exc}"
except Exception as exc:
    logger.error("CacPullCollector | %s | Erreur inattendue : %s", key, exc)
    errors[key] = f"Error: {exc}"
```

### Discrete Categorization of Target Health:
- **`RemoteServiceStatus.ONLINE`**: All 5 remote endpoints responded successfully (`200 OK`).
- **`RemoteServiceStatus.PARTIAL`**: At least one endpoint failed (e.g., Prefect is down, but Prometheus still responds).
- **`RemoteServiceStatus.REMOTE_TARGET_OFFLINE`**: 100% of remote endpoints failed (Scaleway VPS stopped, kernel crash, or Tailscale down).

Even in total outage, `CacPullCollector.collect_all()` returns a valid HTTP `200` JSON response containing the diagnosis:
```json
{
  "status": "REMOTE_TARGET_OFFLINE",
  "collected_at": "2026-10-14T19:05:00Z",
  "errors": {
    "loki_alerts": "ConnectError: [Errno 111] Connection refused",
    "prometheus": "ConnectError: [Errno 111] Connection refused",
    "mlflow_model": "ConnectError: [Errno 111] Connection refused",
    "prefect_flow_runs": "ConnectError: [Errno 111] Connection refused"
  },
  "loki_alerts": null,
  "prometheus": null,
  "mlflow_model": null,
  "prefect_flow_runs": null,
  "drift_report": null
}
```

---

## 3. Why the Entire Test Suite & Web Console Pass Without Scaleway

An essential engineering requirement of `Agentic-Ops` is that academic juries, SRE auditors, and developers must be able to run and verify the entire system without depending on external infrastructure availability.

### Self-Contained Incident Blueprints:
The **36 War-Room Scenarios Registry** (`docs/mlops_simulation_scenarios_registry.md` and `tests/scenarios/data/`) and the unit tests are completely self-contained:
- Telemetry facts (`drift_share`, `accuracy_drop`, `oom_kills`) are injected into the orchestrator via immutable test fixtures.
- The `Orchestrator FSM`, `PolicyEngine` rules (`R-001`, `R-002`), cryptographic `WORM Trust Ledger`, Slack HITL HMAC verification, and LLM reasoning do not make physical outbound network calls to Scaleway during tests.

### Proof via Automated Test Execution:
Running the connector test suite:
```bash
.venv/bin/pytest tests/adapters/test_cac_pull_collector.py -v
```
Output:
```text
tests/adapters/test_cac_pull_collector.py::TestCollectAll::test_status_offline_si_vps_eteint PASSED [ 69%]
tests/adapters/test_cac_pull_collector.py::TestCollectAll::test_status_partial_si_une_source_echoue PASSED [ 76%]
======================== 13 passed, 1 warning in 0.97s =========================
```
And clicking **`Grand Slam: All 62 Tests`** on `/console` executes all 62 sandbox, adversarial, and scenario tests (`62 passed, 2 skipped`) in under 15 seconds, totally oblivious to whether Scaleway is online or powered off.

---

## 4. SRE Governance Defense: The Fail-Closed State

If the monitored platform drops offline:
1. **Zero Hallucinated Mutation**: LLM agents are physically blocked from triggering a mutation (`restart_pod`, `rollback`, `propose_retrain`) against an unreachable target.
2. **Policy Engine Veto**: The `PolicyEngine` rejects any destructive proposal when the underlying target health is non-operational.
3. **WORM Forensic Record**: The outage event is logged and cryptographically signed in `ledger.jsonl`.

---

## 5. Tailscale Mesh Self-Healing & 1-Minute Recovery Protocol

If Tailscale connectivity between Render and Scaleway is interrupted (e.g. session revocation or ephemeral key expiry):

### Option A: 1-Click Interactive Web Recovery
1. Open the live Tailscale status endpoint:
   `https://agentic-ops-5ebv.onrender.com/api/tailscale/status`
2. If the field `"backend_state"` displays `"NeedsLogin"`, the endpoint automatically generates an active authentication URL:
   ```json
   {
     "backend_state": "NeedsLogin",
     "auth_url": "https://login.tailscale.com/a/0123456789abcdef"
   }
   ```
3. Open `auth_url` in any browser and click **Connect**. The Render node immediately rejoins the Tailnet without redeploying.

### Option B: Persistent Auth Key Injection
If the peer was completely deleted from the Tailnet:
1. Generate an ephemeral auth key on **`https://login.tailscale.com/admin/settings/keys`**.
2. Update the environment variable `TAILSCALE_AUTH_KEY` in the Render Dashboard (**`https://dashboard.render.com`**).
3. The container's `scripts/entrypoint.sh` executes `tailscale up --authkey=$TAILSCALE_AUTH_KEY` upon automatic restart.
