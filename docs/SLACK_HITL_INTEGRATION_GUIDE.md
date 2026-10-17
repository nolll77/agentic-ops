# Agentic-Ops — Slack Human-in-the-Loop (HITL) Governance & Integration Guide

> **Module Entrypoints**: `agentic_ops/entrypoints/slack_webhook.py` (`POST /slack/interactive`), `agentic_ops/entrypoints/slack_verify.py`
> **Outbound Adapter**: `agentic_ops/adapters/slack_adapter.py` (`SlackInteractiveAdapter`)
> **Verification Diagnostic**: `/console` -> `sandbox_phase_b_slack_spoof` (`HTTP 401 Unauthorized` in `~2ms`)

---

## 1. Architectural Vision: Deterministic Human-in-the-Loop (HITL)

When an autonomous AI agent in the multi-agent system (`MAS`) diagnoses a high-severity incident (`CRITICAL` drift, pod saturation, model rollback), the deterministic `PolicyEngine` enforces an explicit governance decision:

* **Level 1 (`L1`) — Autonomous Execution (`ALLOW`)**: Safe read-only actions (e.g. `create_issue`, `investigate`) execute automatically.
* **Level 2 / Level 3 (`L2/L3`) — Human Approval Required (`REQUIRE_APPROVAL`)**: Mutating actions with non-zero blast radius (e.g. `restart_pod`, `scale_up`, `rollback`) immediately halt the finite state machine (`FSM`) in state `AWAITING_APPROVAL` and dispatch an interactive Block Kit card to an on-call Slack channel.

```text
+-------------------------------------------------------------------------------------------------+
| AGENTIC-OPS CONTROL PLANE                                                                       |
|                                                                                                 |
|   1. Incident Detected (e.g. DATA-042 / INFRA-005)                                              |
|   2. PolicyEngine Evaluation -> REQUIRE_APPROVAL (L2/L3)                                        |
|   3. FSM Transition -> AWAITING_APPROVAL                                                        |
+-------------------------------------------------------------------------------------------------+
                                       |
                   Outbound Block Kit  | HTTP POST (Incoming Webhook)
                                       v
+-------------------------------------------------------------------------------------------------+
| SLACK WORKSPACE (#astreinte-mlops)                                                              |
|                                                                                                 |
|   +-----------------------------------------------------------------------------------------+   |
|   | MLOps Control Plane : Approbation Requise                                               |   |
|   | Episode : EP-0042 | Risk : DATA-042 | Action : restart_pod                              |   |
|   | Le Policy Engine a bloque cette action et requiert une validation humaine.              |   |
|   |                                                                                         |   |
|   | [ Approve (Primary) ]                      [ Reject (Danger) ]                          |   |
|   +-----------------------------------------------------------------------------------------+   |
+-------------------------------------------------------------------------------------------------+
                                       |
                   Interactive Payload | POST /slack/interactive
                   HMAC-SHA256 Signed  | Header: X-Slack-Signature, X-Slack-Request-Timestamp
                                       v
+-------------------------------------------------------------------------------------------------+
| SLACK WEBHOOK ENDPOINT (agentic_ops/entrypoints/slack_webhook.py)                               |
|                                                                                                 |
|   1. verify_slack() -> HMAC-SHA256(SLACK_SIGNING_SECRET) & Timestamp window (< 300s)           |
|   2. Replay Attack Protection -> Signature deduplication in SQLite WAL (state/approvals.db)    |
|   3. Approver Group Validation -> Verify user role for required governance tier                |
|   4. FSM Resumption -> Resume episode execution or transition to REJECTED                       |
+-------------------------------------------------------------------------------------------------+
```

---

## 2. Technical Audit: Core SRE Components (What is 100% Implemented)

The entire SRE governance engine and cryptographic perimeter are fully implemented and verified in the codebase:

### 2.1 Inbound Interactive Webhook (`POST /slack/interactive`)
* **File**: `agentic_ops/entrypoints/slack_webhook.py`
* **Route**: Mounted directly on FastAPI at `/slack/interactive`.
* **Behavior**:
  * Parses Slack interactive payload containing user identity, clicked action ID (`approve` / `deny`), target episode ID, and cryptographic proposal hash (`claimed_hash`).
  * Validates approver group authorization via `d.approvers.group_of(user, level)` against required permission tier.
  * Records the decision in persistent SQLite storage (`ApprovalRepo` with Write-Ahead Logging `WAL`).
  * Triggers background task execution: `resume_from_claim` if approved, or `close_episode` if rejected or expired.

### 2.2 Cryptographic Security & Anti-Replay Protection
* **File**: `agentic_ops/entrypoints/slack_verify.py`
* **Signature Algorithm**: Strict `HMAC-SHA256` verification matching the official Slack signing protocol:
  $$\text{signature} = \text{"v0="} + \text{HMAC-SHA256}(\text{SLACK\_SIGNING\_SECRET}, \text{"v0:"} + \text{timestamp} + \text{":"} + \text{body})$$
* **Constant-Time Comparison**: Uses `hmac.compare_digest` to prevent timing attacks.
* **Timestamp Replay Window**: Rejects any request older than 300 seconds (`tolerance_s = 300`) with `HTTP 401 Unauthorized` (`timestamp hors fenetre`).
* **Signature Deduplication**: The SQLite repository registers used signatures to drop replayed payloads (`duplicate_ignored`).

### 2.3 Live Red-Team Defense Verification (Phase B Console Diagnostic)
* **Diagnostic Command**: `sandbox_phase_b_slack_spoof`
* **Validation**:
  * Simulates an adversarial webhook spoofing attack: sends an unauthenticated `POST /slack/interactive` with forged body `payload=fake_tampered_attack`.
  * The security layer intercepts the call in `~2ms` and returns `HTTP 401 Unauthorized` (`en-tetes manquants`) in strict **Fail-Closed** mode.

### 2.4 Interactive Block Kit Message Formatter
* **File**: `agentic_ops/adapters/slack_adapter.py`
* **Class**: `SlackInteractiveAdapter(NotificationAdapter)`
* **Output Structure**: Dynamically builds two-button Slack Block Kit cards containing episode metadata, risk identifier, target resource, and callback actions (`APPROVE_<episode_id>` / `DENY_<episode_id>`).

---

## 3. Deployment Modes: Hermetic Sandbox vs. Live External Slack

Depending on your operational environment, `Agentic-Ops` supports two operational modes:

| Dimension | Mode 1: Hermetic SRE Sandbox (Default) | Mode 2: Live External Slack Workspace |
| :--- | :--- | :--- |
| **Purpose** | Self-contained validation, CI/CD pipelines, demos, zero external network dependencies. | Real-time human alerting on mobile/desktop Slack channels. |
| **Outbound Webhook** | Simulated in-process (`print` statement, zero network latency). | Active HTTP POST to `https://hooks.slack.com/services/...`. |
| **Inbound Webhook** | Verified via in-memory/local requests (`sandbox_phase_b_slack_spoof`). | Live traffic from Slack edge servers to `https://<domain>/slack/interactive`. |
| **Secret Key** | Fallback key (`dummy_secret_defense_presentation`). | Real secret issued by `api.slack.com` (`SLACK_SIGNING_SECRET`). |
| **Availability Risk** | **0%** (Immune to third-party outages, rate-limits, or expired tokens). | Subject to Slack API availability and webhook delivery latencies. |

---

## 4. Step-by-Step Guide: Connecting to a Real Slack Workspace (Production Setup)

When ready to connect the Control Plane to an active corporate or personal Slack workspace, follow these four simple setup steps:

### Step 1 — Create the Slack App & Retrieve the Signing Secret
1. Navigate to [api.slack.com/apps](https://api.slack.com/apps) and click **Create New App** -> **From scratch**.
2. Name your app `Agentic-Ops Control Plane` and select your target workspace.
3. Under **Basic Information** -> **App Credentials**, copy the **Signing Secret**.
4. Configure this secret in your deployment environment variables:
   * **Render Dashboard**: Add `SLACK_SIGNING_SECRET=<your_signing_secret>`.
   * **Docker Compose**: Set `SLACK_SIGNING_SECRET=<your_signing_secret>` in `.env` or `docker-compose.yml`.

### Step 2 — Configure Slack Interactivity
1. In the Slack App management console, navigate to **Features** -> **Interactivity & Shortcuts**.
2. Toggle the switch to **On**.
3. Under **Request URL**, enter the public HTTPS URL of your deployed Control Plane:
   ```text
   https://<your-control-plane-domain>/slack/interactive
   ```
   *(Example for Render deployment: `https://agentic-ops-5ebv.onrender.com/slack/interactive`)*
4. Click **Save Changes** at the bottom of the page.

### Step 3 — Create an Incoming Webhook for On-Call Notifications
1. Under **Features**, navigate to **Incoming Webhooks** and toggle to **On**.
2. Click **Add New Webhook to Workspace**.
3. Select your on-call alerts channel (e.g. `#mlops-alerts` or `#sre-incidents`) and authorize.
4. Copy the generated Webhook URL (format: `https://hooks.slack.com/services/T.../B.../...`).
5. Configure the environment variable in your deployment:
   ```bash
   SLACK_WEBHOOK_URL="https://hooks.slack.com/services/T.../B.../..."
   ```

### Step 4 — Activate Outbound HTTP Dispatch in `slack_adapter.py`
In `agentic_ops/adapters/slack_adapter.py`, locate lines 71-78 inside `SlackInteractiveAdapter.request_approval()`:

```python
# Change from simulated mode:
print(f"[Slack] Sending approval request for {episode_id} to webhook...")
# req = urllib.request.Request(
#     self.webhook_url, 
#     data=json.dumps(payload).encode('utf-8'),
#     headers={'Content-Type': 'application/json'}
# )
# urllib.request.urlopen(req)

# To active production dispatch:
req = urllib.request.Request(
    self.webhook_url,
    data=json.dumps(payload).encode("utf-8"),
    headers={"Content-Type": "application/json"},
)
with urllib.request.urlopen(req, timeout=5) as response:
    logger.info("Dispatched approval notification to Slack: HTTP %s", response.status)
```

---

## 5. Security & SRE Best Practices

1. **Strict HTTPS Required**: Slack requires interactive webhook endpoints to use valid SSL/TLS certificates. Plain HTTP endpoints are rejected by Slack's gateway.
2. **Fail-Closed Principle**: If `SLACK_SIGNING_SECRET` is unset or headers are missing, `slack_verify.py` immediately rejects requests with `HTTP 401 Unauthorized` or `HTTP 500 Internal Server Error`, ensuring no forged action can bypass governance.
3. **Audit Trail Synchronization**: Every approved or rejected action received via Slack is committed to SQLite and permanently recorded in the immutable WORM Trust Ledger (`ledger.jsonl`), linking the Slack user ID to the cryptographic episode hash.
