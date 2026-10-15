# Agentic-Ops — Model Context Protocol (`MCP`) Governance Gateway Guide

> **Module Entrypoint**: `agentic_ops/entrypoints/mcp_server.py` (`agentic-mcp`)
> **Protocol Specification**: Anthropic `Model Context Protocol` (`JSON-RPC 2.0`, `protocolVersion: "2024-11-05"`)
> **Live Cloud Endpoint**: `https://agentic-ops-5ebv.onrender.com/mcp` | **Manifest Discovery**: `https://agentic-ops-5ebv.onrender.com/mcp/manifest`
> **Automated Validation Suite**: `tests/entrypoints/test_mcp_server.py` (`12 passed`)

---

## 1. Architectural Vision: The Deterministic `MCP` Firewall

In standard enterprise deployments, connecting autonomous AI clients (`Claude Desktop`, `Cursor`, `Windsurf`, `Google Antigravity`, or custom `LangGraph` agents) directly to infrastructure `MCP` servers (`Kubernetes MCP`, `PostgreSQL MCP`, `GitHub MCP`) introduces an unmitigated operational hazard: **the LLM can directly invoke destructive mutations on production without deterministic pre-flight validation**.

`Agentic-Ops` solves this by exposing the Control Plane itself as a **Governed `MCP` Server**:

```ansi
[1;34m+-----------------------------------------------------------------------------------+[0m
[1;34m|[0m EXTERNAL AI CLIENTS (Claude Desktop / Cursor / Windsurf / Google Antigravity)     [1;34m|[0m
[1;34m+-----------------------------------------+-----------------------------------------+[0m
[1;34m|[0m[1;34m|[0m
                     1. STDIO (Local CLI) | or 2. HTTP JSON-RPC 2.0 (POST /mcp)
                                          v
[1;34m+-----------------------------------------------------------------------------------+[0m
[1;34m|[0m AGENTIC-OPS MCP GOVERNANCE GATEWAY (agentic_ops/entrypoints/mcp_server.py)        [1;34m|[0m
[1;34m|[0m                                                                                   [1;34m|[0m
[1;34m|[0m  +---------------------------+  +-----------------------+  +-------------------+  [1;34m|[0m
[1;34m|[0m  | 8 Governed MCP Tools      |  | 5 Knowledge Resources |  | 20 Starter Prompts|  [1;34m|[0m
[1;34m|[0m  | - read_console_diagnostic |  | - 435 Failure Modes   |  | - Console Audits  |  [1;34m|[0m
[1;34m|[0m  | - evaluate_governance_pol.|  | - 20 Scenarios Reg.   |  | - Policy Vetoes   |  [1;34m|[0m
[1;34m|[0m  | - run_governed_incident   |  | - Autonomy Policy     |  | - WORM Forensics  |  [1;34m|[0m
[1;34m|[0m  | - inspect_worm_ledger     |  | - Known Gaps Matrix   |  | - Taxonomy Search |  [1;34m|[0m
[1;34m|[0m  | - search_failure_taxonomy |  | - Live Console Vitals |  | - SecOps & Jury   |  [1;34m|[0m
[1;34m|[0m  | - get_scenario_blueprint  |  +-----------------------+  +-------------------+  [1;34m|[0m
[1;34m|[0m  | - poll_target_mlops_snap. |                                                    [1;34m|[0m
[1;34m|[0m  | - inspect_control_vitals  |                                                    [1;34m|[0m
[1;34m|[0m[1;34m  +-------------+-------------+                                                    [0m[1;34m|[0m
[1;34m|[0m                |                                                                  [1;34m|[0m
[1;34m|[0m                v                                                                  [1;34m|[0m
[1;34m|[0m[1;34m  +-----------------------------------------------------------------------------+  [0m[1;34m|[0m
[1;34m|[0m  | DETERMINISTIC CORE ([1;32mPolicyEngine[0m + FSM + WORM EvidenceStore + Tailscale)    |  [1;34m|[0m
[1;34m|[0m  | -> Verdicts: ALLOW (L1) | REQUIRE_APPROVAL (Slack HITL L2/L3) | DENY (Veto) |  [1;34m|[0m
[1;34m|[0m  | [1;36m->[0m Cryptographic Sealing: Canonical JSON + SHA-256 Chain + HMAC-SHA512      |  [1;34m|[0m
[1;34m|[0m[1;34m  +-----------------------------------------------------------------------------+  [0m[1;34m|[0m
[1;34m+-----------------------------------------------------------------------------------+[0m
```

---

## 2. Can the `MCP` Server Read the `/console` Web Terminal?

**Yes.** Through the tool `read_console_diagnostic`, any connected `MCP` client can execute and read the exact output of any diagnostic phase from the `/console` Web UI in real time:

- **Compact Mode (`include_guides=False`)**: Returns only the raw, compact `pytest -v` `PASSED` lines, hardware telemetry, or `Tailscale` mesh status.
- **Cognitive Pedagogical Mode (`include_guides=True`, default)**: Appends the structured `[GUIDE:ROLE]`, `[GUIDE:AGENT]`, `[GUIDE:SLACK]`, `[GUIDE:PROD]`, and `[GUIDE:HOW_IT_PASSES]` blocks so the connected LLM has full architectural context to explain *why* and *how* each test passed.

---

## 3. Reference of the 8 Governed `MCP Tools`

| Tool Name | Underlying Module | Input Arguments | Deterministic Guarantee & Output |
| :--- | :--- | :--- | :--- |
| `read_console_diagnostic` | `agentic_ops/cli/main.py` (`run_diagnostic_command`) | `command` (`sandbox_phase_a_vitals` .. `pytest_all`), `include_guides` (`bool`) | Executes whitelisted `/console` suites in-container with `_redact_pii()` anonymization. |
| `evaluate_governance_policy` | `agentic_ops/core/policy_engine.py` (`evaluate`) | `risk_id`, `action`, `target`, `upstream_data_severity`, `recent_executions_last_hour`, `target_replicas`, `target_criticality` | Purely functional evaluation against `autonomy_policy.yaml`, `action_catalog.yaml`, and `risk_register.yaml`. Returns `ALLOW`, `REQUIRE_APPROVAL`, or `DENY` + rule IDs (`R-001`, `R-002`). |
| `run_governed_incident_episode` | `agentic_ops/core/evidence.py` (`EvidenceStore.save`) | `risk_id`, `action`, `target`, `finding_summary`, `confidence_score` | Runs policy evaluation, traces FSM transitions (`DETECTED -> ... -> RESOLVED/DENIED/AWAITING_APPROVAL`), and seals the episode in `ledger.jsonl` with `SHA-256` + `HMAC-SHA512`. |
| `inspect_worm_trust_ledger` | `agentic_ops/core/evidence.py` (`verify_chain`) | `episode_id` (optional), `limit` (`int`) | Verifies the entire `SHA-256` Merkle chain (`previous_hash`) and `HMAC-SHA512` signatures across `ledger.jsonl`. |
| `search_failure_taxonomy` | `docs/mlops_failure_modes_taxonomy.md` | `query` (`str`), `max_results` (`int`) | Searches all `435` cataloged MLOps failure modes across the 10 dimensions and returns line-indexed matches. |
| `get_scenario_blueprint` | `docs/mlops_simulation_scenarios_registry.md` & `tests/scenarios/data/` | `scenario_id` (`SC-101`, `SC-001`, `SIM-1`, `all`) | Retrieves both the prose architectural blueprint and the executable YAML test contract. |
| `poll_target_mlops_snapshot` | `agentic_ops/adapters/cac_pull_collector.py` | `use_proxy` (`bool`), `timeout` (`float`) | Performs a `100% Read-Only` (`HTTP GET`) collection across the 5 `jakatt/cac_mlops` endpoints via the `Tailscale SOCKS5` proxy (`127.0.0.1:1055`). |
| `inspect_control_plane_vitals` | `agentic_ops/cli/main.py` | *(none)* | Returns live TCP socket checks (`Redis :6379`, `Tailscale :1055`), active `PolicyBundle` SHA-256 version, and governed action counts. |

---

## 4. Reference of the 5 Foundational `MCP Resources`

| Resource URI | Source File | MIME Type | Purpose in LLM Context |
| :--- | :--- | :--- | :--- |
| `agentic-ops://taxonomy/failure-modes` | `docs/mlops_failure_modes_taxonomy.md` | `text/markdown` | Injects the 10-dimension ontology of `435` MLOps failure modes into the LLM context window. |
| `agentic-ops://registry/scenarios` | `docs/mlops_simulation_scenarios_registry.md` | `text/markdown` | Injects the 20 MLOps crisis blueprints (`SIM-1` to `SIM-20`) and target metric invariants. |
| `agentic-ops://governance/autonomy-policy` | `agentic_ops/governance/*.yaml` | `application/json` | Exposes the compiled `PolicyBundle` (`autonomy_policy.yaml`, `action_catalog.yaml`, `risk_register.yaml`). |
| `agentic-ops://governance/known-gaps` | `tests/known_gaps.yaml` | `text/yaml` | Exposes the adversarial boundary matrix and test coverage mappings. |
| `agentic-ops://console/vitals` | Live Runtime State | `application/json` | Exposes live daemon health and all whitelisted `/console` diagnostic commands. |

---

## 5. How to Connect (`Comment se brancher dessus`)

### Option A — Claude Desktop Local `STDIO` Connection (Mac & Windows)

The Model Context Protocol (`MCP`) is natively supported by Anthropic's **Claude Desktop** application.

1. Open your Claude Desktop configuration file:
   - **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
2. Insert the `agentic-ops-governance` server definition:

```json
{
  "mcpServers": {
    "agentic-ops-governance": {
      "command": "/Users/nolll/Documents/car_acc/agentic-ops-core/.venv/bin/python",
      "args": [
        "-m",
        "agentic_ops.entrypoints.mcp_server",
        "--stdio"
      ],
      "cwd": "/Users/nolll/Documents/car_acc/agentic-ops-core",
      "env": {
        "AGENTIC_OPS_ENV": "production",
        "PYTHONPATH": "/Users/nolll/Documents/car_acc/agentic-ops-core"
      }
    }
  }
}
```

3. Restart Claude Desktop. An icon indicating available tools will appear in the chat prompt area, giving Claude direct local access to all 8 governed tools and 5 knowledge resources.

*(Note: The web version at `claude.ai` does not yet support arbitrary third-party local `MCP` processes; Claude Desktop is the official and supported Anthropic client for `MCP`).*

---

### Option B — Cursor, Windsurf & Google Antigravity Configuration

For agentic IDEs, configure the local `MCP` server in their respective settings:
- **Cursor**: `.cursor/mcp.json`
- **Windsurf / Google Antigravity**: `~/.gemini/antigravity/mcp_config.json`

Both local process execution (`command` / `args` above) and remote HTTP endpoints are supported:

```json
{
  "mcpServers": {
    "agentic-ops-remote": {
      "url": "https://agentic-ops-5ebv.onrender.com/mcp"
    }
  }
}
```

---

### Option C — ChatGPT Web Integration via Custom GPT Action (`OpenAPI / REST`)

While OpenAI's web interface (`chatgpt.com`) does not use the Anthropic `MCP` protocol directly, you can connect ChatGPT to `Agentic-Ops` in 2 minutes using its native **Custom GPT Actions** backed by the live Render OpenAPI specification:

1. Navigate to **`https://chatgpt.com/gpts/editor`** (or click your profile -> **My GPTs** -> **Create a GPT**).
2. Go to the **Configure** tab:
   - **Name**: `Agentic-Ops Control Plane`
   - **Description**: `Autonomous and governed SRE control plane for MLOps platforms.`
3. Scroll down to **Actions** and click **Create new action**.
4. In the **Schema** section, click **Import from URL** and paste:
   ```ansi
   https://agentic-ops-5ebv.onrender.com/openapi.json
   ```
5. Click **Import**. ChatGPT will parse the endpoints:
   - `GET /api/diagnostics/{command}` (execute `/console` test phases: `sandbox_phase_a_vitals` through `pytest_all`).
   - `GET /api/cac/snapshot` (real-time read-only pull from `jakatt/cac_mlops`).
   - `GET /api/tailscale/status` (mesh VPN topology inspection).
   - `GET /mcp/manifest` (complete catalog of tools, prompts, and resources).
6. Under **Privacy Policy**, enter `https://agentic-ops-5ebv.onrender.com/healthz`.
7. In the Instructions box, add:
   ```text
   You are the Agentic-Ops SRE Assistant. When requested, trigger diagnostic suites using GET /api/diagnostics/{command} and explain the governance verdicts, WORM evidence seals, and policy constraints.
   ```
8. Save and publish (private or link-shared). You can now interact with your Render cluster directly from `chatgpt.com`.

---

### Option E — LibreChat Web UI (`OpenRouter Brain` + `Agentic-Ops MCP Gateway`)

[LibreChat](https://www.librechat.ai) is the leading open-source ChatGPT alternative supporting **both OpenRouter AI models and the Model Context Protocol (`MCP`)**. This architecture allows you to select any model on Earth via OpenRouter (e.g. `deepseek/deepseek-r1:free`) while giving it direct tool-access to your Render Control Plane.

1. A production-ready configuration template is provided at [`librechat.yaml`](../librechat.yaml).
2. To run LibreChat with `Agentic-Ops` MCP enabled:
   ```yaml
   # docker-compose.override.yml in your LibreChat directory
   services:
     api:
       volumes:
         - /path/to/agentic-ops-core/librechat.yaml:/app/librechat.yaml
       environment:
         - OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxxxxxxxxxx
   ```
3. In LibreChat, the MCP tools (`read_console_diagnostic`, `evaluate_governance_policy`, `run_governed_incident_episode`) become available as native tool attachments to DeepSeek-R1, Mistral Large, or Llama 3.3 conversations.

---

### Option F — Standalone Zero-Dependency Cloud Web Chat (`GET /chat` on Render)

For users who want zero local setup (no Docker, no MongoDB, no local Mac resource usage), `Agentic-Ops` includes a native web chat interface served directly by `FastAPI` at `https://agentic-ops-5ebv.onrender.com/chat`:

1. Open your browser directly at:
   ```text
   https://agentic-ops-5ebv.onrender.com/chat
   ```
2. The interface automatically connects to `POST /api/chat` and queries the active provider configured in `LLMProviderRegistry` (e.g. `openrouter/deepseek/deepseek-chat:free` or `openrouter/deepseek/deepseek-r1:free`).
3. It features real-time LLM status probing (`GET /api/llm/status`), structured action metadata cards (`Action`, `Confidence`, `Latency`, `Model`), one-click SRE scenario chips, and full dark-mode styling aligned with the `/console`.
4. **Interactive 20 MCP Cognitive Prompts Catalog**: Clicking the `20 Prompts MCP` header button opens a searchable modal catalog grouping all 20 starter prompts across 5 MLOps categories. Operators can search by keyword (e.g. `drift`, `worm`, `veto`, `slack`), insert templates into the input for customization (`Insert in Chat`), or execute them immediately (`Execute Directly`).
5. **Dedicated Prompts API (`GET /api/prompts`)**: Exposes the full JSON list of the 20 cognitive prompts for external automation or third-party web clients.

#### Comparative Architecture Matrix: LibreChat (Local Docker) vs. Native Web Chat (Render Cloud)

[1;34m|[0m Architectural Dimension | Option 1: Local LibreChat (Docker on Mac/PC) | Option 2: Standalone Cloud Web Chat (`/chat` on Render) [1;34m|[0m
[1;34m|[0m :--- | :--- | :--- [1;34m|[0m
[1;34m|[0m **Hosting Location** | Local workstation (`localhost:3080`) | Render [1;32mFree Tier[0m (`https://agentic-ops-5ebv.onrender.com/chat`) [1;34m|[0m
[1;34m|[0m **Prerequisites** | Docker Desktop, `git clone`, `docker compose up` | Web browser only (zero installation) [1;34m|[0m
[1;34m|[0m **RAM Footprint** | ~1.5 GB RAM (Node.js + MongoDB + Meilisearch) | < 2 MiB RAM (native HTML/JS rendered by existing FastAPI) [1;34m|[0m
[1;34m|[0m **Cloud Availability** | Only when local machine is awake | 24/7 Cloud (Render auto-wake on HTTP request) [1;34m|[0m
[1;34m|[0m **LLM Connection** | Direct client-to-OpenRouter or via local proxy | Server-side via `LLMProviderRegistry` + auto-fallback [1;34m|[0m
[1;34m|[0m **Tool Calling Mode** | MCP client tool attachment (`librechat.yaml`) | Server-side governed execution + `ActionProposal` validation [1;34m|[0m
[1;34m|[0m **User Management** | Multi-user accounts, auth tokens, chat export | Single-operator SRE console session [1;34m|[0m
[1;34m|[0m **Cost** | [1;32m0 EUR[0m (local compute) | [1;32m0 EUR[0m (Render [1;32mFree Tier[0m + OpenRouter `:[1;32mfree[0m` tier) [1;34m|[0m

---

### Option D — Zero-Install Remote Cloud Connection (`HTTP JSON-RPC 2.0` on Render)

Because the `MCP` router is mounted directly on the live `FastAPI` container (`https://agentic-ops-5ebv.onrender.com`), you can query the `MCP` server from any terminal, CI runner, or HTTP `MCP` client without installing Python locally:


#### 1. Inspect the Full `MCP` Manifest (`GET /mcp/manifest`)
```bash
curl -s https://agentic-ops-5ebv.onrender.com/mcp/manifest | jq .counts
```

#### 2. List All 8 Governed `MCP Tools` (`POST /mcp`)
```bash
curl -s -X POST https://agentic-ops-5ebv.onrender.com/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "id": 1, "method": "tools/list"}' | jq .
```

#### 3. Read the `/console` Live via `MCP` (`tools/call -> read_console_diagnostic`)
```bash
curl -s -X POST https://agentic-ops-5ebv.onrender.com/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/call",
    "params": {
      "name": "read_console_diagnostic",
      "arguments": {
        "command": "sandbox_phase_d_mlops_scenarios",
        "include_guides": true
      }
    }
  }' | jq -r '.result.content[0].text'
```

#### 4. Evaluate an Action via the `PolicyEngine` (`tools/call -> evaluate_governance_policy`)
```bash
curl -s -X POST https://agentic-ops-5ebv.onrender.com/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 3,
    "method": "tools/call",
    "params": {
      "name": "evaluate_governance_policy",
      "arguments": {
        "risk_id": "DATA-042",
        "action": "propose_retrain",
        "target": "baac_rf",
        "upstream_data_severity": "CRITICAL"
      }
    }
  }' | jq -r '.result.content[0].text'
```

---

## 6. Complete Catalog of the 20 Cognitive Starter Prompts

All 20 prompts below are natively registered inside `agentic_ops/entrypoints/mcp_server.py` (retrievable via `prompts/list`, `prompts/get`, `GET /mcp/manifest`, and `GET /api/prompts`).

They are also **directly executable in 1 click** inside the Standalone Web Chat at [`https://agentic-ops-5ebv.onrender.com/chat`](https://agentic-ops-5ebv.onrender.com/chat) using the built-in `20 Prompts MCP` catalog browser:

### Category I — Live Web Console (`/console`) Reading & Auditing (Prompts `01` to `04`)

| # | Prompt ID (`prompts/get`) | Ready-to-Use Starter Prompt (Copy-Paste) | `MCP` Tools Chained | Expected Deterministic Verification |
| :--- | :--- | :--- | :--- | :--- |
| **`01`** | `01_console_grand_slam_audit` | *"Exécute le Grand Slam complet sur la console Web via `read_console_diagnostic(command='pytest_all')` et dresse un tableau d'audit SRE par Phase en vérifiant que `forbidden_executed=0`."* | `read_console_diagnostic` | `62 passed` (`Phases C + D + E + F + G + H`), `forbidden_executed=0`. |
| **`02`** | `02_console_vitals_and_cgroup_check` | *"Lis la Phase A de la console (`sandbox_phase_a_vitals`) et `inspect_control_plane_vitals` pour auditer l'enveloppe mémoire `cgroup v2`, `Redis :6379`, `Tailscale SOCKS5 :1055` et `SQLite WAL`."* | `read_console_diagnostic`, `inspect_control_plane_vitals` | Confirms `512 MiB` cgroup limit compliance and live TCP sockets. |
| **`03`** | `03_console_redteam_slack_spoof` | *"Déclenche la Phase B de la console (`sandbox_phase_b_slack_spoof`) et explique comment `slack_webhook.py` bloque le payload forgé `fake_tampered_attack` en `HTTP 401`."* | `read_console_diagnostic` | `HTTP/1.1 401 Unauthorized` in `~2ms` via `HMAC-SHA256` check. |
| **`04`** | `04_console_live_pull_cac_mlops` | *"Interroge en direct les 5 endpoints de la plateforme cible `jakatt/cac_mlops` via `poll_target_mlops_snapshot` à travers le tunnel `Tailscale`."* | `poll_target_mlops_snapshot` | `100% Read-Only` snapshot (`OK` or graceful `REMOTE_TARGET_OFFLINE`). |

### Category II — Deterministic `PolicyEngine` & Risk Arbitration (Prompts `05` to `08`)

| # | Prompt ID (`prompts/get`) | Ready-to-Use Starter Prompt (Copy-Paste) | `MCP` Tools Chained | Expected Deterministic Verification |
| :--- | :--- | :--- | :--- | :--- |
| **`05`** | `05_policy_veto_corrupted_sensor` | *"Un agent propose `propose_retrain` sur `baac_rf` lors de l'incident `DATA-042` alors que la couche `DATA` est en sévérité `CRITICAL`. Évalue cette action avec `evaluate_governance_policy` et explique le veto."* | `evaluate_governance_policy` | Verdict `DENY` triggered by rules `R-001` (`upstream_masks_service`) and `R-002` (`risk_register_forbids`). |
| **`06`** | `06_policy_veto_thrashing_cooldown` | *"Compare le verdict de `evaluate_governance_policy` pour `restart_pod` sur `baac-api` (`INFRA-005`) lorsque `recent_executions_last_hour=0` vs `recent_executions_last_hour=5`."* | `evaluate_governance_policy` | Switches from `REQUIRE_APPROVAL` (`L2`) to hard `DENY` (`rate_limit_exceeded: 1/hour`). |
| **`07`** | `07_policy_hitl_slack_escalation` | *"Évalue l'action `scale_up` sur `baac-api` (`INFRA-005`) avec `target_replicas=2` et `target_criticality='low'`, et explique pourquoi la FSM passe en `AWAITING_APPROVAL`."* | `evaluate_governance_policy` | Verdict `REQUIRE_APPROVAL` (`approvals_required=1`, Slack Block Kit HITL). |
| **`08`** | `08_policy_l1_autonomy_fastpath` | *"Prouve avec `evaluate_governance_policy` pourquoi `create_issue` sur `mlops-incidents` (`DATA-042`) est la seule action autorisée en autonomie totale `L1` (`ALLOW`)."* | `evaluate_governance_policy` | Verdict `ALLOW` (`mutating=False`, `computed_blast_radius=0`, `level=L1`). |

### Category III — `WORM Trust Ledger` Forensics & Cryptography (Prompts `09` to `12`)

| # | Prompt ID (`prompts/get`) | Ready-to-Use Starter Prompt (Copy-Paste) | `MCP` Tools Chained | Expected Deterministic Verification |
| :--- | :--- | :--- | :--- | :--- |
| **`09`** | `09_worm_ledger_chain_verification` | *"Inspecte le `Trust Ledger` via `inspect_worm_trust_ledger(limit=20)` et vérifie l'intégrité de la chaîne de hachage `SHA-256` (`previous_hash`) et des signatures `HMAC-SHA512`."* | `inspect_worm_trust_ledger` | `merkle_chain_and_hmac_valid: true` across all stored episodes. |
| **`10`** | `10_worm_simulate_and_seal_episode` | *"Exécute un épisode gouverné complet via `run_governed_incident_episode` (`risk_id='DATA-042'`, `action='create_issue'`, `target='mlops-incidents'`) puis vérifie son scellement WORM."* | `run_governed_incident_episode`, `inspect_worm_trust_ledger` | Returns new `EP-XXXX`, 64-char `sha256_hash`, and 128-char `hmac_sha512_signature`. |
| **`11`** | `11_worm_tamper_detection_audit` | *"Lance la Phase C de la console (`sandbox_phase_c_adversarial_worm`) et explique comment `test_evidence_integrity.py` détecte la falsification d'un seul octet dans `ledger.jsonl`."* | `read_console_diagnostic` | `9 passed` in Phase C; proves cryptographic anti-tampering. |
| **`12`** | `12_worm_eu_ai_act_compliance_report` | *"Lis la ressource `agentic-ops://governance/autonomy-policy` et `inspect_worm_trust_ledger` pour générer un rapport de conformité `EU AI Act (Articles 12 & 14)`."* | `inspect_worm_trust_ledger` + Resource `autonomy-policy` | Maps WORM logging to Art. 12 and `PolicyEngine` + Slack HITL to Art. 14. |

### Category IV — Knowledge Engineering: `435 Taxonomy` & `Scenarios Registry` (Prompts `13` to `16`)

| # | Prompt ID (`prompts/get`) | Ready-to-Use Starter Prompt (Copy-Paste) | `MCP` Tools Chained | Expected Deterministic Verification |
| :--- | :--- | :--- | :--- | :--- |
| **`13`** | `13_taxonomy_deep_search_drift` | *"Utilise `search_failure_taxonomy(query='drift', max_results=15)` pour extraire tous les risques de dérive dans la Taxonomie des 435 pannes et associe-les aux règles du `PolicyEngine`."* | `search_failure_taxonomy` | Line-indexed matches from `docs/mlops_failure_modes_taxonomy.md`. |
| **`14`** | `14_scenario_lineage_sim1_to_sc001` | *"Appelle `get_scenario_blueprint` pour `SC-001` et `SIM-1` afin de démontrer la filiation directe entre `mlops_simulation_scenarios_registry.md` et `sc_001_data_ingestion_drop.yaml`."* | `get_scenario_blueprint` | Side-by-side lineage from prose specification to executable YAML test. |
| **`15`** | `15_scenario_adversarial_triad_analysis` | *"Inspecte les contrats `SC-101`, `SC-102` et `SC-103` via `get_scenario_blueprint`, puis exécute `sandbox_phase_d_mlops_scenarios` pour prouver pourquoi `forbidden_proposed=6` mais `forbidden_executed=0`."* | `get_scenario_blueprint`, `read_console_diagnostic` | Proves deterministic interception of all 6 adversarial LLM proposals. |
| **`16`** | `16_design_new_scenario_sim9_to_sim20` | *"Consulte `get_scenario_blueprint(scenario_id='SIM-9')` et génère le contrat YAML exécutable complet (`sc_009_*.yaml`) prêt à être intégré dans `tests/scenarios/data/`."* | `get_scenario_blueprint`, `search_failure_taxonomy` | Produces a schema-valid YAML scenario contract for `tests/scenarios/`. |

### Category V — SecOps, Red-Teaming & Executive Jury Defense (Prompts `17` to `20`)

| # | Prompt ID (`prompts/get`) | Ready-to-Use Starter Prompt (Copy-Paste) | `MCP` Tools Chained | Expected Deterministic Verification |
| :--- | :--- | :--- | :--- | :--- |
| **`17`** | `17_secops_prompt_injection_audit` | *"Analyse le scénario `SC-101` (`sc_101_log_injection.yaml`) via `get_scenario_blueprint` et montre comment la double barrière (`PromptGuard` + `PolicyEngine`) bloque une injection ordonnant `scale_to_zero`."* | `get_scenario_blueprint`, `evaluate_governance_policy` | `scale_to_zero` is absent from `action_catalog.yaml` -> immediate `DENY` (`unknown_action`). |
| **`18`** | `18_secops_tool_sandboxing_verification` | *"Exécute `sandbox_phase_e_fsm_governance` via `read_console_diagnostic` et explique comment `AgentTool` isole chaque outil dans un `multiprocessing.Process` avec `SIGKILL` à `15s`."* | `read_console_diagnostic` | `10 passed` in Phase E (`test_tools_security.py` + `test_fsm_orchestrator.py`). |
| **`19`** | `19_sre_tailscale_mesh_diagnostics` | *"Exécute `tailscale_status` et `tailscale_netcheck` via `read_console_diagnostic` pour auditer le mesh WireGuard userspace, la latence DERP et l'anonymisation `_redact_pii()`."* | `read_console_diagnostic` | Displays live mesh peers (`[REDACTED_ACCOUNT]`) and UDP/DERP latencies. |
| **`20`** | `20_executive_jury_defense_briefing` | *"Exécute `inspect_control_plane_vitals`, `read_console_diagnostic(command='pytest_all', include_guides=False)` et `inspect_worm_trust_ledger(limit=5)` pour générer une note de synthèse Jury en 5 points."* | `inspect_control_plane_vitals`, `read_console_diagnostic`, `inspect_worm_trust_ledger` | Executive 5-point synthesis backed by live `62 passed` tests and cryptographic hashes. |

---

## 7. Universal LLM Provider Hub Configuration

The Control Plane decouples reasoning from infrastructure via `agentic_ops/adapters/llm_provider_registry.py` and `llm_protocol.py`. The active provider can be selected dynamically via environment variables without code modification:

| Provider (`LLM_PROVIDER`) | Recommended Model (`LLM_MODEL`) | Cost | Deployment Architecture |
| :--- | :--- | :--- | :--- |
| **`openrouter` (Default)** | `openrouter/deepseek/deepseek-r1:free` | **0 EUR** | 24/7 Cloud via OpenRouter free tier (20 req/min). |
| **`openrouter` (Fast JSON)** | `openrouter/deepseek/deepseek-chat:free` | **0 EUR** | Low latency, direct JSON outputs without think blocks. |
| **`openrouter` (Llama 70B)** | `openrouter/meta-llama/llama-3.3-70b-instruct:free` | **0 EUR** | Enterprise-grade 70B parameter open weights. |
| **`gemini`** | `gemini/gemini-1.5-pro-latest` | Free/Paid | Native Google Gemini multimodal reasoning. |
| **`openai`** | `gpt-4o-mini` | Paid | OpenAI ChatCompletion API. |
| **`anthropic`** | `claude-3-5-haiku-20241022` | Paid | Anthropic Claude 3.5 family. |
| **`azure`** | `azure/gpt-4o` | Enterprise | Azure OpenAI with dedicated endpoints. |
| **`mistral`** | `mistral/mistral-large-2411` | Paid (Cheap) | Native European sovereign model provider. |
| **`huggingface`** | `huggingface/mistralai/Mistral-7B-Instruct-v0.2` | **0 EUR** | Serverless free inference (1000 req/month). |
| **`ollama` (Local/Mesh)** | `ollama/llama3.2:3b` | **0 EUR** | Local workstation, reachable by Render via Tailscale private IP (`OLLAMA_BASE_URL=http://100.x.y.z:11434`). |

### Automatic Failover Chain (`FallbackLLMAdapter`)
If the primary model is throttled or raises a rate-limit error (`429 Too Many Requests`), the adapter automatically tries the fallback chain declared in `LLM_FALLBACK_MODELS` (e.g. `openrouter/deepseek/deepseek-chat:free,openrouter/meta-llama/llama-3.3-70b-instruct:free`) sequentially before raising an exception.

