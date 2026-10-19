import json
import sqlite3

import pytest

from agentic_ops.core.alert_outbox import AlertIngestionWorker, AlertOutbox, LostLeaseError
from agentic_ops.core.alert_processing import (
    AlertClassificationStore,
    AlertClassifier,
    AlertMappingError,
    AlertTriageWorker,
)
from agentic_ops.core.atomic_quota import AtomicQuotaManager


def test_outbox_deduplicates_and_recovers_expired_lease(tmp_path):
    now = [1000.0]
    outbox = AlertOutbox(str(tmp_path / "outbox.db"), clock=lambda: now[0])
    alert = {"status": "firing", "labels": {"alertname": "DiskFull"}, "startsAt": "t0"}

    records, duplicates = outbox.enqueue([alert, alert])
    assert duplicates == 1
    assert records[0].tracking_id == records[1].tracking_id

    first = outbox.claim("worker-a", lease_seconds=5)
    assert first is not None
    assert first.attempts == 1
    assert outbox.claim("worker-b", lease_seconds=5) is None

    now[0] += 6
    recovered = outbox.claim("worker-b", lease_seconds=5)
    assert recovered is not None
    assert recovered.tracking_id == first.tracking_id
    assert recovered.attempts == 2
    with pytest.raises(LostLeaseError):
        outbox.complete(first.tracking_id, "worker-a")

    outbox.complete(recovered.tracking_id, "worker-b")
    assert outbox.get(recovered.tracking_id).status == "COMPLETED"
    now[0] += 301
    later, duplicates = outbox.enqueue([alert])
    assert duplicates == 0
    assert later[0].tracking_id != recovered.tracking_id


def test_worker_retries_then_marks_terminal_failure(tmp_path):
    now = [100.0]
    outbox = AlertOutbox(str(tmp_path / "outbox.db"), clock=lambda: now[0])
    record, _ = outbox.enqueue([{"status": "firing", "labels": {"alertname": "x"}}])
    worker = AlertIngestionWorker(
        outbox,
        "worker",
        lambda alert: (_ for _ in ()).throw(RuntimeError("temporary")),
        max_attempts=1,
    )

    assert worker.run_once()
    saved = outbox.get(record[0].tracking_id)
    assert saved.status == "DEAD"
    assert saved.attempts == 1
    assert saved.last_error == "RuntimeError"
    assert not worker.run_once()


def test_alert_triage_worker_persists_classification_and_unknown_review(tmp_path):
    mapping_path = tmp_path / "mapping.yaml"
    mapping_path.write_text(
        "schema_version: 1\nmappings:\n  KnownAlert:\n    risk_id: DATA-042\n",
        encoding="utf-8",
    )
    database = str(tmp_path / "alerts.db")
    outbox = AlertOutbox(database)
    results = AlertClassificationStore(database)
    classifier = AlertClassifier(mapping_path)
    worker = AlertTriageWorker(outbox, classifier, results, "triage-worker")
    records, _ = outbox.enqueue(
        [
            {"status": "firing", "labels": {"alertname": "KnownAlert"}},
            {"status": "firing", "labels": {"alertname": "UnmappedAlert"}},
            {"status": "firing", "labels": {"severity": "warning"}},
        ]
    )

    assert worker.run_once()
    assert worker.run_once()
    assert worker.run_once()
    assert not worker.run_once()
    assert [outbox.get(record.tracking_id).status for record in records] == [
        "COMPLETED",
        "COMPLETED",
        "COMPLETED",
    ]
    assert results.get(records[0].tracking_id).triage_status == "CLASSIFIED"
    assert results.get(records[0].tracking_id).risk_id == "DATA-042"
    assert results.get(records[1].tracking_id).triage_status == "REVIEW_REQUIRED"
    assert results.get(records[1].tracking_id).risk_id is None
    assert results.get(records[2].tracking_id).triage_status == "REVIEW_REQUIRED"


def test_alert_triage_result_is_idempotent_across_retries(tmp_path):
    database = str(tmp_path / "alerts.db")
    store = AlertClassificationStore(database)
    first = store.record("tracking-1", "CLASSIFIED", "Alert", "DATA-042", "version-1", 1.0)
    replay = store.record("tracking-1", "REVIEW_REQUIRED", "Alert", None, "version-2", 2.0)

    assert replay == first


def test_alert_triage_recovers_after_result_persisted_before_ack(tmp_path):
    now = [100.0]
    database = str(tmp_path / "alerts.db")
    outbox = AlertOutbox(database, clock=lambda: now[0])
    results = AlertClassificationStore(database)
    mapping_path = tmp_path / "mapping.yaml"
    mapping_path.write_text(
        "schema_version: 1\nmappings:\n  KnownAlert:\n    risk_id: DATA-042\n",
        encoding="utf-8",
    )
    record, _ = outbox.enqueue(
        [{"status": "firing", "labels": {"alertname": "KnownAlert"}}]
    )
    worker = AlertTriageWorker(
        outbox,
        AlertClassifier(mapping_path),
        results,
        "triage-worker",
    )
    handler = worker.worker.handler
    fail_once = [True]

    def persist_then_crash(alert):
        handler(alert)
        if fail_once[0]:
            fail_once[0] = False
            raise RuntimeError("simulated crash after durable result")

    worker.worker.handler = persist_then_crash
    assert worker.run_once()
    assert outbox.get(record[0].tracking_id).status == "RETRY"
    now[0] += 2
    assert worker.run_once()
    assert outbox.get(record[0].tracking_id).status == "COMPLETED"
    result = results.get(record[0].tracking_id)
    assert result is not None
    assert result.risk_id == "DATA-042"


def test_deployed_worker_creates_orchestrated_investigation_episode(tmp_path, monkeypatch):
    from agentic_ops.entrypoints.alert_worker import build_worker

    database = str(tmp_path / "alerts.db")
    monkeypatch.setenv("ALERT_OUTBOX_DB_PATH", database)
    monkeypatch.setenv("EVIDENCE_STORE_DIR", str(tmp_path / "episodes"))
    monkeypatch.setenv("POLICY_QUOTA_DB_PATH", str(tmp_path / "quotas.db"))
    worker = build_worker()
    records, _ = worker.worker.outbox.enqueue(
        [
            {
                "status": "firing",
                "startsAt": "2026-10-19T09:00:00Z",
                "labels": {
                    "alertname": "CacDriftAlert",
                    "severity": "warning",
                    "service": "feature-pipeline",
                },
                "annotations": {"description": "Drift threshold exceeded"},
            }
        ]
    )

    assert worker.run_once()
    triage = worker.result_store.get(records[0].tracking_id)
    saved_alert = worker.worker.outbox.get(records[0].tracking_id)
    assert saved_alert.status == "COMPLETED"
    assert triage is not None
    assert triage.episode_id == "EP-0001"
    episode = json.loads(
        (tmp_path / "episodes" / f"{triage.episode_id}.json").read_text(encoding="utf-8")
    )
    assert episode["signal"]["signal_id"] == records[0].tracking_id
    assert episode["risk_id"] == "DATA-042"
    assert episode["action_proposal"]["type"] == "investigate"
    assert episode["execution"]["status"] == "SIMULATED"
    assert episode["state_trace"][-1] == "RESOLVED"
    assert len((tmp_path / "episodes" / "ledger.jsonl").read_text().splitlines()) == 1


def test_orchestrated_episode_is_not_duplicated_on_worker_retry(tmp_path, monkeypatch):
    from agentic_ops.entrypoints.alert_worker import build_worker

    database = str(tmp_path / "alerts.db")
    monkeypatch.setenv("ALERT_OUTBOX_DB_PATH", database)
    monkeypatch.setenv("EVIDENCE_STORE_DIR", str(tmp_path / "episodes"))
    monkeypatch.setenv("POLICY_QUOTA_DB_PATH", str(tmp_path / "quotas.db"))
    worker = build_worker()
    records, _ = worker.worker.outbox.enqueue(
        [{"status": "firing", "labels": {"alertname": "CacDriftAlert"}}]
    )
    handler = worker.worker.handler
    fail_once = [True]

    def persist_episode_then_crash(alert):
        handler(alert)
        if fail_once[0]:
            fail_once[0] = False
            raise RuntimeError("simulated process crash after episode persistence")

    worker.worker.handler = persist_episode_then_crash
    assert worker.run_once()
    assert worker.worker.outbox.get(records[0].tracking_id).status == "RETRY"
    with sqlite3.connect(database) as conn:
        conn.execute(
            "UPDATE alerts SET available_at=0 WHERE tracking_id=?",
            (records[0].tracking_id,),
        )
    assert worker.run_once()
    assert worker.worker.outbox.get(records[0].tracking_id).status == "COMPLETED"
    assert worker.result_store.get(records[0].tracking_id).episode_id == "EP-0001"
    assert len((tmp_path / "episodes" / "ledger.jsonl").read_text().splitlines()) == 1


def test_alert_mapping_rejects_unknown_risk_id(tmp_path):
    mapping_path = tmp_path / "mapping.yaml"
    mapping_path.write_text(
        "schema_version: 1\nmappings:\n  Alert:\n    risk_id: UNKNOWN-999\n",
        encoding="utf-8",
    )

    with pytest.raises(AlertMappingError, match="unknown risk"):
        AlertClassifier(mapping_path)


def test_alert_mapping_rejects_duplicate_yaml_keys(tmp_path):
    mapping_path = tmp_path / "mapping.yaml"
    mapping_path.write_text(
        "schema_version: 1\nmappings:\n"
        "  Alert:\n    risk_id: DATA-042\n"
        "  Alert:\n    risk_id: ML-014\n",
        encoding="utf-8",
    )

    with pytest.raises(AlertMappingError, match="duplicate key"):
        AlertClassifier(mapping_path)


def test_quota_reservation_is_atomic_and_not_reusable(tmp_path):
    manager = AtomicQuotaManager(str(tmp_path / "quotas.db"), clock=lambda: 100.0)
    assert manager.reserve("restart_pod", "staging/api", 1, 3600, "episode-1")
    assert not manager.reserve("restart_pod", "staging/api", 1, 3600, "episode-1")
    assert not manager.reserve("restart_pod", "staging/api", 1, 3600, "episode-2")
