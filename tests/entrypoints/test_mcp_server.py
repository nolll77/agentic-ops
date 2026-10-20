"""
End-to-End & Unit Validation Suite for the Agentic-Ops Model Context Protocol (MCP) Server.
Verifies JSON-RPC 2.0 compliance, live /console diagnostic reading, PolicyEngine arbitration,
WORM Trust Ledger sealing, 435 Failure Modes Taxonomy search, 5 Resources, and 20 Starter Prompts.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from fastapi.testclient import TestClient

from agentic_ops.cli.main import app
from agentic_ops.entrypoints.mcp_server import (
    MCP_PROMPTS,
    MCP_PROTOCOL_VERSION,
    MCP_RESOURCES,
    MCP_TOOLS,
    handle_mcp_jsonrpc,
)


client = TestClient(
    app,
    headers={"X-API-Key": "test-admin-key-" + "a" * 32},
)


def test_mcp_initialize_handshake():
    resp = handle_mcp_jsonrpc({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}})
    assert resp is not None
    assert resp["jsonrpc"] == "2.0"
    assert resp["id"] == 1
    assert resp["result"]["protocolVersion"] == MCP_PROTOCOL_VERSION
    assert resp["result"]["serverInfo"]["name"] == "agentic-ops-mcp-gateway"
    assert "tools" in resp["result"]["capabilities"]
    assert "resources" in resp["result"]["capabilities"]
    assert "prompts" in resp["result"]["capabilities"]


def test_mcp_tools_list_exposes_10_governed_tools():
    resp = handle_mcp_jsonrpc({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
    tools = resp["result"]["tools"]
    assert len(tools) == 10
    names = {t["name"] for t in tools}
    assert names == {
        "read_console_diagnostic",
        "evaluate_governance_policy",
        "run_governed_incident_episode",
        "inspect_worm_trust_ledger",
        "get_ledger_status",
        "verify_ledger_inclusion",
        "search_failure_taxonomy",
        "get_scenario_blueprint",
        "poll_target_mlops_snapshot",
        "inspect_control_plane_vitals",
    }


def test_mcp_tool_read_console_diagnostic_with_and_without_guides():
    # 1. With pedagogical guides (default)
    resp_full = handle_mcp_jsonrpc(
        {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "read_console_diagnostic",
                "arguments": {"command": "sandbox_phase_b_slack_spoof", "include_guides": True},
            },
        }
    )
    assert resp_full["result"]["isError"] is False
    text_full = resp_full["result"]["content"][0]["text"]
    assert "HTTP/1.1 401 Unauthorized" in text_full
    assert "[GUIDE:ROLE]" in text_full

    # 2. Compact mode (include_guides=False)
    resp_compact = handle_mcp_jsonrpc(
        {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {
                "name": "read_console_diagnostic",
                "arguments": {"command": "sandbox_phase_b_slack_spoof", "include_guides": False},
            },
        }
    )
    text_compact = resp_compact["result"]["content"][0]["text"]
    assert "HTTP/1.1 401 Unauthorized" in text_compact
    assert "[GUIDE:ROLE]" not in text_compact


def _configure_inventory(monkeypatch, tmp_path):
    path = tmp_path / "inventory.yaml"
    path.write_text(
        f"""schema_version: 1
generated_at: {datetime.now(timezone.utc).isoformat()}
max_age_seconds: 3600
targets:
  mlops-incidents:
    replicas: 1
    criticality: low
  baac_rf:
    replicas: 1
    criticality: low
""",
        encoding="utf-8",
    )
    monkeypatch.setenv("AGENTIC_OPS_INVENTORY_PATH", str(path))


def test_mcp_tool_evaluate_governance_policy_deny_and_allow(monkeypatch, tmp_path):
    _configure_inventory(monkeypatch, tmp_path)
    # Forbidden action: propose_retrain on DATA-042 -> DENY (R-001 / R-002)
    deny_resp = handle_mcp_jsonrpc(
        {
            "jsonrpc": "2.0",
            "id": 5,
            "method": "tools/call",
            "params": {
                "name": "evaluate_governance_policy",
                "arguments": {
                    "risk_id": "DATA-042",
                    "action": "propose_retrain",
                    "target": "baac_rf",
                    "upstream_data_severity": "CRITICAL",
                },
            },
        }
    )
    deny_data = json.loads(deny_resp["result"]["content"][0]["text"])
    assert deny_data["verdict"]["effect"] == "DENY"
    assert len(deny_data["verdict"]["rule_ids"]) >= 1

    # Safe L1 action: create_issue on DATA-042 -> ALLOW
    allow_resp = handle_mcp_jsonrpc(
        {
            "jsonrpc": "2.0",
            "id": 6,
            "method": "tools/call",
            "params": {
                "name": "evaluate_governance_policy",
                "arguments": {
                    "risk_id": "DATA-042",
                    "action": "create_issue",
                    "target": "mlops-incidents",
                },
            },
        }
    )
    allow_data = json.loads(allow_resp["result"]["content"][0]["text"])
    assert allow_data["verdict"]["effect"] == "ALLOW"


def test_mcp_inventory_is_not_user_supplied_and_missing_config_fails_closed(
    monkeypatch,
):
    monkeypatch.delenv("AGENTIC_OPS_INVENTORY_PATH", raising=False)
    response = handle_mcp_jsonrpc(
        {
            "jsonrpc": "2.0",
            "id": 61,
            "method": "tools/call",
            "params": {
                "name": "evaluate_governance_policy",
                "arguments": {
                    "risk_id": "DATA-042",
                    "action": "create_issue",
                    "target": "mlops-incidents",
                    "target_replicas": 1,
                    "target_criticality": "low",
                },
            },
        }
    )
    data = json.loads(response["result"]["content"][0]["text"])

    assert data["verdict"]["effect"] == "DENY"
    assert data["verdict"]["rule_ids"] == ["INV-001"]
    assert "no authoritative local inventory is configured" in data["verdict"]["reasons"][0]


def test_mcp_tool_seal_and_verify_worm_trust_ledger(tmp_path, monkeypatch):
    _configure_inventory(monkeypatch, tmp_path)
    monkeypatch.setenv("EVIDENCE_STORE_DIR", str(tmp_path))
    seal_resp = handle_mcp_jsonrpc(
        {
            "jsonrpc": "2.0",
            "id": 7,
            "method": "tools/call",
            "params": {
                "name": "run_governed_incident_episode",
                "arguments": {
                    "risk_id": "DATA-042",
                    "action": "create_issue",
                    "target": "mlops-incidents",
                    "finding_summary": "MCP WORM test episode",
                },
            },
        }
    )
    sealed = json.loads(seal_resp["result"]["content"][0]["text"])
    assert sealed["status"] == "EPISODE_SEALED_IN_WORM_LEDGER"
    assert sealed["policy_decision"] == "ALLOW"
    assert len(sealed["sha256_hash"]) == 64
    assert len(sealed["hmac_sha512_signature"]) == 128

    verify_resp = handle_mcp_jsonrpc(
        {
            "jsonrpc": "2.0",
            "id": 8,
            "method": "tools/call",
            "params": {
                "name": "inspect_worm_trust_ledger",
                "arguments": {"episode_id": sealed["episode_id"]},
            },
        }
    )
    verified = json.loads(verify_resp["result"]["content"][0]["text"])
    assert verified["linear_chain_and_hmac_valid"] is True
    assert verified["merkle_chain_and_hmac_valid"] is True
    assert verified["total_matching_episodes"] == 1


def test_mcp_tool_search_failure_taxonomy():
    resp = handle_mcp_jsonrpc(
        {
            "jsonrpc": "2.0",
            "id": 9,
            "method": "tools/call",
            "params": {
                "name": "search_failure_taxonomy",
                "arguments": {"query": "drift", "max_results": 5},
            },
        }
    )
    data = json.loads(resp["result"]["content"][0]["text"])
    assert data["matches_returned"] > 0
    assert any("drift" in item.lower() for item in data["results"])


def test_mcp_tool_get_scenario_blueprint():
    resp = handle_mcp_jsonrpc(
        {
            "jsonrpc": "2.0",
            "id": 10,
            "method": "tools/call",
            "params": {
                "name": "get_scenario_blueprint",
                "arguments": {"scenario_id": "SC-101"},
            },
        }
    )
    data = json.loads(resp["result"]["content"][0]["text"])
    assert "sc_101_log_injection.yaml" in data["yaml_contracts"]


def test_mcp_tool_inspect_control_plane_vitals():
    resp = handle_mcp_jsonrpc(
        {
            "jsonrpc": "2.0",
            "id": 11,
            "method": "tools/call",
            "params": {"name": "inspect_control_plane_vitals", "arguments": {}},
        }
    )
    data = json.loads(resp["result"]["content"][0]["text"])
    assert data["service"] == "agentic-ops-control-plane"
    assert data["governed_actions_count"] >= 4


def test_mcp_resources_list_and_read():
    list_resp = handle_mcp_jsonrpc({"jsonrpc": "2.0", "id": 12, "method": "resources/list"})
    assert len(list_resp["result"]["resources"]) == 5

    read_resp = handle_mcp_jsonrpc(
        {
            "jsonrpc": "2.0",
            "id": 13,
            "method": "resources/read",
            "params": {"uri": "agentic-ops://governance/autonomy-policy"},
        }
    )
    contents = read_resp["result"]["contents"]
    assert len(contents) == 1
    policy_json = json.loads(contents[0]["text"])
    assert "policy" in policy_json
    assert "catalog" in policy_json


def test_mcp_prompts_list_exposes_all_20_starter_prompts():
    list_resp = handle_mcp_jsonrpc({"jsonrpc": "2.0", "id": 14, "method": "prompts/list"})
    prompts = list_resp["result"]["prompts"]
    assert len(prompts) == 20
    assert prompts[0]["name"] == "01_console_grand_slam_audit"
    assert prompts[-1]["name"] == "20_executive_jury_defense_briefing"


def test_mcp_prompts_get_returns_structured_template():
    get_resp = handle_mcp_jsonrpc(
        {
            "jsonrpc": "2.0",
            "id": 15,
            "method": "prompts/get",
            "params": {
                "name": "05_policy_veto_corrupted_sensor",
                "arguments": {"risk_id": "DATA-042"},
            },
        }
    )
    messages = get_resp["result"]["messages"]
    assert len(messages) == 1
    assert "evaluate_governance_policy" in messages[0]["content"]["text"]
    assert "DATA-042" in messages[0]["content"]["text"]


def test_fastapi_http_mcp_endpoints():
    manifest_res = client.get("/mcp/manifest")
    assert manifest_res.status_code == 200
    m = manifest_res.json()
    assert m["counts"]["tools"] == 10
    assert m["counts"]["resources"] == 5
    assert m["counts"]["starter_prompts"] == 20

    rpc_res = client.post(
        "/mcp",
        json={"jsonrpc": "2.0", "id": 99, "method": "prompts/list"},
    )
    assert rpc_res.status_code == 200
    assert len(rpc_res.json()["result"]["prompts"]) == 20


def test_mcp_tool_poll_target_mlops_snapshot(monkeypatch):
    from unittest.mock import MagicMock

    mock_collector = MagicMock()
    mock_snap = MagicMock()
    mock_snap.model_dump.return_value = {
        "status": "ONLINE",
        "endpoints": {"mlflow": 200, "prometheus": 200},
        "target": "jakatt/cac_mlops",
    }
    mock_collector.collect_all.return_value = mock_snap
    monkeypatch.setattr(
        "agentic_ops.entrypoints.mcp_server.CacPullCollector",
        lambda *args, **kwargs: mock_collector,
    )

    resp = handle_mcp_jsonrpc(
        {
            "jsonrpc": "2.0",
            "id": 16,
            "method": "tools/call",
            "params": {
                "name": "poll_target_mlops_snapshot",
                "arguments": {"use_proxy": False, "timeout": 1.0},
            },
        }
    )
    assert resp["result"]["isError"] is False
    data = json.loads(resp["result"]["content"][0]["text"])
    assert data["target"] == "jakatt/cac_mlops"


def test_mcp_tools_declare_all_four_hints():
    resp = handle_mcp_jsonrpc({"jsonrpc": "2.0", "id": 17, "method": "tools/list"})
    tools = resp["result"]["tools"]
    assert len(tools) == 10
    for tool in tools:
        assert isinstance(tool.get("readOnlyHint"), bool), f"Missing readOnlyHint in {tool['name']}"
        assert isinstance(tool.get("destructiveHint"), bool), f"Missing destructiveHint in {tool['name']}"
        assert isinstance(tool.get("idempotentHint"), bool), f"Missing idempotentHint in {tool['name']}"
        assert isinstance(tool.get("openWorldHint"), bool), f"Missing openWorldHint in {tool['name']}"


def test_tool_get_mlflow_model_info():
    from agentic_ops.tools.model import GetMLflowModelInfo

    tool = GetMLflowModelInfo()
    assert tool.name == "get_mlflow_model_info"
    assert tool.readOnlyHint is True
    assert tool.destructiveHint is False
    assert tool.idempotentHint is True
    assert tool.openWorldHint is True
    res = tool.run(model_name="baac_rf", stage="Production")
    assert "baac_rf" in res


def test_tool_get_prometheus_metric():
    from agentic_ops.tools.observability import GetPrometheusMetric

    tool = GetPrometheusMetric()
    assert tool.name == "get_prometheus_metric"
    assert tool.readOnlyHint is True
    assert tool.destructiveHint is False
    assert tool.idempotentHint is True
    assert tool.openWorldHint is True
    res = tool.run(metric_name="http_requests_total", query_window="5m")
    assert "42.0" in res


def test_tool_get_evidently_report():
    from agentic_ops.tools.observability import GetEvidentlyReport

    tool = GetEvidentlyReport()
    assert tool.name == "get_evidently_report"
    assert tool.readOnlyHint is True
    assert tool.destructiveHint is False
    assert tool.idempotentHint is True
    assert tool.openWorldHint is True
    res = tool.run(model_version="v2.1")
    assert "v2.1" in res


def test_tool_check_database_health():
    from agentic_ops.tools.infra import CheckDatabaseHealth

    tool = CheckDatabaseHealth()
    assert tool.name == "check_database_health"
    assert tool.readOnlyHint is True
    assert tool.destructiveHint is False
    assert tool.idempotentHint is True
    assert tool.openWorldHint is True
    res = tool.run(db_name="postgres_production")
    assert "postgres_production" in res


def test_tool_check_docker_container():
    from agentic_ops.tools.infra import CheckDockerContainer

    tool = CheckDockerContainer()
    assert tool.name == "check_docker_container"
    assert tool.readOnlyHint is True
    assert tool.destructiveHint is False
    assert tool.idempotentHint is True
    assert tool.openWorldHint is False
    res = tool.run(container_name="model-api")
    assert "model-api" in res


def test_tool_check_dvc_status():
    from agentic_ops.tools.data import CheckDvcStatus

    tool = CheckDvcStatus()
    assert tool.name == "check_dvc_status"
    assert tool.readOnlyHint is True
    assert tool.destructiveHint is False
    assert tool.idempotentHint is True
    assert tool.openWorldHint is False
    res = tool.run(dataset_path="data/raw/accidents.csv")
    assert "abcd123" in res


def test_tool_validate_pandera_schema():
    from agentic_ops.tools.data import ValidatePanderaSchema

    tool = ValidatePanderaSchema()
    assert tool.name == "validate_pandera_schema"
    assert tool.readOnlyHint is True
    assert tool.destructiveHint is False
    assert tool.idempotentHint is True
    assert tool.openWorldHint is False
    res = tool.run(table_name="fact_accidents")
    assert "fact_accidents" in res


def test_tool_execute_sql():
    from agentic_ops.tools.data import ExecuteSql

    tool = ExecuteSql()
    assert tool.name == "execute_sql"
    assert tool.readOnlyHint is False
    assert tool.destructiveHint is True
    assert tool.idempotentHint is False
    assert tool.openWorldHint is True
    res = tool.run(query="SELECT 1;", database="analytics", approved_by_admin=True)
    assert "analytics" in res


def test_tool_create_github_issue():
    from agentic_ops.tools.github import CreateIssue

    tool = CreateIssue()
    assert tool.name == "create_github_issue"
    assert tool.readOnlyHint is False
    assert tool.destructiveHint is False
    assert tool.idempotentHint is False
    assert tool.openWorldHint is True
    res = tool.run(
        title="Drift detected",
        body="Drift on feature speed_limit > 0.05",
        risk_id="DATA-042",
        approved_by_admin=True,
    )
    assert "DATA-042" in res


def test_all_19_tools_audit_and_coverage():
    all_19_tools = [
        # 10 Governed MCP Gateway Tools
        "read_console_diagnostic",
        "evaluate_governance_policy",
        "run_governed_incident_episode",
        "inspect_worm_trust_ledger",
        "get_ledger_status",
        "verify_ledger_inclusion",
        "search_failure_taxonomy",
        "get_scenario_blueprint",
        "poll_target_mlops_snapshot",
        "inspect_control_plane_vitals",
        # 9 Modular Operational Tools
        "get_mlflow_model_info",
        "get_prometheus_metric",
        "get_evidently_report",
        "check_database_health",
        "check_docker_container",
        "check_dvc_status",
        "validate_pandera_schema",
        "execute_sql",
        "create_github_issue",
    ]
    assert len(all_19_tools) == 19
    assert len(set(all_19_tools)) == 19


def test_mcp_tool_get_ledger_status():
    resp = handle_mcp_jsonrpc(
        {
            "jsonrpc": "2.0",
            "id": 88,
            "method": "tools/call",
            "params": {
                "name": "get_ledger_status",
                "arguments": {},
            },
        }
    )
    assert resp["result"]["isError"] is False
    data = json.loads(resp["result"]["content"][0]["text"])
    assert "worm_ledger_file" in data
    assert "total_episodes" in data
    assert "linear_chain_valid" in data
    assert "hmac_signatures_valid" in data
    assert "merkle_root" in data
    assert len(data["merkle_root"]) == 64
    assert data["status"] in ("HEALTHY", "CORRUPTED_OR_TAMPERED")


def test_mcp_tool_verify_ledger_inclusion_workflow():
    # 1. Seal an episode first
    seal_resp = handle_mcp_jsonrpc(
        {
            "jsonrpc": "2.0",
            "id": 89,
            "method": "tools/call",
            "params": {
                "name": "run_governed_incident_episode",
                "arguments": {
                    "scenario_id": "SC-101",
                    "action_name": "scale_to_zero",
                    "target_service": "accident_prediction_api",
                },
            },
        }
    )
    sealed = json.loads(seal_resp["result"]["content"][0]["text"])
    ep_id = sealed["episode_id"]

    # 2. Verify inclusion by episode_id
    verify_resp = handle_mcp_jsonrpc(
        {
            "jsonrpc": "2.0",
            "id": 90,
            "method": "tools/call",
            "params": {
                "name": "verify_ledger_inclusion",
                "arguments": {"episode_id": ep_id},
            },
        }
    )
    assert verify_resp["result"]["isError"] is False
    vdata = json.loads(verify_resp["result"]["content"][0]["text"])
    assert vdata["verified"] is True
    assert vdata["status"] == "VALID_INCLUSION_PROOF"
    assert vdata["episode_id"] == ep_id
    assert len(vdata["leaf_hash"]) == 64
    assert len(vdata["merkle_root"]) == 64
    assert "complexity" in vdata

    # 3. Verify offline with complete proof packet
    from agentic_ops.core.evidence import EvidenceStore
    import os
    from pathlib import Path
    store = EvidenceStore(os.environ.get("EVIDENCE_STORE_DIR", str(Path(__file__).resolve().parent.parent.parent / "state" / "episodes")))
    packet = store.get_merkle_proof(ep_id)
    assert packet is not None

    offline_resp = handle_mcp_jsonrpc(
        {
            "jsonrpc": "2.0",
            "id": 91,
            "method": "tools/call",
            "params": {
                "name": "verify_ledger_inclusion",
                "arguments": {
                    "proof_packet": packet,
                    "expected_root": packet["merkle_root"],
                },
            },
        }
    )
    assert offline_resp["result"]["isError"] is False
    odata = json.loads(offline_resp["result"]["content"][0]["text"])
    assert odata["verified"] is True
    assert odata["status"] == "VALID_INCLUSION_PROOF"

    # 4. Assert root mismatch detection
    fake_root = "b" * 64
    mismatch_resp = handle_mcp_jsonrpc(
        {
            "jsonrpc": "2.0",
            "id": 92,
            "method": "tools/call",
            "params": {
                "name": "verify_ledger_inclusion",
                "arguments": {
                    "proof_packet": packet,
                    "expected_root": fake_root,
                },
            },
        }
    )
    assert mismatch_resp["result"]["isError"] is False
    mdata = json.loads(mismatch_resp["result"]["content"][0]["text"])
    assert mdata["verified"] is False
    assert mdata["status"] == "ROOT_MISMATCH"

    # 5. Assert tampering rejection
    tampered_packet = dict(packet)
    tampered_packet["leaf_hash"] = "0" * 64
    tampered_resp = handle_mcp_jsonrpc(
        {
            "jsonrpc": "2.0",
            "id": 93,
            "method": "tools/call",
            "params": {
                "name": "verify_ledger_inclusion",
                "arguments": {"proof_packet": tampered_packet},
            },
        }
    )
    assert tampered_resp["result"]["isError"] is False
    tdata = json.loads(tampered_resp["result"]["content"][0]["text"])
    assert tdata["verified"] is False
    assert tdata["status"] == "TAMPERING_OR_INVALID_PROOF"

    # 6. Missing parameters rejection
    missing_resp = handle_mcp_jsonrpc(
        {
            "jsonrpc": "2.0",
            "id": 94,
            "method": "tools/call",
            "params": {
                "name": "verify_ledger_inclusion",
                "arguments": {},
            },
        }
    )
    assert missing_resp["result"]["isError"] is True

    # 7. Mutually exclusive parameters rejection (both episode_id and proof_packet)
    both_resp = handle_mcp_jsonrpc(
        {
            "jsonrpc": "2.0",
            "id": 95,
            "method": "tools/call",
            "params": {
                "name": "verify_ledger_inclusion",
                "arguments": {
                    "episode_id": ep_id,
                    "proof_packet": packet,
                },
            },
        }
    )
    assert both_resp["result"]["isError"] is True
    bdata = json.loads(both_resp["result"]["content"][0]["text"])
    assert bdata["status"] == "MUTUALLY_EXCLUSIVE_PARAMS"


