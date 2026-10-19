from __future__ import annotations

import argparse
import logging
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace
from typing import Any

from agentic_ops.core.alert_outbox import AlertOutbox
from agentic_ops.core.approvals import ApprovalRepo
from agentic_ops.core.alert_processing import (
    AlertIncidentProcessor,
    AlertClassificationStore,
    AlertClassifier,
    AlertTriageWorker,
)
from agentic_ops.core.contracts import Diagnosis, Finding, Signal
from agentic_ops.core.evidence import EvidenceStore
from agentic_ops.core.local_inventory import inventory_from_environment
from agentic_ops.core.policy import PolicyEngine
from agentic_ops.core.atomic_quota import AtomicQuotaManager
from agentic_ops.core.orchestrator import Orchestrator

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MAPPING_PATH = REPOSITORY_ROOT / "agentic_ops" / "governance" / "alert_classification.yaml"
DEFAULT_POLICY_PATH = REPOSITORY_ROOT / "agentic_ops" / "governance" / "autonomy_policy.yaml"


class _AlertObservability:
    def __init__(self, database_path: str):
        self.database_path = database_path
        self.signal: Signal | None = None
        self.event: Any = None

    def set_alert(self, alert: dict[str, Any], tracking_id: str, risk_id: str) -> None:
        labels = alert.get("labels", {})
        annotations = alert.get("annotations", {})
        if not isinstance(labels, dict):
            labels = {}
        if not isinstance(annotations, dict):
            annotations = {}
        observed_at = datetime.now(timezone.utc)
        starts_at = alert.get("startsAt")
        if isinstance(starts_at, str):
            try:
                observed_at = datetime.fromisoformat(starts_at.replace("Z", "+00:00"))
                if observed_at.tzinfo is None:
                    observed_at = observed_at.replace(tzinfo=timezone.utc)
            except ValueError:
                pass
        severity = str(labels.get("severity", "WARNING")).upper()
        if severity not in {"INFO", "WARNING", "CRITICAL"}:
            severity = "WARNING"
        layer = (
            "infrastructure"
            if risk_id.startswith("INFRA-")
            else "model"
            if risk_id.startswith(("ML-", "MODEL-"))
            else "data_pipeline"
        )
        service = str(labels.get("service") or labels.get("job") or labels.get("alertname") or "unknown")
        target = str(labels.get("service") or labels.get("job") or "").strip()
        self.signal = Signal(
            signal_id=tracking_id,
            source="grafana",
            observed_at=observed_at,
            metadata={
                "tenant": str(labels.get("tenant", "default")),
                "service": service,
                "alertname": str(labels.get("alertname", "")),
                "severity": severity,
                "labels": labels,
                "annotations": annotations,
                "value": labels.get("value", annotations.get("value", "N/A")),
                "threshold": annotations.get("threshold", "N/A"),
                "target": target,
            },
        )
        self.event = SimpleNamespace(
            layer=layer,
            severity=severity,
            timestamp=observed_at,
        )

    def get_signal(self, signal_id: str) -> Signal:
        if self.signal is None or self.signal.signal_id != signal_id:
            raise LookupError(f"no alert signal loaded for {signal_id}")
        return self.signal

    def get_events(self) -> list[Any]:
        return [self.event] if self.event is not None else []


class _DeterministicDiagnosis:
    """Produce bounded input for the orchestrator without external LLM calls."""

    def complete(self, *, system: str, user: str, response_model: type, temperature: float = 0.0):
        if response_model is not Diagnosis:
            raise TypeError(f"unsupported response model: {response_model.__name__}")
        return Diagnosis(
            layer="alert",
            findings=[Finding(description="Alerte Grafana classifiée; investigation déterministe.")],
            confidence_score=1.0,
        )


def _build_incident_processor(database_path: str, inventory) -> AlertIncidentProcessor:
    evidence_path = os.environ.get("EVIDENCE_STORE_DIR", "state/episodes")
    policy_path = Path(os.environ.get("AUTONOMY_POLICY_PATH", str(DEFAULT_POLICY_PATH)))
    policy_engine = PolicyEngine.from_yaml(
        policy_path,
        quota_manager=AtomicQuotaManager(
            os.environ.get("POLICY_QUOTA_DB_PATH", "state/policy_quotas.sqlite3")
        ),
    )
    evidence_store = EvidenceStore(evidence_path)
    approval_database_path = os.environ.get("APPROVAL_DB_PATH", "state/approvals.db")
    if approval_database_path == ":memory:":
        raise ValueError("APPROVAL_DB_PATH must be persistent for the alert worker")
    approval_repo = ApprovalRepo(approval_database_path, time.time)
    observability = _AlertObservability(database_path)
    orchestrator = Orchestrator(
        observability=observability,
        policy_engine=policy_engine,
        evidence_store=evidence_store,
        environment=os.environ.get("ENVIRONMENT", "development"),
        llm=_DeterministicDiagnosis(),
        inventory=inventory,
        approval_repo=approval_repo,
        approval_requester_id=os.environ.get(
            "APPROVAL_REQUESTER_ID", "agentic-ops-alert-worker"
        ),
    )

    def process_alert(record, risk_id):
        existing = evidence_store.find_episode_by_signal_id(record.tracking_id)
        if existing is not None:
            orchestrator.ensure_approval_request(existing)
            return str(existing["episode_id"])
        if not risk_id:
            raise ValueError("classified alert has no risk_id")
        observability.set_alert(record.payload, record.tracking_id, risk_id)
        return AlertIncidentProcessor(orchestrator)(record, risk_id)

    return process_alert


def build_worker() -> AlertTriageWorker:
    database_path = os.environ.get("ALERT_OUTBOX_DB_PATH", "state/alerts.db")
    mapping_path = os.environ.get("ALERT_CLASSIFICATION_MAP", str(DEFAULT_MAPPING_PATH))
    if database_path == ":memory:":
        raise ValueError("ALERT_OUTBOX_DB_PATH must be persistent for a standalone worker")
    inventory = inventory_from_environment()
    return AlertTriageWorker(
        outbox=AlertOutbox(database_path),
        classifier=AlertClassifier(mapping_path),
        result_store=AlertClassificationStore(database_path),
        worker_id=os.environ.get("ALERT_WORKER_ID", f"alert-triage-{os.getpid()}"),
        incident_handler=_build_incident_processor(database_path, inventory),
    )


def run_alert_worker(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Process persisted Grafana alerts in triage-only mode.")
    parser.add_argument("--once", action="store_true", help="process at most one queued alert and exit")
    parser.add_argument(
        "--poll-interval-seconds",
        type=float,
        default=1.0,
        help="delay between empty queue polls (default: 1 second)",
    )
    args = parser.parse_args(argv)
    if args.poll_interval_seconds <= 0:
        parser.error("--poll-interval-seconds must be positive")

    logging.basicConfig(level=os.environ.get("LOG_LEVEL", "INFO"))
    worker = build_worker()
    if args.once:
        worker.run_once()
        return 0

    logging.getLogger(__name__).info(
        "alert investigation worker started (simulation/observation only)"
    )
    try:
        while True:
            if not worker.run_once():
                time.sleep(args.poll_interval_seconds)
    except KeyboardInterrupt:
        logging.getLogger(__name__).info("alert triage worker stopped")
        return 0


if __name__ == "__main__":
    raise SystemExit(run_alert_worker())
