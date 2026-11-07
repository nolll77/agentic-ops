# Agentic-Ops — Model Context Protocol (`MCP`) Engineering Roadmap

> **Document Status**: Active Strategic Roadmap & Architectural Specification  
> **Target Release Window**: Versions `v0.2.0` through `v0.4.0`  
> **Canonical Registry Entry**: [`io.github.nolll77/agentic-ops`](https://registry.modelcontextprotocol.io/v0.1/servers/io.github.nolll77%2Fagentic-ops/versions)  
> **Underlying RFC Standards**: Anthropic Model Context Protocol (`2024-11-05`), RFC 6962 (`Certificate Transparency / Merkle Tree`), RFC 8888, EU AI Act (`Regulation (EU) 2024/1689`, Articles 12 & 14)

---

## Executive Summary & Design Invariant

The **`Agentic-Ops` Model Context Protocol Gateway** (`agentic_ops/entrypoints/mcp_server.py`) operates as a governed control plane connecting external cognitive agents (`Claude Desktop`, `Cursor`, `Windsurf`, `Google Antigravity`, `OpenRouter`) to production infrastructure.

Unlike conventional CRUD or unstructured tool gateways, `Agentic-Ops` adheres to the **Deterministic Firewall Invariant**:
> *Cognitive models propose hypotheses; deterministic, zero-token Python kernels enforce policy boundaries, compute blast radiuses, and seal immutable cryptographic evidence.*

This roadmap formalizes the three upcoming engineering phases designed to evolve the gateway from a synchronous execution endpoint into an autonomous, distributed, and cryptographically provable MLOps nervous system.

```text
+-------------------------------------------------------------------------------------------------+
|                                 MCP EVOLUTION ROADMAP TIMELINE                                  |
+-------------------------------------------------------------------------------------------------+
|                                                                                                 |
|   PHASE 1: Real-Time Sensory Probes & Streaming                                                 |
|   ------------------------------------------------------------                                  |
|   * Server-Sent Events (`SSE`) transport stream alongside HTTP JSON-RPC 2.0.                     |
|   * Chunked telemetry & Evidently AI data drift metric streaming over MCP resources.            |
|   * Dynamic prompt sampling (`sampling/createMessage`) for interactive operator confirmation.   |
|                                                                                                 |
|   PHASE 2: Cryptographic Auditability & EU AI Act Compliance                                    |
|   ------------------------------------------------------------                                  |
|   * Native `verify_ledger_inclusion` tool exposing RFC 6962 binary Merkle proofs in O(log N).   |
|   * WORM linear hash chain (`SHA-256` + `HMAC-SHA512`) live audit via MCP JSON-RPC.             |
|   * Direct compliance attestation for EU AI Act High-Risk systems (Articles 12 & 14).          |
|                                                                                                 |
|   PHASE 3: Judicial Multi-Agent Quorum & Sovereign Mesh                                         |
|   ------------------------------------------------------------                                  |
|   * Separation of Powers: Proposer Agent vs Inspector / Auditor Quorum before execution.        |
|   * Sovereign off-cloud fallback: routing tool execution over encrypted Tailscale mesh.         |
|   * Multi-cluster blast-radius isolation & air-gapped zero-trust execution.                     |
|                                                                                                 |
+-------------------------------------------------------------------------------------------------+
```

---

## Phase 1: Real-Time Sensory Probes & Streaming Telemetry (`Delivered in v0.2.0`)

### 1.1 Objective & Context
`Agentic-Ops` now exposes **11 governed MCP tools** and **8 resources** via synchronous HTTP `POST /mcp` (Streamable JSON-RPC 2.0), `GET /mcp/events` (`Server-Sent Events`), and local `stdio`. High-throughput MLOps incident response is supported via continuous non-blocking sensory observation without client-side polling loops.

### 1.2 Architectural Deliverables

1. **Dual Transport Support (`SSE` + `Streamable HTTP`)**:
   - Introduce native Server-Sent Events (`SSE`) endpoint at `GET /mcp/events` alongside the existing `POST /mcp` (`agentic_ops/entrypoints/mcp_sse.py`).
   - Maintain full backwards compatibility with Anthropic MCP protocol version `2024-11-05`.
   - Implement client session heartbeat (`: ping`), `Mcp-Session-Id` binding, and `Last-Event-ID` reconnection replay over retained in-memory history.

2. **Streaming Telemetry over Dynamic MCP Resources**:
   - Expose dynamic URI schemes (`agentic_ops/core/telemetry_stream.py`):
     - `mlops://telemetry/live/drift`: Relays `drift_share` and `n_drifted_columns` from the remote `Evidently AI` report via `CacPullCollector` when `MCP_TELEMETRY_SOURCE=cac_pull`, or emits an explicitly labelled `source="simulated"` baseline by default (never fabricates live drift).
     - `mlops://telemetry/live/latency`: Quantiles (`p50`/`p95`/`p99`) interpolated from the local `agentic_ops_llm_latency_seconds` Prometheus histogram (measuring Agentic-Ops' own LLM calls, explicitly labelled `source="agentic_ops_local"`).
   - External LLMs can subscribe to resource notifications (`resources/subscribe` $\rightarrow$ `notifications/resources/updated`) over active `SSE` sessions rather than polling `poll_target_mlops_snapshot`.

3. **Dynamic Prompt Sampling (`sampling/createMessage`)**:
   - Implement MCP server-initiated prompt sampling (`request_client_sampling` in `agentic_ops/entrypoints/mcp_transport.py`) allowing the control plane to delegate localized heuristic evaluation back to a connected `STDIO` or `HTTP+SSE` client declaring `capabilities.sampling`.
   - Wraps untrusted client model completions inside `prompt_guard.wrap_untrusted(..., source="client_sampling")` and enforces `includeContext="none"`.

### 1.3 Technical Verification Criteria
- [x] SSE connection benchmark: sustain 50 concurrent SSE streaming connections with $< 15\,\text{ms}$ event dispatch latency *(verified in `tests/entrypoints/test_mcp_sse.py`: in-process fan-out $p_{50} = 2.40\,\text{ms}$, $p_{95} = 4.78\,\text{ms}$, $\max = 5.34\,\text{ms}$ across 50 concurrent streams)*.
- [x] Non-blocking event loop: ensure streaming sensory telemetry does not block synchronous tool calls in `mcp_server.py` *(verified via `asyncio.to_thread` collectors, bounded drop-oldest queues, and `run_in_threadpool` JSON-RPC dispatch in `tests/entrypoints/test_mcp_sse.py` & `test_mcp_sampling.py`)*.
- [x] Zero-drift schema validation: ensure all streamed event payloads adhere to strict Pydantic v2 schemas (`TelemetrySnapshot` with `ConfigDict(extra="forbid")`).

---

## Phase 2: Cryptographic Auditability & EU AI Act Compliance (`Delivered in v0.2.0`)

### 2.1 Objective & Context
Regulatory frameworks for autonomous systems—most notably the **European Union Artificial Intelligence Act (`Regulation (EU) 2024/1689`)**—mandate strict record-keeping (Article 12: *Record-keeping*) and human oversight (Article 14: *Human oversight*) for high-risk autonomous AI systems operating in critical workflows.

Phase 2 embeds mathematical proof generation and read-only technical evidence bundles directly into the MCP protocol interface *(technical evidence aid only; not a legal conformity assessment)*.

### 2.2 Architectural Deliverables

1. **Native `verify_ledger_inclusion` Governed MCP Tool**:
   - Expose a new governed tool:
     ```python
     def verify_ledger_inclusion(
         episode_id: str,
         leaf_index: int,
         expected_merkle_root: str
     ) -> Dict[str, Any]:
         """Verifies an RFC 6962 audit path proof in O(log N) time."""
     ```
   - Connects directly to `agentic_ops/core/merkle.py` (`MerkleTree`).
   - Returns a structured proof audit certificate:
     - Sibling audit path hashes: `[{"position": "left"|"right", "hash": "..."}]`.
     - Calculated root vs expected root equality verdict (`VALID_AUTHENTICATED_INCLUSION_PROOF` / `ROOT_MISMATCH` / `TAMPERING_OR_INVALID_PROOF`).
     - Computational verification complexity: $\mathcal{O}(\log_2 N)$ hashing operations.

2. **Automated EU AI Act Article 12 Compliance Bundle**:
   - Expose an MCP resource `mlops://compliance/eu-ai-act/article-12/audit-pack` (`agentic_ops/core/compliance_pack.py`) providing a consolidated, `HMAC-SHA512`-sealed read-only export containing:
     - WORM ledger integrity status, `Merkle` root, episode/decision/FSM state counters (`ledger.jsonl`).
     - SHA-256 linear hash chain continuity and `HMAC-SHA512` signature verification status.
     - Active deterministic `PolicyBundle` rules, version hash, and catalog summary.
     - Read-only operator approval aggregates (`ApprovalRepo.stats()`) plus explicit `signing_key_provenance` (`CONFIGURED` vs `INSECURE_DEFAULT_DUMMY_KEY`) and `third_party_verifiable: false`.

3. **Tamper Rejection Proof in CI/CD**:
   - Automated adversarial test cases validating that any single-bit flip in historical episode logs or audit packs causes immediate verification failure (`tests/adversarial/test_merkle_tree.py`, `tests/core/test_compliance_pack.py`).

### 2.3 Technical Verification Criteria
- [x] $\mathcal{O}(\log N)$ proof generation executes in $< 2\,\text{ms}$ for ledgers exceeding $10^5$ episodes *(verified in `tests/adversarial/test_merkle_tree.py`: `0.040 ms` proof generation and `0.047 ms` verification on a pre-indexed `MerkleTree` of $100,005$ leaves; cold `EvidenceStore.get_merkle_proof` still performs an initial $\mathcal{O}(N)$ `ledger.jsonl` read)*.
- [x] Cryptographic tool suite fully audited by automated pytest cases in `tests/entrypoints/test_mcp_server.py` and `tests/core/test_compliance_pack.py`.
- [x] 100% compliance with RFC 6962 specification for leaf hashing prefix (`0x00`) and interior node hashing prefix (`0x01`).

---

## Phase 3: Judicial Multi-Agent Quorum & Sovereign Mesh (`3.1 Delivered in v0.2.0` · `3.2–3.3 Planned for v0.3.0+`)

### 3.1 Objective & Context
Allowing a single AI agent or single LLM provider to both formulate remediation plans and validate their safety creates an unacceptable single point of failure and systemic cognitive bias. Phase 3 introduces **Judicial Quorum Governance** (`Delivered in v0.2.0`) and **Sovereign Mesh Fallbacks** (`Planned`).

### 3.2 Architectural Deliverables

```text
                               +----------------------------------+
                               |     INCIDENT DETECTED VIA        |
                               |    STREAMING TELEMETRY (P1)      |
                               +-----------------+----------------+
                                                 |
                                                 v
                               +----------------------------------+
                               |   PROPOSER AGENT (e.g. Claude)   |
                               | Formulates ActionProposal:       |
                               | "Scale replicas + flush buffer"  |
                               +-----------------+----------------+
                                                 |
                                                 v
           +-------------------------------------+-------------------------------------+
           |                                                                           |
           v                                                                           v
+-----------------------+                                                   +-----------------------+
|  DETERMINISTIC KERNEL |                                                   |    INSPECTOR AGENT    |
| (agentic-ops Policy)  |                                                   |   (Judicial Quorum)   |
| Pure Python 0-Token   |                                                   | Independent Model     |
| * Blast radius < 0.2  |                                                   | (e.g. Gemma 4 vs      |
| * Rate limit check    |                                                   |  NVIDIA Nemotron)     |
| * Upstream masking    |                                                   | * Evaluates rationale |
+-----------+-----------+                                                   +-----------+-----------+
            |                                                                           |
            +-------------------------------------+-------------------------------------+
                                                  |
                                                  v
                               +----------------------------------+
                               |    CONSENSUS & EXECUTION GATE    |
                               | BOTH Verdicts Must Be "PASS"     |
                               | If approved -> Execute & WORM    |
                               | If vetoed    -> Abort & Log      |
                               +----------------------------------+
```

1. **Judicial Separation of Powers (Proposer vs Inspector)** *(Delivered in `v0.2.0` — `agentic_ops/core/inspector_agent.py`, opt-in via `AGENTIC_OPS_INSPECTOR_ENABLED=true`)*:
   - Split cognitive roles during incident remediation:
     - **Proposer Agent (`RemediationAgent`)**: Drafts `ActionIntent` / `ActionProposal` (`nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free` by default).
     - **Inspector Agent (`InspectorAgent`, role `"inspector"`)**: Operates under a distinct model family (`google/gemma-4-31b-it:free` by default) with `prompt_guard.wrap_untrusted` isolation.
   - **Monotonic Tightening & Fail-Closed**: `apply_inspector_verdict` can ONLY tighten `PolicyEngine` `ALLOW` into `DENY` (on `VETO`) or `REQUIRE_APPROVAL` (fail-closed on LLM timeout/error); it can never loosen `DENY` or `REQUIRE_APPROVAL`.

2. **Sovereign Encrypted Mesh Routing (`Tailscale` + `Ollama`)** *(Planned — `v0.3.0+`)*:
   - Deepen integration with `agentic_ops/adapters/cac_pull_collector.py` and private mesh networks.
   - In the event of cloud provider partition, rate-limiting (`HTTP 429`), or network cutoff:
     - MCP server automatically routes tool calls and prompt evaluations over encrypted WireGuard tunnels (`Tailscale`) to on-premises sovereign inference nodes (`Ollama` running `qwen2.5-coder` or `deepseek-r1`).
     - Guarantees $100\%$ air-gapped emergency remediation capability with zero external cloud dependencies.

3. **Multi-Cluster Federation** *(Planned — `v0.4.0`)*:
   - Allow a master `Agentic-Ops` MCP gateway to orchestrate worker nodes across heterogeneous Kubernetes clusters and bare-metal environments via authenticated mutual TLS (`mTLS`) or WireGuard overlays.

### 3.3 Technical Verification Criteria
- [x] Judicial quorum consensus verified under simulated adversarial prompt injections (`SC-101`, `SC-102`) *(verified in `tests/core/test_inspector_agent.py::test_judicial_quorum_under_sc101_and_sc102_adversarial_injections`, `forbidden_executed=0`)*.
- [ ] Automatic failover to local sovereign node executes in $< 500\,\text{ms}$ upon external API failure *(planned for `v0.3.0+`)*.
- [x] Zero regression across the existing unit and integration test suite *(`288 passed, 3 skipped, 0 failed` in `v0.2.0`)*.

---

## Technical Invariant Matrix Across All Phases

| Engineering Milestone | Transport Protocol | Security Guarantee | Cryptographic Standard | Human Oversight Mode |
| :--- | :--- | :--- | :--- | :--- |
| **Baseline (`v0.1.14`)** | Streamable HTTP / Stdio | Deterministic PolicyEngine (0 tokens) | SHA-256 chain + HMAC-SHA512 + RFC 6962 Merkle | Slack HITL (L2/L3) |
| **Current (`v0.2.0` — P1 + P2 + P3.1)** | SSE (`GET /mcp/events`) + Streamable HTTP + Stdio | Non-blocking telemetry + $\mathcal{O}(\log N)$ Merkle + Monotonic `InspectorAgent` Quorum | RFC 6962 Merkle Proofs + Signed EU AI Act Art. 12 Pack | Slack HITL + `sampling/createMessage` + Fail-Closed Quorum |
| **Planned (`v0.3.0+` — P3.2 & P3.3)** | Dual Mesh (HTTP + WireGuard + `mTLS`) | Sovereign `< 500 ms` `Tailscale`/`Ollama` failover + Multi-Cluster isolation | Multi-party consensus + External WORM anchoring | Air-gapped Sovereign Quorum + Operator |

---

## Community Contribution & Issue Mapping

Engineers and researchers wishing to participate in the implementation of these milestones are invited to consult:
- **Contributing Guide**: [`CONTRIBUTING.md`](../CONTRIBUTING.md) (French: [`docs/CONTRIBUTING_FR.md`](CONTRIBUTING_FR.md))
- **Related GitHub Issues**:
  - **[Issue #1](https://github.com/nolll77/agentic-ops/issues/1)**: Formal linking of human operator rejection to origin episode in WORM ledger.
  - **[Issue #2](https://github.com/nolll77/agentic-ops/issues/2)**: At-least-once delivery, isolated crash injection, and worker failure recovery.
  - **[Issue #6](https://github.com/nolll77/agentic-ops/issues/6)**: Empirical evaluation of free OpenRouter LLMs for the Inspector Quorum role.
