# Contributing to Agentic-Ops

Welcome to **Agentic-Ops**! We appreciate your interest in contributing to our autonomous SRE and MLOps governance control plane.

This document outlines our engineering standards, architectural invariants, testing methodologies, and Pull Request workflows for all software engineers and researchers.

> **French Version / Version Française** : Consultez le guide en français sur [`docs/CONTRIBUTING_FR.md`](docs/CONTRIBUTING_FR.md).

---

## 1. Architectural Invariants (Non-Negotiable)

Every contribution must strictly adhere to the following **five foundational invariants**:

1. **Hexagonal Architecture (Ports & Adapters)**:
   - Core domain logic (`agentic_ops/core/`) must remain pure, decoupled from external frameworks, network protocols, and persistence mechanisms.
   - External transports (FastAPI, Model Context Protocol JSON-RPC, Slack Webhooks, CLI commands) live strictly in `agentic_ops/entrypoints/` and `agentic_ops/adapters/`.
2. **AI Proposes, Deterministic Code Decides (0-Token Safety Kernel)**:
   - Large Language Models (LLMs) are restricted to semiotic triage, anomaly root-cause investigation, and proposing candidate remediations (`ActionProposal`).
   - Safety arbitration, blast-radius boundaries, target filtering, rate limiting, and vetoes are executed by **100% deterministic Python code with zero tokens and zero hallucinations** (`PolicyEngine`).
3. **Cryptographic WORM Auditability (RFC 6962)**:
   - Every operational decision, policy verdict, and execution trace is immutably appended to a Write-Once, Read-Many (`WORM`) trust ledger (`agentic_ops/core/evidence_store.py`).
   - Entries are chained via SHA-256 linear hashes, HMAC-SHA512 signatures, and provable in $\mathcal{O}(\log N)$ via an RFC 6962 binary Merkle tree (`RFC6962MerkleTree`).
4. **Hard Sub-Process Isolation & Resource Envelopes**:
   - All tool invocations (`AgentTool`) execute inside isolated OS child processes (`multiprocessing.Process`) with strict resource cgroups and a hard OS timeout (`SIGKILL` after 15 seconds) to prevent infinite loops, memory leaks, and runaway processes.
5. **Radical Honesty & Scientific Transparency**:
   - Differentiate what is verified by automated in-memory tests from what requires live multi-node infrastructure or cloud deployments. Never claim production SLOs without reproducible benchmarks.

---

## 2. Local Development Environment

`Agentic-Ops` leverages the ultra-fast Python package manager `uv` under Python 3.11+.

### Prerequisites

- Python `3.11+`
- `uv` package manager (`curl -LsSf https://astral.sh/uv/install.sh | sh`)
- `git`
- *(Optional)* Docker for containerized validation

### Setup

```bash
# Clone the repository
git clone https://github.com/nolll77/agentic-ops.git
cd agentic-ops

# Install dependencies including the development extras
uv sync --all-extras

# Run the complete test suite (231 automated tests)
uv run pytest tests/ -q -p no:randomly
```

### Running the Local Development Servers

```bash
# Start the full Control Plane (Web Console on :8001/console, Chat on :8001/chat, API on :8001/docs)
uv run agentic-start --port 8001

# Or start the Model Context Protocol (MCP) Governance Gateway in standalone mode
uv run agentic-mcp --port 8000
```

---

## 3. Active Community Issues & Strategic Roadmap

Our current engineering priorities are tracked across 6 open GitHub issues:

| Issue | Title & Technical Scope | Complexity | Reference Documentation |
| :--- | :--- | :---: | :--- |
| **[#1](https://github.com/nolll77/agentic-ops/issues/1)** | **Denial Reconciliation in Evidence Store**: Link operator rejection back to origin episode in WORM ledger. | Medium | `docs/SELF_HOSTED_SCOPE_EXECUTION_PLAN_NOV_2026.md` |
| **[#2](https://github.com/nolll77/agentic-ops/issues/2)** | **Deterministic Worker Failure Drills**: At-least-once delivery, isolated crash injection, and idempotent recovery. | High | `docs/SELF_HOSTED_SCOPE_EXECUTION_PLAN_NOV_2026.md` |
| **[#3](https://github.com/nolll77/agentic-ops/issues/3)** | **Local Inventory Lifecycle & Drift**: Staleness, tampering detection, schema verification, and atomic reloads. | Medium | `docs/SELF_HOSTED_SCOPE_EXECUTION_PLAN_NOV_2026.md` |
| **[#4](https://github.com/nolll77/agentic-ops/issues/4)** | **Local Backup / Restore Drills**: Automated rehearsals of SQLite WAL and WORM snapshot restoration. | Medium | `agentic_ops/core/sqlite_backup.py` |
| **[#5](https://github.com/nolll77/agentic-ops/issues/5)** | **Local Alert Ingestion Benchmark**: Scalability and latency percentiles under burst alert storms. | Medium | `agentic_ops/entrypoints/alert_benchmark.py` |
| **[#6](https://github.com/nolll77/agentic-ops/issues/6)** | **Benchmark of Free OpenRouter LLMs**: Empirical evaluation of 17+ `:free` models across MAS roles. | High | `docs/OPENROUTER_FREE_MODELS_GUIDE.md` |

For future milestones covering Server-Sent Events (`SSE`), EU AI Act Article 12 compliance exports, and Judicial Multi-Agent Quorums, please consult the **[Model Context Protocol Roadmap (`docs/MCP_ROADMAP.md`)](docs/MCP_ROADMAP.md)**.

---

## 4. Contributing to Issue #6: OpenRouter Free Models Benchmark

We actively seek researchers and engineers to benchmark free models (`:free`) on OpenRouter across our **5 cognitive MAS roles**:

1. **Target Cognitive Roles**:
   - `DataSpecialist`: Parsing covariance matrices, evaluating Evidently AI drift reports.
   - `ModelSpecialist`: Detecting calibration drift, tracking F1 degradation.
   - `InfraSpecialist`: Triaging voluminous Grafana Loki logs and Prometheus metrics.
   - `RemediationAgent`: Generating step-by-step CoT action plans adhering to blast-radius limits.
   - `WebChatAssistant`: Fluid human operator interaction with low Time-to-First-Token (`TTFT`).
2. **Evaluation Metrics**:
   - Pydantic v2 JSON schema adherence (parsing failure rate).
   - Resistance to adversarial prompt injections (`SC-101`, `SC-102`).
   - Roundtrip latency and behavior under HTTP 429 rate-limiting.

---

## 5. Coding Standards & Review Guidelines

1. **Strict Monospace Typographical Formatting**:
   - All code symbols, function names, classes, commands, files, and environment variables must be enclosed in backticks (e.g. `PolicyEngine`, `ActionProposal`, `uv sync`, `server.json`).
2. **Type Hints & Schemas**:
   - All new functions must include Python 3.11+ type hints (`from typing import Optional, Dict, List` or native `dict[str, Any]`).
   - All external data structures must be modeled as Pydantic v2 `BaseModel` classes with explicit field validations.
3. **Deterministic Safety over AI Cleverness**:
   - Never replace deterministic checks with prompt instructions. If a condition can be checked with a Python `if` statement or regex, it **must** be implemented in Python.
4. **Test Coverage**:
   - Every bug fix or new feature must be accompanied by automated tests in `tests/`.
   - Tests must run deterministically with `uv run pytest tests/ -q -p no:randomly`.

---

## 6. Pull Request Workflow

1. **Create a focused topic branch**:
   ```bash
   git checkout -b feat/merkle-inclusion-proof
   # or
   git checkout -b bench/openrouter-qwen-nemotron
   ```
2. **Run linting, formatting, and tests**:
   ```bash
   uv run pytest tests/ -q -p no:randomly
   ```
3. **Submit the Pull Request**:
   - Reference the related GitHub issue in your PR description (e.g. `Closes #1` or `Relates to #6`).
   - Provide concrete test execution output demonstrating your changes.
   - Never commit sensitive secrets, API tokens, or internal credentials.

Thank you for helping us build a resilient, sovereign, and cryptographically verifiable MLOps control plane!
