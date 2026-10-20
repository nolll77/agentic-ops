# Agentic-Ops — Model Context Protocol (`MCP`) Governance Gateway Guide

> **Module Entrypoint**: `agentic_ops/entrypoints/mcp_server.py` (`agentic-mcp`)
> **Protocol Specification**: Anthropic `Model Context Protocol` (`JSON-RPC 2.0`, `protocolVersion: "2024-11-05"`)
> **Live Cloud Endpoint**: `https://agentic-ops-5ebv.onrender.com/mcp` | **Manifest Discovery**: `https://agentic-ops-5ebv.onrender.com/mcp/manifest`
> **Automated Validation Suite**: `tests/entrypoints/test_mcp_server.py` (`24 passed` · 100% Tool Coverage) | Full Suite: `69 passed`

---

## 1. Architectural Vision: The Deterministic `MCP` Firewall

In standard enterprise deployments, connecting autonomous AI clients (`Claude Desktop`, `Cursor`, `Windsurf`, `Google Antigravity`, or custom `LangGraph` agents) directly to infrastructure `MCP` servers (`Kubernetes MCP`, `PostgreSQL MCP`, `GitHub MCP`) introduces an unmitigated operational hazard: **the LLM can directly invoke destructive mutations on production without deterministic pre-flight validation**.

`Agentic-Ops` solves this by exposing the Control Plane itself as a **Governed `MCP` Server**:

```text
+-----------------------------------------------------------------------------------+
| EXTERNAL AI CLIENTS (Claude Desktop / Cursor / Windsurf / Google Antigravity)     |
+-----------------------------------------+-----------------------------------------+
                                          |
                     1. STDIO (Local CLI) | or 2. HTTP JSON-RPC 2.0 (POST /mcp)
                                          v
+-----------------------------------------------------------------------------------+
| AGENTIC-OPS MCP GOVERNANCE GATEWAY (agentic_ops/entrypoints/mcp_server.py)        |
|                                                                                   |
|  +---------------------------+  +-----------------------+  +-------------------+  |
|  | 8 Governed MCP Tools      |  | 5 Knowledge Resources |  | 20 Starter Prompts|  |
|  | - read_console_diagnostic |  | - 435 Failure Modes   |  | - Console Audits  |  |
|  | - evaluate_governance_pol.|  | - 20 Scenarios Reg.   |  | - Policy Vetoes   |  |
|  | - run_governed_incident   |  | - Autonomy Policy     |  | - WORM Forensics  |  |
|  | - inspect_worm_ledger     |  | - Known Gaps Matrix   |  | - Taxonomy Search |  |
|  | - search_failure_taxonomy |  | - Live Console Vitals |  | - SecOps & Jury   |  |
|  | - get_scenario_blueprint  |  +-----------------------+  +-------------------+  |
|  | - poll_target_mlops_snap. |                                                    |
|  | - inspect_control_vitals  |                                                    |
|  +-------------+-------------+                                                    |
|                |                                                                  |
|                v                                                                  |
|  +-----------------------------------------------------------------------------+  |
|  | DETERMINISTIC CORE (PolicyEngine + FSM + WORM EvidenceStore + Tailscale)    |  |
|  | -> Verdicts: ALLOW (L1) | REQUIRE_APPROVAL (Slack HITL L2/L3) | DENY (Veto) |  |
|  | -> Cryptographic Sealing: Canonical JSON + SHA-256 Chain + HMAC-SHA512      |  |
|  +-----------------------------------------------------------------------------+  |
+-----------------------------------------------------------------------------------+
```

---

## 2. Can the `MCP` Server Read the `/console` Web Terminal?

**Yes.** Through the tool `read_console_diagnostic`, any connected `MCP` client can execute and read the exact output of any diagnostic phase from the `/console` Web UI in real time:

- **Compact Mode (`include_guides=False`)**: Returns only the raw, compact `pytest -v` `PASSED` lines, hardware telemetry, or `Tailscale` mesh status.
- **Cognitive Pedagogical Mode (`include_guides=True`, default)**: Appends the structured `[GUIDE:ROLE]`, `[GUIDE:AGENT]`, `[GUIDE:SLACK]`, `[GUIDE:PROD]`, and `[GUIDE:HOW_IT_PASSES]` blocks so the connected LLM has full architectural context to explain *why* and *how* each test passed.

---

## 3. Reference of the 10 Governed `MCP Tools`

| Tool Name | Underlying Module | Input Arguments | Deterministic Guarantee & Output |
| :--- | :--- | :--- | :--- |
| `read_console_diagnostic` | `agentic_ops/cli/main.py` (`run_diagnostic_command`) | `command` (`sandbox_phase_a_vitals` .. `pytest_all`), `include_guides` (`bool`) | Executes whitelisted `/console` suites in-container with `_redact_pii()` anonymization. |
| `evaluate_governance_policy` | `agentic_ops/core/policy_engine.py` (`evaluate`) | `risk_id`, `action`, `target`, `upstream_data_severity`, `recent_executions_last_hour`, `target_replicas`, `target_criticality` | Purely functional evaluation against `autonomy_policy.yaml`, `action_catalog.yaml`, and `risk_register.yaml`. Returns `ALLOW`, `REQUIRE_APPROVAL`, or `DENY` + rule IDs (`R-001`, `R-002`). |
| `run_governed_incident_episode` | `agentic_ops/core/evidence.py` (`EvidenceStore.save`) | `risk_id`, `action`, `target`, `finding_summary`, `confidence_score` | Runs policy evaluation, traces FSM transitions (`DETECTED -> ... -> RESOLVED/DENIED/AWAITING_APPROVAL`), and seals the episode in `ledger.jsonl` with `SHA-256` + `HMAC-SHA512`. |
| `inspect_worm_trust_ledger` | `agentic_ops/core/evidence.py` (`verify_chain`) | `episode_id` (optional), `limit` (`int`) | Verifies the entire `SHA-256` linear hash chain (`previous_hash`), `HMAC-SHA512` signatures, and current Merkle Root across `ledger.jsonl`. |
| `get_ledger_status` | `agentic_ops/core/evidence.py` (`get_merkle_root`, `verify_chain`) | *(none)* | Returns complete WORM ledger health: total sealed episodes, linear chain integrity, HMAC-SHA512 signatures, and active RFC 6962 Merkle Root. |
| `verify_ledger_inclusion` | `agentic_ops/core/evidence.py` (`verify_merkle_proof`) & `agentic_ops/core/merkle.py` | `episode_id` (optional), `proof_packet` (optional), `expected_root` (optional) | Verifies an RFC 6962 binary Merkle inclusion proof in $\mathcal{O}(\log N)$ time, binding episode payload to leaf hash and Merkle root (supports local lookup or offline zero-I/O verification). |
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

**Option 1: Native `uvx` Configuration (Recommended — Zero-install, uses PyPI)**
Add to your Claude Desktop configuration file:
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "agentic-ops": {
      "command": "uvx",
      "args": ["--from", "agentic-ops", "agentic-mcp"]
    }
  }
}
```

**Option 2: Containerized via Docker Hub (Zero Python dependencies)**
```json
{
  "mcpServers": {
    "agentic-ops": {
      "command": "docker",
      "args": ["run", "-i", "--rm", "nolll78/agentic-ops:latest", "agentic-mcp"]
    }
  }
}
```

Restart Claude Desktop. An icon indicating available tools will appear in the chat prompt area, giving Claude direct access to all 8 governed tools and 5 knowledge resources.

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
   ```text
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

| Architectural Dimension | Option 1: Local LibreChat (Docker on Mac/PC) | Option 2: Standalone Cloud Web Chat (`/chat` on Render) |
| :--- | :--- | :--- |
| **Hosting Location** | Local workstation (`localhost:3080`) | Render Free Tier (`https://agentic-ops-5ebv.onrender.com/chat`) |
| **Prerequisites** | Docker Desktop, `git clone`, `docker compose up` | Web browser only (zero installation) |
| **RAM Footprint** | ~1.5 GB RAM (Node.js + MongoDB + Meilisearch) | < 2 MiB RAM (native HTML/JS rendered by existing FastAPI) |
| **Cloud Availability** | Only when local machine is awake | 24/7 Cloud (Render auto-wake on HTTP request) |
| **LLM Connection** | Direct client-to-OpenRouter or via local proxy | Server-side via `LLMProviderRegistry` + auto-fallback |
| **Tool Calling Mode** | MCP client tool attachment (`librechat.yaml`) | Server-side governed execution + `ActionProposal` validation |
| **User Management** | Multi-user accounts, auth tokens, chat export | Single-operator SRE console session |
| **Cost** | 0 EUR (local compute) | 0 EUR (Render Free Tier + OpenRouter `:free` tier) |

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

#### 5. Inspect Trust Ledger Cryptographic State (`tools/call -> get_ledger_status`)
```bash
curl -s -X POST https://agentic-ops-5ebv.onrender.com/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 4,
    "method": "tools/call",
    "params": {
      "name": "get_ledger_status",
      "arguments": {}
    }
  }' | jq -r '.result.content[0].text'
```

#### 6. Verify Merkle Proof of Inclusion (`tools/call -> verify_ledger_inclusion`)

##### A. Local Ledger Lookup Mode (`episode_id`)
```bash
curl -s -X POST https://agentic-ops-5ebv.onrender.com/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 5,
    "method": "tools/call",
    "params": {
      "name": "verify_ledger_inclusion",
      "arguments": {
        "episode_id": "EP-20261021-001"
      }
    }
  }' | jq -r '.result.content[0].text'
```

##### B. Offline Zero-I/O Verification Mode (`proof_packet` + optional `expected_root`)
```bash
curl -s -X POST https://agentic-ops-5ebv.onrender.com/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 6,
    "method": "tools/call",
    "params": {
      "name": "verify_ledger_inclusion",
      "arguments": {
        "proof_packet": {
          "episode_id": "EP-20261021-001",
          "leaf_index": 0,
          "total_leaves": 4,
          "leaf_hash": "a1b2c3d4e5f6...64hex",
          "canonical_payload": "{\"episode_id\":\"EP-20261021-001\",...}",
          "merkle_root": "f6e5d4c3b2a1...64hex",
          "audit_path": [{"position": "right", "hash": "..."}]
        },
        "expected_root": "f6e5d4c3b2a1...64hex"
      }
    }
  }' | jq -r '.result.content[0].text'
```

---

### Option G — Glama Web UI (`glama.ai`) & Hosted Cloud MCP Clients

View the verified live listing directly on the [Glama MCP Directory (`glama.ai/mcp/servers/nolll77/agentic-ops`)](https://glama.ai/mcp/servers/nolll77/agentic-ops).

In [Glama](https://glama.ai), LibreChat, or any cloud MCP client, connect using the direct hosted HTTP JSON-RPC 2.0 endpoint:
```json
{
  "mcpServers": {
    "agentic-ops": {
      "url": "https://agentic-ops-5ebv.onrender.com/mcp"
    }
  }
}
```
When submitted under `Runs from source` on Glama (`https://github.com/nolll77/agentic-ops`), Glama executes the server container inside its own isolated cloud sandbox, ensuring zero compute load and zero billing impact on your personal infrastructure.

---

### Option H — Official Anthropic Model Context Protocol Registry (`registry.modelcontextprotocol.io`)

`Agentic-Ops` is officially registered and active on the Anthropic-governed [Official Model Context Protocol Registry](https://registry.modelcontextprotocol.io):
- **Canonical Reverse-DNS Namespace**: `io.github.nolll77/agentic-ops`
- **Live Registry API Endpoint**: [`https://registry.modelcontextprotocol.io/v0.1/servers/io.github.nolll77%2Fagentic-ops/versions`](https://registry.modelcontextprotocol.io/v0.1/servers/io.github.nolll77%2Fagentic-ops/versions)
- **Official Manifest Specification**: [`server.json`](../server.json) conforming to schema `https://static.modelcontextprotocol.io/schemas/2025-12-11/server.schema.json`.
- **Ecosystem Discovery**: Enables instant auto-discovery across all modern MCP clients (Claude Desktop, Cursor, Windsurf, Zed, Glama, PulseMCP).

---

## 6. How to Prompt the MCP Server: The SRE & MLOps Operator Guide

> **Core Architectural Invariant**: The `Agentic-Ops` MCP server is **NOT** a business-domain CRUD API for querying raw target datasets or counting road accidents. It is an **SRE & MLOps Governance Cockpit** designed to empower an operations engineer with AI-assisted incident investigation, policy veto auditing, cryptographic evidence verification, and runtime telemetry inspection.

When querying the MCP server through an AI assistant (Claude Desktop, Cursor, Glama with DeepSeek, or ChatGPT), structure your prompts around the following **5 operational patterns**:

### 1. MLOps Failure Taxonomy Investigation (`search_failure_taxonomy`)
*Use when investigating anomalous telemetry, data drift, or model degradation.*
- **Operator Prompt**: *"We detected significant data drift on input features and elevated latency spikes. Search the 435 MLOps failure taxonomy for matching root causes, propagation cascades, and recommended mitigations."*
- **What the LLM Does**: Calls `search_failure_taxonomy` with keywords like `"drift"`, `"latency"`, or `"poisoning"`, mapping the symptom across the 10 MLOps architectural dimensions.

### 2. Pre-Execution Policy & Veto Verification (`evaluate_governance_policy`)
*Use when verifying whether an autonomous agent's proposed action is safe to execute.*
- **Operator Prompt**: *"An AI remediation agent proposes to restart the prediction pod or trigger an automated retrain under CRITICAL upstream data severity. Check if the deterministic PolicyEngine permits this action or issues a hard veto (DENY)."*
- **What the LLM Does**: Calls `evaluate_governance_policy` with exact target and severity parameters, explaining the fail-closed veto (`R-001 upstream_masks_service` or `1/hour rate_limit_exceeded`).

### 3. WORM Trust Ledger & Merkle Audit (`inspect_worm_trust_ledger`)
*Use for forensic post-mortems, EU AI Act compliance checks, or tamper detection.*
- **Operator Prompt**: *"Verify the cryptographic integrity of the linear SHA-256 hash chain in the WORM Trust Ledger and show the sealed proof for the latest incident episode."*
- **What the LLM Does**: Calls `inspect_worm_trust_ledger` to verify the HMAC-SHA512 signatures and RFC 6962 binary Merkle root, certifying zero tampering.

### 4. War-Room Crisis Blueprints (`get_scenario_blueprint`)
*Use during tabletop exercises, fire drills, or chaos engineering preparations.*
- **Operator Prompt**: *"Retrieve the architectural specification and invariants for scenario SC-101 (adversarial data poisoning) and explain what human-in-the-loop approvals are required."*
- **What the LLM Does**: Calls `get_scenario_blueprint` to extract YAML crisis contracts, blast-radius boundaries, and required quorum levels.

### 5. Live Glass-Box SRE Diagnostics (`read_console_diagnostic`)
*Use to inspect daemon vitals, memory cgroups, or test execution proofs.*
- **Operator Prompt**: *"Execute the sandbox vitals phase A diagnostic to inspect daemon memory, socket connectivity (Redis, Tailscale), and the active policy version."*
- **What the LLM Does**: Calls `read_console_diagnostic(command='sandbox_phase_a_vitals')` and returns verified test results with pedagogical guidance.

### 6. Merkle Inclusion Proof & Independent Root Authentication (`verify_ledger_inclusion` & `get_ledger_status`)
*Use for independent compliance verification (EU AI Act Article 12/17), zero-knowledge inclusion proofs, and cryptographic trust anchoring.*
- **Operator Prompt**: *"Verify whether incident episode EP-20261021-001 is sealed in the WORM Trust Ledger, extract its O(log N) Merkle audit proof path, and authenticate the declared root against our trusted anchor."*
- **What the LLM Does**:
  1. Calls `get_ledger_status` to retrieve the current active RFC 6962 binary Merkle root, linear chain validity, and total sealed episode count.
  2. Calls `verify_ledger_inclusion(episode_id='...')` for local ledger lookup, OR calls `verify_ledger_inclusion(proof_packet={...}, expected_root='...')` for offline zero-I/O verification.
- **Architectural & Security Invariants Enforced**:
  - **Key-Presence Mutual Exclusivity**: Rejects simultaneous presence of `episode_id` and `proof_packet` with `MUTUALLY_EXCLUSIVE_PARAMS` (`isError: True`), even if falsy strings or empty objects are supplied.
  - **Zero-I/O Offline Mode**: Verifies standalone proof packets strictly in memory without opening or instantiating `EvidenceStore`.
  - **Strict Cryptographic Binding**: Binds `episode_id` $\rightarrow$ `canonical_payload` $\rightarrow$ `leaf_hash` via `SHA-256(0x00 || payload)` before traversing the $\mathcal{O}(\log N)$ sibling path. Any payload tampering produces `TAMPERING_OR_INVALID_PROOF`.
  - **Dual Trust Semantics**: Explicitly separates mathematical consistency (`proof_valid_for_declared_root`) from external root certification (`root_authenticated` and `verified_against_trusted_root`). If `expected_root` differs, returns `ROOT_MISMATCH`. If valid and trusted, returns `VALID_AUTHENTICATED_INCLUSION_PROOF`.

---

## 7. Complete Catalog of the 20 Cognitive Starter Prompts

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
| **`09`** | `09_worm_ledger_chain_verification` | *"Inspecte le `Trust Ledger` via `inspect_worm_trust_ledger(limit=20)` et vérifie l'intégrité de la chaîne de hachage `SHA-256` (`previous_hash`) et des signatures `HMAC-SHA512`."* | `inspect_worm_trust_ledger` | `linear_chain_and_hmac_valid: true` (and `merkle_chain_and_hmac_valid: true`) across all stored episodes. |
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

## 8. Universal LLM Provider Hub Configuration

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

---

## 9. M8ven Trust Index & Ecosystem Security Standards (Behavioral Tool Annotations, Licensing, and 100% Test Coverage)

To achieve autonomous production grade on public Model Context Protocol indexes (such as the **M8ven Trust Index**, OpenAI's directory, and Anthropic's catalog), `agentic-ops` satisfies strict determinism and safety requirements, achieving **Grade A (95-100 / 100) Verified Enterprise Control Plane** rating.

### 9.1 Technical Analysis: MLOps Theory vs. Solo Engineering Reality

* **MLOps Theory & Ecosystem Standards**:
  Autonomous agent ecosystems require programmatic guarantees before connecting an LLM to infrastructure. These platforms evaluate four critical security dimensions:
  1. **Declarative Behavioral Contracts (`Tool Annotations`)**: Every tool must explicitly declare four boolean hints (`readOnlyHint`, `destructiveHint`, `idempotentHint`, `openWorldHint`). OpenAI and Anthropic registries reject or flag tools where any of these hints are missing or non-boolean, as clients need to know whether to prompt human users before execution.
  2. **Legal Governance & Open Licensing (`LICENSE`)**: An explicit open-source license (such as `MIT` or `Apache-2.0`) must reside at the repository root to guarantee reuse freedom and patent-free interoperability.
  3. **Traceability & Zero-Regression Testing (`Tool Test Coverage`)**: 100% of declared tools must be tested and referenced by name in automated unit suites (`tests/entrypoints/test_mcp_server.py`).

* **Solo Engineering Reality**:
  Public crawlers such as `M8ven` do not restrict their audit to the primary JSON-RPC list (`MCP_TOOLS` in `agentic_ops/entrypoints/mcp_server.py`, which exposes 8 control plane tools). They execute deep AST (Abstract Syntax Tree) parsing across all Python modules in the repository, detecting operational tools under `agentic_ops/tools/` (9 specialized classes inheriting from `AgentTool`). To guarantee flawless evaluation, all 17 tools have been systematically annotated and verified.

---

### 9.2 Comprehensive Taxonomy of the 19 Annotated Tools

All 19 tools declare explicit boolean hints formatted in both `camelCase` (for official MCP and OpenAI directory compatibility) and `snake_case` (for native Python client compatibility):

| # | Tool Identifier | Source File | `readOnlyHint` | `destructiveHint` | `idempotentHint` | `openWorldHint` | SRE Safety & Blast Radius Rationale |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| **1** | `read_console_diagnostic` | `agentic_ops/entrypoints/mcp_server.py` | `True` | `False` | `True` | `False` | Read-only in-memory execution of diagnostic commands with PII redaction. |
| **2** | `evaluate_governance_policy` | `agentic_ops/entrypoints/mcp_server.py` | `True` | `False` | `True` | `False` | Pure functional arbitration against YAML policy manifests with zero mutation. |
| **3** | `run_governed_incident_episode` | `agentic_ops/entrypoints/mcp_server.py` | `False` | `False` | `False` | `False` | Seals a new cryptographic record into `ledger.jsonl`; state-mutating but non-destructive. |
| **4** | `inspect_worm_trust_ledger` | `agentic_ops/entrypoints/mcp_server.py` | `True` | `False` | `True` | `False` | Audits the SHA-256 linear hash chain and HMAC-SHA512 signatures without modification. |
| **5** | `get_ledger_status` | `agentic_ops/entrypoints/mcp_server.py` | `True` | `False` | `True` | `False` | Reads total episodes, linear chain integrity, and current RFC 6962 binary Merkle root. |
| **6** | `verify_ledger_inclusion` | `agentic_ops/entrypoints/mcp_server.py` | `True` | `False` | `True` | `False` | Verifies RFC 6962 inclusion proofs in $\mathcal{O}(\log N)$ time, binding episode payload to leaf hash and root. |
| **7** | `search_failure_taxonomy` | `agentic_ops/entrypoints/mcp_server.py` | `True` | `False` | `True` | `False` | Performs exact read-only substring matching across `docs/mlops_failure_modes_taxonomy.md`. |
| **8** | `get_scenario_blueprint` | `agentic_ops/entrypoints/mcp_server.py` | `True` | `False` | `True` | `False` | Reads scenario registry Markdown and executable YAML scenario contracts. |
| **9** | `poll_target_mlops_snapshot` | `agentic_ops/entrypoints/mcp_server.py` | `True` | `False` | `True` | `True` | Pulls external telemetry via `CacPullCollector` over Tailscale SOCKS5 (`127.0.0.1:1055`). |
| **10** | `inspect_control_plane_vitals` | `agentic_ops/entrypoints/mcp_server.py` | `True` | `False` | `True` | `False` | Inspects local Unix sockets, cgroup v2 memory telemetry, and active `PolicyBundle` hash. |
| **11** | `get_mlflow_model_info` | `agentic_ops/tools/model.py` | `True` | `False` | `True` | `True` | Queries remote MLflow Model Registry metadata via read-only GET requests. |
| **12** | `get_prometheus_metric` | `agentic_ops/tools/observability.py` | `True` | `False` | `True` | `True` | Queries Prometheus metric endpoints over the observability network. |
| **13** | `get_evidently_report` | `agentic_ops/tools/observability.py` | `True` | `False` | `True` | `True` | Fetches Evidently AI data drift reports from external storage. |
| **14** | `check_database_health` | `agentic_ops/tools/infra.py` | `True` | `False` | `True` | `True` | Performs low-overhead TCP socket ping against the PostgreSQL instance. |
| **15** | `check_docker_container` | `agentic_ops/tools/infra.py` | `True` | `False` | `True` | `False` | Queries local Docker daemon socket for container status. |
| **16** | `check_dvc_status` | `agentic_ops/tools/data.py` | `True` | `False` | `True` | `False` | Reads local `.dvc` lock files to verify dataset cryptographic hash parity. |
| **17** | `validate_pandera_schema` | `agentic_ops/tools/data.py` | `True` | `False` | `True` | `False` | In-memory schema validation against data contract specifications. |
| **18** | `execute_sql` | `agentic_ops/tools/data.py` | `False` | `True` | `False` | `True` | Executes raw SQL (DML/DDL) on target database; strictly guarded by Least Privilege and human approval (`requires_approval=True`). |
| **19** | `create_github_issue` | `agentic_ops/tools/github.py` | `False` | `False` | `False` | `True` | Calls GitHub REST API to post incident tracking issues; guarded by approval. |


---

### 9.3 Automated Verification & Suite Coverage

The verification suite in `tests/entrypoints/test_mcp_server.py` validates this architecture through:
* `test_mcp_tools_declare_all_four_hints`: Programmatically asserts that all 10 tools exposed via JSON-RPC declare `readOnlyHint`, `destructiveHint`, `idempotentHint`, and `openWorldHint` as genuine `bool` instances.
* `test_mcp_tool_poll_target_mlops_snapshot`: Validates full mocked HTTP pull pipeline execution.
* Individual unit tests for each of the 9 operational `AgentTool` implementations (`test_tool_get_mlflow_model_info`, `test_tool_execute_sql`, etc.) ensuring sub-process OS isolation, SIGTERM timeouts, and proper argument schema validation.
* `test_all_19_tools_audit_and_coverage`: Comprehensive parity audit ensuring all 19 tools are unique, declared, and covered without omission.

---

## 10. Architectural Roadmap & Community Contributions

For upcoming R&D phases covering Server-Sent Events (`SSE`), EU AI Act Article 12 cryptographic compliance packs, and Judicial Multi-Agent Quorum architectures, please consult:

- **[Model Context Protocol (`MCP`) Engineering Roadmap (`docs/MCP_ROADMAP.md`)](MCP_ROADMAP.md)** (Version française : [`docs/MCP_ROADMAP_FR.md`](MCP_ROADMAP_FR.md))
- **[Community Collaboration & Contributing Guide (`CONTRIBUTING.md`)](../CONTRIBUTING.md)** (Version française : [`docs/CONTRIBUTING_FR.md`](CONTRIBUTING_FR.md))
- **[Active Community Issues on GitHub](https://github.com/nolll77/agentic-ops/issues)**




