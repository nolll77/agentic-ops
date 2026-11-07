"""Tests for the EU AI Act Article 12 audit pack (read-only, HMAC-sealed)."""

from __future__ import annotations

import json
import os
import sqlite3
from datetime import datetime, timezone

import pytest

from agentic_ops.core.approvals import ApprovalRepo, FrozenProposal
from agentic_ops.core.compliance_pack import (
    PACK_SCHEMA,
    PACK_URI,
    build_audit_pack,
    verify_audit_pack,
)
from agentic_ops.core.evidence import EvidenceStore
from agentic_ops.entrypoints.mcp_server import (
    COMPLIANCE_PACK_URI,
    MCP_RESOURCES,
    handle_mcp_jsonrpc,
)

FIXED_NOW = datetime(2026, 11, 7, 12, 0, 0, tzinfo=timezone.utc)


def _episode(episode_id: str, decision: str, final_state: str) -> dict:
    return {
        "episode_id": episode_id,
        "risk_id": "DATA-001",
        "state_trace": ["DETECTED", "PLANNED", final_state],
        "policy_evaluation": {"decision": decision, "matched_rule": "R-TEST"},
    }


@pytest.fixture
def populated_store(tmp_path):
    store = EvidenceStore(str(tmp_path / "episodes"))
    store.save(_episode("EP-0001", "ALLOW", "RESOLVED"))
    store.save(_episode("EP-0002", "DENY", "DENIED"))
    store.save(_episode("EP-0003", "DENY", "DENIED"))
    return store


def test_pack_reports_ledger_state_and_is_signed(populated_store):
    pack = build_audit_pack(populated_store.store_dir, approval_db_path=None, now=FIXED_NOW)
    assert pack["schema"] == PACK_SCHEMA
    assert pack["resource_uri"] == PACK_URI == COMPLIANCE_PACK_URI
    ledger = pack["ledger"]
    assert ledger["available"] is True
    assert ledger["episodes"] == 3
    assert ledger["chain_valid"] is True
    assert ledger["merkle_root"] == populated_store.get_merkle_root()
    assert ledger["decision_counts"] == {"ALLOW": 1, "DENY": 2}
    assert ledger["state_counts"] == {"DENIED": 2, "RESOLVED": 1}
    assert pack["signature"]["algorithm"] == "HMAC-SHA512"
    assert pack["signature"]["third_party_verifiable"] is False
    assert verify_audit_pack(pack) is True


def test_pack_is_deterministic_for_same_inputs(populated_store):
    a = build_audit_pack(populated_store.store_dir, now=FIXED_NOW)
    b = build_audit_pack(populated_store.store_dir, now=FIXED_NOW)
    assert a == b


def test_tampering_with_pack_body_breaks_the_seal(populated_store):
    pack = build_audit_pack(populated_store.store_dir, now=FIXED_NOW)
    pack["ledger"]["episodes"] = 999
    assert verify_audit_pack(pack) is False


def test_missing_or_malformed_signature_is_rejected(populated_store):
    pack = build_audit_pack(populated_store.store_dir, now=FIXED_NOW)
    del pack["signature"]
    assert verify_audit_pack(pack) is False
    assert verify_audit_pack({"signature": "not-a-dict"}) is False


def test_single_bit_ledger_tamper_is_reported_as_chain_invalid(populated_store):
    ledger = populated_store.ledger_file
    lines = ledger.read_text().splitlines()
    record = json.loads(lines[1])
    record["risk_id"] = "DATA-002"  # one field altered after sealing
    lines[1] = json.dumps(record)
    ledger.write_text("\n".join(lines) + "\n")
    pack = build_audit_pack(populated_store.store_dir, now=FIXED_NOW)
    assert pack["ledger"]["chain_valid"] is False
    # The pack itself is still validly sealed: it honestly REPORTS the broken chain.
    assert verify_audit_pack(pack) is True


def test_reading_pack_never_creates_ledger_or_directories(tmp_path):
    missing = tmp_path / "does-not-exist"
    pack = build_audit_pack(missing, approval_db_path=str(tmp_path / "nope.db"), now=FIXED_NOW)
    assert not missing.exists()
    assert not (tmp_path / "nope.db").exists()
    assert pack["ledger"] == {
        "available": False,
        "episodes": 0,
        "chain_valid": None,
        "merkle_root": None,
        "decision_counts": {},
        "state_counts": {},
        "note": "No ledger present: nothing has been recorded yet.",
    }
    assert pack["human_oversight"]["available"] is False
    assert verify_audit_pack(pack) is True


def test_pack_flags_insecure_default_key(monkeypatch, populated_store):
    monkeypatch.delenv("LEDGER_SECRET_KEY", raising=False)
    monkeypatch.delenv("EVIDENCE_STORE_HMAC_KEY", raising=False)
    pack = build_audit_pack(populated_store.store_dir, now=FIXED_NOW)
    assert pack["signature"]["signing_key_provenance"] == "INSECURE_DEFAULT_DUMMY_KEY"
    monkeypatch.setenv("LEDGER_SECRET_KEY", "x" * 32)
    pack = build_audit_pack(populated_store.store_dir, now=FIXED_NOW)
    assert pack["signature"]["signing_key_provenance"] == "CONFIGURED"


def test_pack_includes_policy_and_oversight_statistics(populated_store, tmp_path):
    from pathlib import Path

    from agentic_ops.core.policy_engine import PolicyBundle

    gov = Path(__file__).resolve().parents[2] / "agentic_ops" / "governance"
    bundle = PolicyBundle.load(
        gov / "autonomy_policy.yaml", gov / "action_catalog.yaml", gov / "risk_register.yaml"
    )
    db = tmp_path / "approvals.db"
    repo = ApprovalRepo(str(db), lambda: 1_000.0)
    proposal = FrozenProposal(
        episode_id="EP-0002",
        action="restart_pod",
        target="fastapi-model-demo",
        risk_id="INFRA-001",
        policy_version="v-test",
        requester_id="requester",
        required=1,
        required_groups=("SRE_LEAD",),
    )
    repo.open_request(proposal, ttl_s=3600)

    pack = build_audit_pack(populated_store.store_dir, bundle, str(db), now=FIXED_NOW)

    assert pack["policy"]["available"] is True
    assert pack["policy"]["version"] == bundle.version
    assert pack["policy"]["default_effect"] == "deny"
    assert {r["id"] for r in pack["policy"]["rules"]} == {r.id for r in bundle.policy.rules}
    oversight = pack["human_oversight"]
    assert oversight["available"] is True
    assert oversight["requests_total"] == 1
    assert oversight["requests_by_status"] == {"PENDING": 1}
    assert oversight["approvals_total"] == 0
    assert verify_audit_pack(pack) is True


def test_approval_stats_is_read_only(tmp_path):
    db = tmp_path / "approvals.db"
    repo = ApprovalRepo(str(db), lambda: 1_000.0)
    before = db.read_bytes()
    stats = repo.stats()
    assert stats["requests_total"] == 0
    assert stats["approvals_total"] == 0
    assert stats["distinct_approvers"] == 0
    # no write transaction: the main DB file content is untouched by stats()
    assert sqlite3.connect(str(db)).execute("PRAGMA integrity_check").fetchone()[0] == "ok"
    assert db.read_bytes() == before


def test_mcp_resource_is_listed_and_readable(monkeypatch, tmp_path):
    monkeypatch.setenv("EVIDENCE_STORE_DIR", str(tmp_path / "episodes"))
    monkeypatch.setenv("APPROVAL_DB_PATH", str(tmp_path / "approvals.db"))
    assert any(r["uri"] == COMPLIANCE_PACK_URI for r in MCP_RESOURCES)

    resp = handle_mcp_jsonrpc(
        {"jsonrpc": "2.0", "id": 1, "method": "resources/read", "params": {"uri": COMPLIANCE_PACK_URI}}
    )
    assert "error" not in resp
    content = resp["result"]["contents"][0]
    assert content["uri"] == COMPLIANCE_PACK_URI
    pack = json.loads(content["text"])
    assert pack["schema"] == PACK_SCHEMA
    assert pack["policy"]["available"] is True
    assert verify_audit_pack(pack) is True
    assert not (tmp_path / "episodes").exists()
