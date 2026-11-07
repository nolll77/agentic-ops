"""
EU AI Act Article 12 (record-keeping) / Article 14 (human oversight) audit pack.

Builds a deterministic, read-only JSON evidence bundle from the WORM Trust Ledger,
the compiled PolicyBundle and the durable approval store.

Honest scope (do not oversell):
  * The bundle is signed with HMAC-SHA512 using the ledger secret. HMAC is symmetric:
    only holders of the key can verify it. It is an INTERNAL integrity seal, NOT a
    third-party-verifiable attestation (that would require an asymmetric signature).
  * If no ledger key is configured the process falls back to a publicly known dummy
    key (dev only). The bundle then says so explicitly (`signing_key_provenance`).
  * Reading the pack never creates directories, databases or ledger files.
"""

from __future__ import annotations

import os
import sqlite3
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from agentic_ops.core.crypto import get_canonical_json, sign_payload
from agentic_ops.core.evidence import EvidenceStore

PACK_SCHEMA = "agentic-ops/eu-ai-act-art12-audit-pack/v1"
PACK_URI = "mlops://compliance/eu-ai-act/article-12/audit-pack"


def _signing_key_provenance() -> str:
    if os.environ.get("LEDGER_SECRET_KEY") or os.environ.get("EVIDENCE_STORE_HMAC_KEY"):
        return "CONFIGURED"
    return "INSECURE_DEFAULT_DUMMY_KEY"


def _ledger_section(store_dir: Path) -> Dict[str, Any]:
    ledger_file = store_dir / "ledger.jsonl"
    if not ledger_file.exists():
        # Read-only: do not instantiate EvidenceStore (its constructor creates files).
        return {
            "available": False,
            "episodes": 0,
            "chain_valid": None,
            "merkle_root": None,
            "decision_counts": {},
            "state_counts": {},
            "note": "No ledger present: nothing has been recorded yet.",
        }
    store = EvidenceStore(str(store_dir))
    episodes = store.load_all_episodes()
    decisions: Counter[str] = Counter()
    states: Counter[str] = Counter()
    for ep in episodes:
        evaluation = ep.get("policy_evaluation") or {}
        decisions[str(evaluation.get("decision", "UNKNOWN"))] += 1
        trace = ep.get("state_trace") or ep.get("state_machine_trace") or []
        if trace:
            states[str(trace[-1])] += 1
    return {
        "available": True,
        "episodes": len(episodes),
        "chain_valid": bool(store.verify_chain()),
        "merkle_root": store.get_merkle_root() if episodes else None,
        "decision_counts": dict(sorted(decisions.items())),
        "state_counts": dict(sorted(states.items())),
    }


def _policy_section(bundle: Any) -> Dict[str, Any]:
    if bundle is None:
        return {"available": False}
    return {
        "available": True,
        "version": bundle.version,
        "default_effect": bundle.policy.default_effect,
        "levels": sorted(bundle.policy.levels.keys()),
        "actions": sorted(bundle.policy.actions.keys()),
        "rules": [
            {
                "id": r.id,
                "kind": r.kind,
                "applies_to_classes": list(r.applies_to_classes),
                "min_severity": r.min_severity,
                "description": r.description,
            }
            for r in bundle.policy.rules
        ],
    }


def _oversight_section(approval_db_path: Optional[str]) -> Dict[str, Any]:
    if not approval_db_path or approval_db_path == ":memory:" or not Path(approval_db_path).exists():
        return {
            "available": False,
            "note": "No durable approval store present: no human-oversight activity recorded.",
        }
    try:
        # Imported lazily; ApprovalRepo.stats() is a plain read-only SELECT.
        from agentic_ops.core.approvals import ApprovalRepo

        repo = ApprovalRepo(approval_db_path, lambda: datetime.now(timezone.utc).timestamp())
        return {"available": True, **repo.stats()}
    except (sqlite3.Error, OSError) as exc:  # pragma: no cover - defensive
        return {"available": False, "error": f"{type(exc).__name__}: {exc}"}


def build_audit_pack(
    store_dir: str | Path,
    bundle: Any = None,
    approval_db_path: Optional[str] = None,
    *,
    now: Optional[datetime] = None,
) -> Dict[str, Any]:
    """Return the signed Article 12 audit pack as a plain dict."""
    generated_at = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    body: Dict[str, Any] = {
        "schema": PACK_SCHEMA,
        "resource_uri": PACK_URI,
        "generated_at_utc": generated_at.isoformat(),
        "regulatory_scope": {
            "regulation": "Regulation (EU) 2024/1689",
            "articles": ["12 (record-keeping)", "14 (human oversight)"],
            "disclaimer": (
                "Technical evidence bundle. It does not by itself constitute legal "
                "compliance or a conformity assessment."
            ),
        },
        "ledger": _ledger_section(Path(store_dir)),
        "policy": _policy_section(bundle),
        "human_oversight": _oversight_section(approval_db_path),
    }
    canonical = get_canonical_json(body)
    body["signature"] = {
        "algorithm": "HMAC-SHA512",
        "scope": "canonical JSON of every field except `signature`",
        "signing_key_provenance": _signing_key_provenance(),
        "third_party_verifiable": False,
        "value": sign_payload(canonical),
    }
    return body


def verify_audit_pack(pack: Dict[str, Any]) -> bool:
    """Recompute the seal. Requires the ledger secret (symmetric HMAC)."""
    import hmac

    candidate = dict(pack)
    signature = candidate.pop("signature", None)
    if not isinstance(signature, dict) or "value" not in signature:
        return False
    expected = sign_payload(get_canonical_json(candidate))
    return hmac.compare_digest(expected, str(signature["value"]))
