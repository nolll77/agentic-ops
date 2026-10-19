"""
Agentic-Ops — Model Context Protocol (MCP) Governance Gateway Server.

Implements the Anthropic Model Context Protocol (JSON-RPC 2.0, protocolVersion "2024-11-05")
over dual transports:
  1. STDIO Transport (`python -m agentic_ops.entrypoints.mcp_server` or `agentic-mcp`)
     for local IDE / Desktop clients (Claude Desktop, Cursor, Windsurf, Google Antigravity).
  2. HTTP JSON-RPC 2.0 Transport (`POST /mcp` and `GET /mcp/manifest`) mounted directly
     on the FastAPI Control Plane (`https://agentic-ops-5ebv.onrender.com/mcp`).

Capabilities exposed:
  - 8 Governed MCP Tools (including live `/console` reader, deterministic PolicyEngine
    evaluator, WORM Trust Ledger verifier, 435-Risk Taxonomy search, and Tailscale Pull).
  - 5 Foundational MCP Resources (435 Failure Modes Taxonomy, 20 Scenarios Registry,
    Autonomy Policy YAML, Known Gaps Matrix, Live Control Plane Vitals).
  - 20 Starter MCP Prompts covering SRE, SecOps, Drift Governance, WORM Forensics,
    and Executive Jury Defense.
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from agentic_ops.adapters.cac_pull_collector import CacPullCollector
from agentic_ops.core.contracts import (
    ActionProposal,
    ActionType,
    Decision,
    DecisionEnum,
    Diagnosis,
    Episode,
    Finding,
    Signal,
)
from agentic_ops.core.evidence import EvidenceStore
from agentic_ops.core.facts import Observation, SEV, SystemFacts, compute_facts
from agentic_ops.core.local_inventory import inventory_from_environment
from agentic_ops.core.policy_engine import (
    EvalContext,
    PolicyBundle,
    ProposalView,
    evaluate,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
GOVERNANCE_DIR = REPO_ROOT / "agentic_ops" / "governance"
KNOWN_GAPS_PATH = REPO_ROOT / "tests" / "known_gaps.yaml"
DOCS_DIR = REPO_ROOT / "docs"
SCENARIOS_DATA_DIR = REPO_ROOT / "tests" / "scenarios" / "data"

MCP_PROTOCOL_VERSION = "2024-11-05"
SERVER_INFO = {
    "name": "agentic-ops-mcp-gateway",
    "version": "0.1.4",
    "description": (
        "Deterministic MLOps & SRE Governance Control Plane MCP Server "
        "(8 Tools, 5 Knowledge Resources, 20 Starter Prompts)"
    ),
}

router = APIRouter(tags=["MCP (Model Context Protocol)"])


# ============================================================================
# 1. MCP TOOLS DEFINITIONS (8 GOVERNED TOOLS)
# ============================================================================

MCP_TOOLS: List[Dict[str, Any]] = [
    {
        "name": "read_console_diagnostic",
        "description": (
            "Reads and executes any live diagnostic phase from the Agentic-Ops Web Console (/console). "
            "Returns the compact pytest PASSED results at the top followed by the color-coded cognitive "
            "pedagogical guide ([GUIDE:ROLE], [GUIDE:AGENT], [GUIDE:SLACK], [GUIDE:PROD], [GUIDE:HOW_IT_PASSES])."
        ),
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
        "read_only_hint": True,
        "destructive_hint": False,
        "idempotent_hint": True,
        "open_world_hint": False,
        "inputSchema": {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "enum": [
                        "sandbox_phase_a_vitals",
                        "sandbox_phase_b_slack_spoof",
                        "sandbox_phase_c_adversarial_worm",
                        "sandbox_phase_d_mlops_scenarios",
                        "sandbox_phase_e_fsm_governance",
                        "pytest_cac_connector",
                        "pytest_all",
                        "trust_ledger_list",
                        "tailscale_status",
                        "tailscale_netcheck",
                        "redis_ping",
                        "system_info",
                    ],
                    "description": "The exact diagnostic command from the /console Web UI.",
                },
                "include_guides": {
                    "type": "boolean",
                    "default": True,
                    "description": "If False, strips [GUIDE:...] lines to return pure compact test results.",
                },
            },
            "required": ["command"],
        },
    },
    {
        "name": "evaluate_governance_policy",
        "description": (
            "Evaluates a proposed AI agent action against the deterministic PolicyEngine "
            "and the configured exact-name local inventory. Without a fresh local inventory, targets are denied. "
            "Returns ALLOW, REQUIRE_APPROVAL (Slack HITL), or DENY with exact rule IDs."
        ),
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
        "read_only_hint": True,
        "destructive_hint": False,
        "idempotent_hint": True,
        "open_world_hint": False,
        "inputSchema": {
            "type": "object",
            "properties": {
                "risk_id": {
                    "type": "string",
                    "description": "Risk identifier from risk_register.yaml (e.g. DATA-042, INFRA-005, MODEL-012).",
                },
                "action": {
                    "type": "string",
                    "enum": [
                        "create_issue",
                        "investigate",
                        "propose_retrain",
                        "restart_pod",
                        "scale_up",
                        "scale_to_zero",
                        "rollback",
                        "promote_model",
                    ],
                    "description": "Action proposed by the cognitive agent.",
                },
                "target": {
                    "type": "string",
                    "default": "service/prediction-api",
                    "description": "Exact target identifier from the configured local inventory.",
                },
                "upstream_data_severity": {
                    "type": "string",
                    "enum": ["OK", "WARNING", "CRITICAL", "UNKNOWN"],
                    "default": "OK",
                    "description": "Severity of upstream DATA layer (triggers R-001 upstream_masks_service if CRITICAL).",
                },
                "recent_executions_last_hour": {
                    "type": "integer",
                    "default": 0,
                    "description": "Number of times this action ran in the last hour (triggers rate_limit_exceeded if >= limit).",
                },
            },
            "required": ["risk_id", "action"],
        },
    },
    {
        "name": "run_governed_incident_episode",
        "description": (
            "Executes a full end-to-end governed incident episode through the PolicyEngine and seals "
            "the record into the local trust ledger. A fresh configured local inventory is required for an allowed target."
        ),
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": False,
        "read_only_hint": False,
        "destructive_hint": False,
        "idempotent_hint": False,
        "open_world_hint": False,
        "inputSchema": {
            "type": "object",
            "properties": {
                "risk_id": {"type": "string", "description": "Risk ID (e.g. DATA-042, INFRA-005)."},
                "action": {
                    "type": "string",
                    "enum": [
                        "create_issue",
                        "investigate",
                        "propose_retrain",
                        "restart_pod",
                        "scale_up",
                        "scale_to_zero",
                        "rollback",
                        "promote_model",
                    ],
                },
                "target": {"type": "string", "default": "service/prediction-api"},
                "finding_summary": {
                    "type": "string",
                    "default": "Elevated drift / anomaly detected on production telemetry.",
                },
                "confidence_score": {"type": "number", "default": 0.92},
            },
            "required": ["risk_id", "action"],
        },
    },
    {
        "name": "inspect_worm_trust_ledger",
        "description": (
            "Audits the append-only WORM Trust Ledger (ledger.jsonl), verifies the full SHA-256 linear hash chain "
            "and HMAC-SHA512 signatures via EvidenceStore.verify_chain(), and returns sealed episodes."
        ),
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
        "read_only_hint": True,
        "destructive_hint": False,
        "idempotent_hint": True,
        "open_world_hint": False,
        "inputSchema": {
            "type": "object",
            "properties": {
                "episode_id": {
                    "type": "string",
                    "description": "Optional specific episode ID (e.g. EP-0001). Omit to list all episodes and verify chain.",
                },
                "limit": {
                    "type": "integer",
                    "default": 10,
                    "description": "Max recent episodes to return.",
                },
            },
        },
    },
    {
        "name": "search_failure_taxonomy",
        "description": (
            "Searches the foundational 435 MLOps Failure Modes Taxonomy (docs/mlops_failure_modes_taxonomy.md) "
            "by keyword, risk ID, dimension, or symptom."
        ),
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
        "read_only_hint": True,
        "destructive_hint": False,
        "idempotent_hint": True,
        "open_world_hint": False,
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Keyword or pattern to search (e.g. 'drift', 'OOM', 'Feast', 'shadow', 'deadlock').",
                },
                "max_results": {
                    "type": "integer",
                    "default": 10,
                    "description": "Maximum matching lines/rows to return.",
                },
            },
            "required": ["query"],
        },
    },
    {
        "name": "get_scenario_blueprint",
        "description": (
            "Retrieves the architectural specification from docs/mlops_simulation_scenarios_registry.md and/or "
            "the executable YAML scenario contract from tests/scenarios/data/*.yaml."
        ),
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
        "read_only_hint": True,
        "destructive_hint": False,
        "idempotent_hint": True,
        "open_world_hint": False,
        "inputSchema": {
            "type": "object",
            "properties": {
                "scenario_id": {
                    "type": "string",
                    "description": "Scenario identifier (e.g. 'SC-101', 'SC-102', 'SC-103', 'SC-001', 'SC-003', 'SC-004', 'SC-005', 'SIM-1', 'all').",
                }
            },
            "required": ["scenario_id"],
        },
    },
    {
        "name": "poll_target_mlops_snapshot",
        "description": (
            "Executes a 100% Read-Only HTTP GET pull collection via CacPullCollector across the 5 observability "
            "endpoints of the target MLOps platform (jakatt/cac_mlops) over the Tailscale SOCKS5 mesh."
        ),
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
        "read_only_hint": True,
        "destructive_hint": False,
        "idempotent_hint": True,
        "open_world_hint": True,
        "inputSchema": {
            "type": "object",
            "properties": {
                "use_proxy": {"type": "boolean", "default": True},
                "timeout": {"type": "number", "default": 3.5},
            },
        },
    },
    {
        "name": "inspect_control_plane_vitals",
        "description": (
            "Returns real-time health, socket status (Redis :6379, Tailscale SOCKS5 :1055), "
            "Linux cgroup v2 memory telemetry, and active PolicyBundle version hash."
        ),
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
        "read_only_hint": True,
        "destructive_hint": False,
        "idempotent_hint": True,
        "open_world_hint": False,
        "inputSchema": {"type": "object", "properties": {}},
    },
]


# ============================================================================
# 2. MCP RESOURCES DEFINITIONS (5 KNOWLEDGE RESOURCES)
# ============================================================================

MCP_RESOURCES: List[Dict[str, Any]] = [
    {
        "uri": "agentic-ops://taxonomy/failure-modes",
        "name": "MLOps 435 Failure Modes Taxonomy",
        "description": "Exhaustive 10-dimension ontology of 435 MLOps failure modes (docs/mlops_failure_modes_taxonomy.md).",
        "mimeType": "text/markdown",
    },
    {
        "uri": "agentic-ops://registry/scenarios",
        "name": "MLOps 20 Scenarios Registry",
        "description": "Foundational specification of the 20 MLOps crisis scenarios SIM-1 to SIM-20 (docs/mlops_simulation_scenarios_registry.md).",
        "mimeType": "text/markdown",
    },
    {
        "uri": "agentic-ops://governance/autonomy-policy",
        "name": "Deterministic Autonomy Policy & Risk Register",
        "description": "Compiled YAML governance bundle (autonomy_policy.yaml, action_catalog.yaml, risk_register.yaml).",
        "mimeType": "application/json",
    },
    {
        "uri": "agentic-ops://governance/known-gaps",
        "name": "Known Gaps & Adversarial Boundary Matrix",
        "description": "Formal registry of adversarial boundaries and test mappings (governance/known_gaps.yaml).",
        "mimeType": "text/yaml",
    },
    {
        "uri": "agentic-ops://console/vitals",
        "name": "Live Control Plane Vitals & Console Commands",
        "description": "Real-time status of Redis, Tailscale SOCKS5, PolicyBundle version, and available /console diagnostics.",
        "mimeType": "application/json",
    },
]


# ============================================================================
# 3. THE 20 COGNITIVE STARTER PROMPTS CATALOG
# ============================================================================

MCP_PROMPTS: List[Dict[str, Any]] = [
    # --- Category I: Live Web Console (/console) Reading & Auditing (1-4) ---
    {
        "name": "01_console_grand_slam_audit",
        "description": "[Console Live] Run all 42 Sandbox + CAC tests via /console and verify forbidden_executed=0.",
        "arguments": [],
        "template": (
            "Call the MCP tool `read_console_diagnostic` with `command='pytest_all'` and `include_guides=True`. "
            "Verify that all 42 tests pass (`PASSED`) and that `forbidden_executed=0` across all adversarial scenarios. "
            "Provide a structured SRE audit table breaking down Phase C (WORM), Phase D (Scenarios), Phase E (FSM), and Phase F (CAC Pull)."
        ),
    },
    {
        "name": "02_console_vitals_and_cgroup_check",
        "description": "[Console Live] Inspect container CPU/RAM cgroup v2 limits, Redis :6379, and Tailscale :1055.",
        "arguments": [],
        "template": (
            "Call `read_console_diagnostic` with `command='sandbox_phase_a_vitals'` and `inspect_control_plane_vitals`. "
            "Analyze the kernel version, CPU model, `/proc/meminfo` vs `cgroup v2` memory usage, and confirm whether "
            "Redis (`127.0.0.1:6379`), Tailscale SOCKS5 (`127.0.0.1:1055`), and SQLite WAL (`approvals.db`) are operational."
        ),
    },
    {
        "name": "03_console_redteam_slack_spoof",
        "description": "[Console Live] Trigger Phase B Red-Team Slack webhook spoofing attack and verify HTTP 401.",
        "arguments": [],
        "template": (
            "Call `read_console_diagnostic` with `command='sandbox_phase_b_slack_spoof'`. "
            "Explain step-by-step how `agentic_ops/entrypoints/slack_webhook.py` intercepts the forged payload "
            "`payload=fake_tampered_attack`, verifies `X-Slack-Signature` (`HMAC-SHA256`), and enforces a Fail-Closed `HTTP 401`."
        ),
    },
    {
        "name": "04_console_live_pull_cac_mlops",
        "description": "[Console Live] Poll the 5 remote observability endpoints of jakatt/cac_mlops over Tailscale.",
        "arguments": [],
        "template": (
            "Call `poll_target_mlops_snapshot` with `use_proxy=True` and `timeout=3.5`. "
            "Report the connectivity status of each of the 5 remote targets (`FastAPI`, `Evidently`, `MLflow`, `Prometheus`, `Grafana`). "
            "If `status='REMOTE_TARGET_OFFLINE'`, explain how the Fail-Safe read-only degradation protects the Control Plane."
        ),
    },
    # --- Category II: Deterministic PolicyEngine & Risk Arbitration (5-8) ---
    {
        "name": "05_policy_veto_corrupted_sensor",
        "description": "[PolicyEngine] Prove how CAT-001 blocks model retraining on corrupted upstream data (DATA-042).",
        "arguments": [
            {"name": "risk_id", "description": "Risk ID (default DATA-042)", "required": False},
        ],
        "template": (
            "Call `evaluate_governance_policy` with `risk_id='DATA-042'`, `action='propose_retrain'`, "
            "`target='model/baac_classifier'`, and `upstream_data_severity='CRITICAL'`. "
            "Explain why the deterministic PolicyEngine returns `DENY` (`risk_register_forbids` / `CAT-001`) "
            "even if the LLM agent is 99% confident that retraining will fix the drift."
        ),
    },
    {
        "name": "06_policy_veto_thrashing_cooldown",
        "description": "[PolicyEngine] Prove how rate-limiting and R-001 prevent Kubernetes pod restart storms (INFRA-005).",
        "arguments": [],
        "template": (
            "Call `evaluate_governance_policy` twice for `risk_id='INFRA-005'`, `action='restart_pod'`, `target='service/api'`: "
            "first with `recent_executions_last_hour=0` and `upstream_data_severity='OK'`, then with `recent_executions_last_hour=5` "
            "and `upstream_data_severity='CRITICAL'`. Compare the two verdicts and explain rules `R-001` and `rate_limit_exceeded`."
        ),
    },
    {
        "name": "07_policy_hitl_slack_escalation",
        "description": "[PolicyEngine] Demonstrate L2/L3 Human-in-the-Loop Slack escalation on model rollback.",
        "arguments": [],
        "template": (
            "Call `evaluate_governance_policy` with `risk_id='MODEL-012'`, `action='rollback'`, "
            "`target='model/baac_rf_v2'`. Ensure that exact target is present in the fresh local inventory, "
            "then explain how the inventory-derived blast radius and action catalog level (`L2`/`L3`) can require approval and prevent execution until approval is recorded."
        ),
    },
    {
        "name": "08_policy_l1_autonomy_fastpath",
        "description": "[PolicyEngine] Verify zero-touch L1 autonomy fast-path for safe non-mutating ticketing.",
        "arguments": [],
        "template": (
            "Call `evaluate_governance_policy` with `risk_id='DATA-042'`, `action='create_issue'`, "
            "`target='repo/mlops-incidents'`. Show why `create_issue` (`mutating=False`, `blast_radius=0`, `level=L1`) "
            "is immediately granted `ALLOW` without human friction."
        ),
    },
    # --- Category III: WORM Trust Ledger Forensics & Cryptography (9-12) ---
    {
        "name": "09_worm_ledger_chain_verification",
        "description": "[WORM Forensics] Verify the SHA-256 linear hash chain and HMAC-SHA512 signatures of all episodes.",
        "arguments": [],
        "template": (
            "Call `inspect_worm_trust_ledger` with `limit=20`. Verify whether `chain_valid` is `True`, "
            "inspect the `previous_hash -> hash` cryptographic links across episodes, and explain how "
            "`agentic_ops/core/crypto.py` signs canonical JSON payloads with `HMAC-SHA512`."
        ),
    },
    {
        "name": "10_worm_simulate_and_seal_episode",
        "description": "[WORM Forensics] Execute a live incident episode and seal its cryptographic proof in the ledger.",
        "arguments": [
            {"name": "risk_id", "description": "Risk ID (default DATA-042)", "required": False},
            {"name": "action", "description": "Action (default create_issue)", "required": False},
        ],
        "template": (
            "Call `run_governed_incident_episode` with `risk_id='DATA-042'`, `action='create_issue'`, "
            "`target='repo/mlops-incidents'`, and `finding_summary='PSI drift 0.42 > 0.25 on feature an_nais'`. "
            "Then call `inspect_worm_trust_ledger` on the newly created `episode_id` and display its full cryptographic proof."
        ),
    },
    {
        "name": "11_worm_tamper_detection_audit",
        "description": "[WORM Forensics] Run the 9 adversarial & WORM security tests from Phase C and explain tamper detection.",
        "arguments": [],
        "template": (
            "Call `read_console_diagnostic` with `command='sandbox_phase_c_adversarial_worm'`. "
            "Analyze the 9 security tests (`test_evidence_integrity.py`, `test_idempotency_and_rate.py`, `test_prompt_hygiene.py`, "
            "`test_executor.py`) and explain how a 1-byte modification on disk breaks `verify_chain()`."
        ),
    },
    {
        "name": "12_worm_eu_ai_act_compliance_report",
        "description": "[WORM Forensics] Generate an EU AI Act Article 14 (Human Oversight & Traceability) audit report.",
        "arguments": [],
        "template": (
            "Read resource `agentic-ops://governance/autonomy-policy` and call `inspect_worm_trust_ledger`. "
            "Draft a formal compliance assessment mapping Agentic-Ops controls (Deterministic PolicyEngine, Slack HITL "
            "`AWAITING_APPROVAL`, WORM `HMAC-SHA512` Trust Ledger) to EU AI Act Articles 12 (Record-Keeping) and 14 (Human Oversight)."
        ),
    },
    # --- Category IV: Knowledge Engineering — 435 Taxonomy & Scenarios Registry (13-16) ---
    {
        "name": "13_taxonomy_deep_search_drift",
        "description": "[Knowledge Base] Search the 435 Failure Modes Taxonomy for Data/Concept Drift & Skew risks.",
        "arguments": [
            {"name": "query", "description": "Search term (default drift)", "required": False},
        ],
        "template": (
            "Call `search_failure_taxonomy` with `query='drift'` and `max_results=15`. "
            "Group the discovered failure modes by MLOps Dimension, highlight their early warning signals, "
            "and map them to deterministic `PolicyEngine` rules."
        ),
    },
    {
        "name": "14_scenario_lineage_sim1_to_sc001",
        "description": "[Knowledge Base] Trace the code lineage from SIM-1 in the Scenarios Registry to SC-001 YAML.",
        "arguments": [],
        "template": (
            "Call `get_scenario_blueprint` with `scenario_id='SC-001'` and `scenario_id='SIM-1'`. "
            "Demonstrate the exact lineage between the prose architectural specification in `mlops_simulation_scenarios_registry.md`, "
            "the declarative test contract in `tests/scenarios/data/sc_001_bad_retrain.yaml`, and `risk_register.yaml`."
        ),
    },
    {
        "name": "15_scenario_adversarial_triad_analysis",
        "description": "[Knowledge Base] Deep-dive into adversarial scenarios SC-101, SC-102, and SC-103.",
        "arguments": [],
        "template": (
            "Call `get_scenario_blueprint` for `SC-101`, `SC-102`, and `SC-103`, then call `read_console_diagnostic` "
            "with `command='sandbox_phase_d_mlops_scenarios'`. Explain how the 3 adversarial traps (Prompt Injection, "
            "Alert Storm Thrashing, Corrupted Sensor Drift) attempt to trick the LLM (`forbidden_proposed=6`) and why "
            "`forbidden_executed` remains strictly `0`."
        ),
    },
    {
        "name": "16_design_new_scenario_sim9_to_sim20",
        "description": "[Knowledge Base] Synthesize a new executable YAML scenario contract from SIM-9..SIM-20.",
        "arguments": [
            {"name": "sim_id", "description": "Scenario ID from registry (e.g. SIM-9)", "required": False},
        ],
        "template": (
            "Call `get_scenario_blueprint` with `scenario_id='SIM-9'` and `search_failure_taxonomy` with `query='Feast'`. "
            "Generate a complete, ready-to-run YAML test file following the exact schema of `tests/scenarios/data/sc_001_bad_retrain.yaml` "
            "including `signal`, `events`, `llm_scripted`, and `expected` assertions."
        ),
    },
    # --- Category V: SecOps, Red-Teaming & Executive Jury Defense (17-20) ---
    {
        "name": "17_secops_prompt_injection_audit",
        "description": "[SecOps] Audit indirect prompt injection defenses (PromptGuard + PolicyEngine veto on scale_to_zero).",
        "arguments": [],
        "template": (
            "Call `get_scenario_blueprint` with `scenario_id='SC-101'` and `evaluate_governance_policy` with "
            "`risk_id='INFRA-005'`, `action='scale_to_zero'`, `target='service/prediction-api'`. "
            "Explain the Defense-in-Depth architecture: Layer 1 (`PromptGuard` sanitization) and Layer 2 (`PolicyEngine` hard veto on `scale_to_zero`)."
        ),
    },
    {
        "name": "18_secops_tool_sandboxing_verification",
        "description": "[SecOps] Verify OS-level multiprocessing.Process sandboxing and 15s SIGKILL timeout (Phase E).",
        "arguments": [],
        "template": (
            "Call `read_console_diagnostic` with `command='sandbox_phase_e_fsm_governance'`. "
            "Explain why Python `ThreadPoolExecutor` timeouts cannot kill hung I/O threads, and how `AgentTool` in "
            "`agentic_ops/tools/base.py` isolates every tool call inside a dedicated `multiprocessing.Process` with `process.terminate()`."
        ),
    },
    {
        "name": "19_sre_tailscale_mesh_diagnostics",
        "description": "[SRE Mesh] Audit Tailscale userspace WireGuard tunnel, DERP relays, and PII auto-redaction.",
        "arguments": [],
        "template": (
            "Call `read_console_diagnostic` with `command='tailscale_status'` and `command='tailscale_netcheck'`. "
            "Analyze the userspace WireGuard mesh state, nearest DERP relay latencies, `TS_STATE_B64` persistence across "
            "Render serverless cold starts, and verify that `_redact_pii()` masks all personal hostnames/emails."
        ),
    },
    {
        "name": "20_executive_jury_defense_briefing",
        "description": "[Jury Defense] Generate a 5-point Executive Defense Briefing from live telemetry & 42 tests.",
        "arguments": [],
        "template": (
            "Execute `inspect_control_plane_vitals`, `read_console_diagnostic(command='pytest_all', include_guides=False)`, "
            "and `inspect_worm_trust_ledger(limit=5)`. Synthesize a punchy 5-point Executive Jury Briefing proving: "
            "(1) Architectural Agnosticism, (2) Deterministic Safety (`forbidden_executed=0`), (3) Cryptographic WORM Auditability, "
            "(4) Zero-Trust Tailscale Mesh Connectivity, and (5) Foundational Knowledge Lineage (`435 Failure Modes` -> Code)."
        ),
    },
]


# ============================================================================
# 4. TOOL & RESOURCE EXECUTION ENGINE
# ============================================================================


def _execute_mcp_tool(name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Executes one of the 8 governed MCP tools and returns an MCP CallToolResult dict."""
    try:
        if name == "read_console_diagnostic":
            from agentic_ops.cli.main import DiagnosticCommand, run_diagnostic_command

            cmd_str = arguments.get("command", "sandbox_phase_a_vitals")
            include_guides = bool(arguments.get("include_guides", True))
            cmd_enum = DiagnosticCommand(cmd_str)
            resp = run_diagnostic_command(cmd_enum)
            raw_text = resp if isinstance(resp, str) else resp.body.decode("utf-8", errors="replace")
            if not include_guides:
                filtered = [
                    ln
                    for ln in raw_text.splitlines()
                    if not ln.startswith("[GUIDE:") and not ln.startswith("====")
                ]
                raw_text = "\n".join(filtered)
            return {
                "content": [{"type": "text", "text": raw_text}],
                "isError": False,
            }

        elif name == "evaluate_governance_policy":
            bundle = PolicyBundle.load(
                GOVERNANCE_DIR / "autonomy_policy.yaml",
                GOVERNANCE_DIR / "action_catalog.yaml",
                GOVERNANCE_DIR / "risk_register.yaml",
            )
            risk_id = str(arguments.get("risk_id", "DATA-042"))
            action = str(arguments.get("action", "create_issue"))
            target = str(arguments.get("target", "service/prediction-api"))
            upstream_sev_str = str(arguments.get("upstream_data_severity", "OK")).upper()
            recent_count_val = int(arguments.get("recent_executions_last_hour", 0))

            now = datetime.now(timezone.utc)
            norm_sev = "INFO" if upstream_sev_str in ("OK", "INFO") else upstream_sev_str
            obs = [
                Observation(
                    layer="DATA",
                    severity=norm_sev,
                    timestamp=now,
                )
            ]
            facts = compute_facts(obs, as_of=now)
            view = ProposalView(action=action, target=target, risk_id=risk_id)
            ctx = EvalContext(
                facts=facts,
                inventory=inventory_from_environment(),
                recent_count=lambda act, win: recent_count_val,
            )
            verdict = evaluate(bundle, view, ctx)
            payload = {
                "tool": "evaluate_governance_policy",
                "input": {
                    "risk_id": risk_id,
                    "action": action,
                    "target": target,
                    "upstream_data_severity": upstream_sev_str,
                    "recent_executions_last_hour": recent_count_val,
                },
                "verdict": verdict.model_dump(mode="json"),
            }
            return {
                "content": [{"type": "text", "text": json.dumps(payload, indent=2, ensure_ascii=False)}],
                "isError": False,
            }

        elif name == "run_governed_incident_episode":
            bundle = PolicyBundle.load(
                GOVERNANCE_DIR / "autonomy_policy.yaml",
                GOVERNANCE_DIR / "action_catalog.yaml",
                GOVERNANCE_DIR / "risk_register.yaml",
            )
            risk_id = str(arguments.get("risk_id", "DATA-042"))
            action_str = str(arguments.get("action", "create_issue")).lower()
            target = str(arguments.get("target", "mlops-incidents"))
            summary = str(arguments.get("finding_summary", "Triggered via MCP Governance Gateway"))
            confidence = float(arguments.get("confidence_score", 0.92))

            now = datetime.now(timezone.utc)
            facts = compute_facts([Observation(layer="DATA", severity="WARNING", timestamp=now)], as_of=now)
            view = ProposalView(action=action_str, target=target, risk_id=risk_id)
            ctx = EvalContext(
                facts=facts,
                inventory=inventory_from_environment(),
                recent_count=lambda act, win: 0,
            )
            verdict = evaluate(bundle, view, ctx)

            store_dir = os.environ.get("EVIDENCE_STORE_DIR", str(REPO_ROOT / "state" / "episodes"))
            store = EvidenceStore(store_dir)
            ep_id = store.next_episode_id()

            terminal_state = (
                "RESOLVED"
                if verdict.effect == "ALLOW"
                else ("AWAITING_APPROVAL" if verdict.effect == "REQUIRE_APPROVAL" else "DENIED")
            )
            state_trace = ["DETECTED", "INVESTIGATING", "DIAGNOSED", "PLANNED"]
            if verdict.effect == "ALLOW":
                state_trace.extend(["EXECUTING", "RESOLVED"])
            else:
                state_trace.append(terminal_state)

            ep_dict = {
                "episode_id": ep_id,
                "dedup_key": f"mcp-{risk_id}-{action_str}-{int(now.timestamp())}",
                "timestamp_utc": now.isoformat(),
                "state_trace": state_trace,
                "risk_id": risk_id,
                "signal": {
                    "signal_id": f"SIG-MCP-{ep_id}",
                    "source": "mcp_governance_gateway",
                    "observed_at": now.isoformat(),
                    "metadata": {"finding_summary": summary},
                },
                "diagnosis": {
                    "layer": risk_id.split("-")[0],
                    "findings": [{"description": summary}],
                    "confidence_score": confidence,
                    "risk_id": risk_id,
                    "agent": "mcp_client_agent",
                },
                "action_proposal": {
                    "type": action_str,
                    "target": target,
                    "risk_id": risk_id,
                    "requested_by": "mcp_client_agent",
                    "reversible": bool(verdict.computed_reversible),
                    "blast_radius": int(verdict.computed_blast_radius or 0),
                },
                "policy_evaluation": {
                    "decision": verdict.effect,
                    "matched_rule": ",".join(verdict.rule_ids) if verdict.rule_ids else "default_allow",
                    "reason_codes": verdict.reasons,
                },
                "human_approval_required": verdict.effect == "REQUIRE_APPROVAL",
                "policy_version": verdict.policy_version,
                "inventory_version": verdict.inventory_version,
            }
            ledger_path = store.save(ep_dict)
            result = {
                "status": "EPISODE_SEALED_IN_WORM_LEDGER",
                "episode_id": ep_id,
                "terminal_fsm_state": terminal_state,
                "policy_decision": verdict.effect,
                "matched_rules": verdict.rule_ids,
                "reasons": verdict.reasons,
                "previous_hash": ep_dict.get("previous_hash"),
                "sha256_hash": ep_dict.get("hash"),
                "hmac_sha512_signature": ep_dict.get("cryptographic_signature"),
                "ledger_file": ledger_path,
            }
            return {
                "content": [{"type": "text", "text": json.dumps(result, indent=2, ensure_ascii=False)}],
                "isError": False,
            }

        elif name == "inspect_worm_trust_ledger":
            store_dir = os.environ.get("EVIDENCE_STORE_DIR", str(REPO_ROOT / "state" / "episodes"))
            store = EvidenceStore(store_dir)
            chain_valid = store.verify_chain()
            target_ep = arguments.get("episode_id")
            limit = int(arguments.get("limit", 10))

            episodes: List[Dict[str, Any]] = []
            if store.ledger_file.exists():
                for line in store.ledger_file.read_text(encoding="utf-8").splitlines():
                    if line.strip():
                        try:
                            ep = json.loads(line)
                            if not target_ep or ep.get("episode_id") == target_ep:
                                episodes.append(ep)
                        except Exception:
                            pass

            payload = {
                "worm_ledger_file": str(store.ledger_file),
                "linear_chain_and_hmac_valid": chain_valid,
                "merkle_chain_and_hmac_valid": chain_valid,  # alias for backward-compatibility
                "total_matching_episodes": len(episodes),
                "episodes": episodes[-limit:],
            }
            return {
                "content": [{"type": "text", "text": json.dumps(payload, indent=2, ensure_ascii=False)}],
                "isError": False,
            }

        elif name == "search_failure_taxonomy":
            query = str(arguments.get("query", "")).strip().lower()
            max_results = int(arguments.get("max_results", 10))
            taxo_path = DOCS_DIR / "mlops_failure_modes_taxonomy.md"
            if not taxo_path.exists():
                return {
                    "content": [{"type": "text", "text": "Taxonomy file not found."}],
                    "isError": True,
                }
            matches: List[str] = []
            current_section = "Header"
            for line_no, line in enumerate(taxo_path.read_text(encoding="utf-8").splitlines(), 1):
                if line.startswith("## ") or line.startswith("### "):
                    current_section = line.strip()
                if query in line.lower():
                    matches.append(f"[L{line_no} | {current_section}] {line.strip()}")
                    if len(matches) >= max_results:
                        break
            payload = {
                "taxonomy_source": "docs/mlops_failure_modes_taxonomy.md (435 Failure Modes)",
                "query": query,
                "matches_returned": len(matches),
                "results": matches,
            }
            return {
                "content": [{"type": "text", "text": json.dumps(payload, indent=2, ensure_ascii=False)}],
                "isError": False,
            }

        elif name == "get_scenario_blueprint":
            sc_id = str(arguments.get("scenario_id", "all")).strip().upper()
            out: Dict[str, Any] = {"requested_id": sc_id, "yaml_contracts": {}, "registry_excerpts": []}

            if SCENARIOS_DATA_DIR.exists():
                for ypath in sorted(SCENARIOS_DATA_DIR.rglob("*.yaml")):
                    content = ypath.read_text(encoding="utf-8")
                    if sc_id == "ALL" or sc_id.lower().replace("-", "_") in ypath.name.lower() or sc_id in content:
                        out["yaml_contracts"][ypath.name] = content

            reg_path = DOCS_DIR / "mlops_simulation_scenarios_registry.md"
            if reg_path.exists():
                reg_text = reg_path.read_text(encoding="utf-8")
                if sc_id == "ALL":
                    out["registry_excerpts"] = [
                        ln for ln in reg_text.splitlines() if ln.startswith("## ") or ln.startswith("### ")
                    ]
                else:
                    lines = reg_text.splitlines()
                    for idx, ln in enumerate(lines):
                        if sc_id in ln.upper():
                            snippet = "\n".join(lines[max(0, idx - 2) : min(len(lines), idx + 35)])
                            out["registry_excerpts"].append(snippet)
                            if len(out["registry_excerpts"]) >= 3:
                                break

            return {
                "content": [{"type": "text", "text": json.dumps(out, indent=2, ensure_ascii=False)}],
                "isError": False,
            }

        elif name == "poll_target_mlops_snapshot":
            from agentic_ops.cli.main import _is_port_open

            use_proxy = bool(arguments.get("use_proxy", True))
            timeout = float(arguments.get("timeout", 3.5))
            proxy_open = _is_port_open("127.0.0.1", 1055)
            collector = CacPullCollector(use_proxy_for_vps=(use_proxy and proxy_open), timeout=timeout)
            snap = collector.collect_all()
            return {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps(snap.model_dump(mode="json"), indent=2, ensure_ascii=False),
                    }
                ],
                "isError": False,
            }

        elif name == "inspect_control_plane_vitals":
            from agentic_ops.cli.main import DiagnosticCommand, _is_port_open

            bundle = PolicyBundle.load(
                GOVERNANCE_DIR / "autonomy_policy.yaml",
                GOVERNANCE_DIR / "action_catalog.yaml",
                GOVERNANCE_DIR / "risk_register.yaml",
            )
            vitals = {
                "service": "agentic-ops-control-plane",
                "mcp_protocol_version": MCP_PROTOCOL_VERSION,
                "redis_local_6379": _is_port_open("127.0.0.1", 6379),
                "tailscale_socks5_1055": _is_port_open("127.0.0.1", 1055),
                "active_policy_bundle_version": bundle.version,
                "governed_actions_count": len(bundle.catalog.actions),
                "registered_risks_count": len(bundle.forbidden_by_risk),
                "available_console_commands": [c.value for c in DiagnosticCommand],
            }
            return {
                "content": [{"type": "text", "text": json.dumps(vitals, indent=2, ensure_ascii=False)}],
                "isError": False,
            }

        else:
            return {
                "content": [{"type": "text", "text": f"Unknown MCP tool: {name}"}],
                "isError": True,
            }
    except Exception as exc:
        return {
            "content": [{"type": "text", "text": f"Tool execution error ({name}): {exc}"}],
            "isError": True,
        }


def _read_mcp_resource(uri: str) -> Dict[str, Any]:
    """Reads one of the 5 foundational MCP resources."""
    if uri == "agentic-ops://taxonomy/failure-modes":
        path = DOCS_DIR / "mlops_failure_modes_taxonomy.md"
        text = path.read_text(encoding="utf-8") if path.exists() else "Not found"
        return {"contents": [{"uri": uri, "mimeType": "text/markdown", "text": text}]}

    if uri == "agentic-ops://registry/scenarios":
        path = DOCS_DIR / "mlops_simulation_scenarios_registry.md"
        text = path.read_text(encoding="utf-8") if path.exists() else "Not found"
        return {"contents": [{"uri": uri, "mimeType": "text/markdown", "text": text}]}

    if uri == "agentic-ops://governance/autonomy-policy":
        bundle = PolicyBundle.load(
            GOVERNANCE_DIR / "autonomy_policy.yaml",
            GOVERNANCE_DIR / "action_catalog.yaml",
            GOVERNANCE_DIR / "risk_register.yaml",
        )
        return {
            "contents": [
                {
                    "uri": uri,
                    "mimeType": "application/json",
                    "text": bundle.model_dump_json(indent=2),
                }
            ]
        }

    if uri == "agentic-ops://governance/known-gaps":
        path = KNOWN_GAPS_PATH
        text = path.read_text(encoding="utf-8") if path.exists() else "Not found"
        return {"contents": [{"uri": uri, "mimeType": "text/yaml", "text": text}]}

    if uri == "agentic-ops://console/vitals":
        res = _execute_mcp_tool("inspect_control_plane_vitals", {})
        return {
            "contents": [
                {
                    "uri": uri,
                    "mimeType": "application/json",
                    "text": res["content"][0]["text"],
                }
            ]
        }

    raise ValueError(f"Unknown MCP resource URI: {uri}")


def _get_mcp_prompt(name: str, arguments: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Retrieves and formats one of the 20 Starter Prompts."""
    for p in MCP_PROMPTS:
        if p["name"] == name:
            text = p["template"]
            if arguments:
                for k, v in arguments.items():
                    text = text + f"\n[Parameter {k}={v}]"
            return {
                "description": p["description"],
                "messages": [
                    {
                        "role": "user",
                        "content": {"type": "text", "text": text},
                    }
                ],
            }
    raise ValueError(f"Unknown MCP prompt: {name}")


# ============================================================================
# 5. JSON-RPC 2.0 MCP PROTOCOL DISPATCHER (STDIO & HTTP)
# ============================================================================


def handle_mcp_jsonrpc(payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Handles a single JSON-RPC 2.0 MCP message and returns a JSON-RPC 2.0 response."""
    method = payload.get("method", "")
    req_id = payload.get("id")
    params = payload.get("params") or {}

    # Notifications (no id) do not return a response
    if req_id is None and method.startswith("notifications/"):
        return None

    try:
        if method == "initialize":
            result = {
                "protocolVersion": MCP_PROTOCOL_VERSION,
                "capabilities": {
                    "tools": {"listChanged": False},
                    "resources": {"subscribe": False, "listChanged": False},
                    "prompts": {"listChanged": False},
                },
                "serverInfo": SERVER_INFO,
            }
        elif method == "ping":
            result = {}
        elif method == "tools/list":
            result = {"tools": MCP_TOOLS}
        elif method == "tools/call":
            tool_name = params.get("name", "")
            tool_args = params.get("arguments") or {}
            result = _execute_mcp_tool(tool_name, tool_args)
        elif method == "resources/list":
            result = {"resources": MCP_RESOURCES}
        elif method == "resources/read":
            uri = params.get("uri", "")
            result = _read_mcp_resource(uri)
        elif method == "prompts/list":
            prompts_public = [
                {
                    "name": p["name"],
                    "description": p["description"],
                    "arguments": p.get("arguments", []),
                }
                for p in MCP_PROMPTS
            ]
            result = {"prompts": prompts_public}
        elif method == "prompts/get":
            prompt_name = params.get("name", "")
            prompt_args = params.get("arguments") or {}
            result = _get_mcp_prompt(prompt_name, prompt_args)
        else:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {"code": -32601, "message": f"Method not found: {method}"},
            }

        return {"jsonrpc": "2.0", "id": req_id, "result": result}

    except Exception as exc:
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "error": {"code": -32602, "message": str(exc)},
        }


# ============================================================================
# 6. FASTAPI HTTP ENDPOINTS (/mcp and /mcp/manifest)
# ============================================================================


@router.get("/mcp/manifest")
def get_mcp_manifest():
    """
    Human- and machine-readable discovery endpoint listing all 8 Governed MCP Tools,
    5 Knowledge Resources, and 20 Cognitive Starter Prompts exposed by Agentic-Ops.
    """
    return {
        "server": SERVER_INFO,
        "protocol_version": MCP_PROTOCOL_VERSION,
        "transports": {
            "http_jsonrpc": "/mcp (POST JSON-RPC 2.0)",
            "stdio": "python -m agentic_ops.entrypoints.mcp_server",
        },
        "counts": {
            "tools": len(MCP_TOOLS),
            "resources": len(MCP_RESOURCES),
            "starter_prompts": len(MCP_PROMPTS),
        },
        "tools": MCP_TOOLS,
        "resources": MCP_RESOURCES,
        "starter_prompts": MCP_PROMPTS,
    }


@router.post("/mcp")
async def post_mcp_jsonrpc(request: Request):
    """
    Standard Model Context Protocol (MCP) JSON-RPC 2.0 HTTP endpoint.
    Accepts `initialize`, `tools/list`, `tools/call`, `resources/list`, `resources/read`,
    `prompts/list`, and `prompts/get`.
    """
    body = await request.json()
    if isinstance(body, list):
        responses = [r for item in body if (r := handle_mcp_jsonrpc(item)) is not None]
        return JSONResponse(content=responses)
    resp = handle_mcp_jsonrpc(body)
    if resp is None:
        return JSONResponse(content={"status": "accepted"}, status_code=202)
    return JSONResponse(content=resp)


# ============================================================================
# 7. STDIO TRANSPORT ENTRYPOINT (FOR CLAUDE DESKTOP / CURSOR / ANTIGRAVITY)
# ============================================================================


def run_stdio_server() -> None:
    """Runs the MCP JSON-RPC 2.0 server over standard input/output (STDIO)."""
    for raw_line in sys.stdin:
        line = raw_line.strip()
        if not line:
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError as exc:
            err_resp = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32700, "message": f"Parse error: {exc}"},
            }
            sys.stdout.write(json.dumps(err_resp) + "\n")
            sys.stdout.flush()
            continue

        response = handle_mcp_jsonrpc(payload)
        if response is not None:
            sys.stdout.write(json.dumps(response) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    run_stdio_server()
