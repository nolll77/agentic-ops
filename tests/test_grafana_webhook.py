from pathlib import Path

import pytest
from agentic_ops.core.alert_outbox import AlertOutbox

from agentic_ops.entrypoints.grafana_webhook import parse_grafana_alerts


def test_parse_grafana_alerts():
    body = b'{"receiver":"local-test","alerts":[{"status":"firing","labels":{"alertname":"SmokeTest"}}]}'

    assert parse_grafana_alerts(body) == [
        {"status": "firing", "labels": {"alertname": "SmokeTest"}}
    ]


@pytest.mark.parametrize(
    ("body", "message"),
    [
        (b"not-json", "body must be valid JSON"),
        (b"[]", "JSON body must be an object"),
        (b"{}", "JSON body must contain an alerts array"),
        (b'{"alerts":[null]}', "each alert must be an object"),
    ],
)
def test_reject_invalid_grafana_payloads(body, message):
    with pytest.raises(ValueError, match=message):
        parse_grafana_alerts(body)


def test_grafana_webhook_persists_before_ack_and_deduplicates(tmp_path, monkeypatch):
    """The webhook acknowledges only after a durable outbox insert."""
    from fastapi.testclient import TestClient
    from agentic_ops.cli.main import app

    monkeypatch.setenv("GRAFANA_WEBHOOK_SECRET", "grafana-test-secret-" + "x" * 32)
    monkeypatch.setenv("ADMIN_API_KEY", "admin-test-secret-" + "y" * 32)
    app.state.alert_outbox = AlertOutbox(str(tmp_path / "alerts.db"))
    client = TestClient(app)
    payload = {
        "receiver": "grafana-alertmanager",
        "alerts": [
            {
                "status": "firing",
                "labels": {"alertname": "CacDriftAlert", "severity": "warning"},
                "annotations": {"description": "Feature drift exceeded 0.30 threshold"},
            }
        ],
    }
    headers = {"X-Grafana-Token": "grafana-test-secret-" + "x" * 32}
    resp = client.post("/webhook/alerts", json=payload, headers=headers)
    assert resp.status_code == 202
    data = resp.json()
    assert data["status"] == "accepted"
    assert data["alerts_received"] == 1
    assert data["accepted"] == 1
    assert data["duplicates"] == 0
    assert app.state.alert_outbox.get(data["tracking_ids"][0]).status == "RECEIVED"

    duplicate = client.post("/webhook/alerts", json=payload, headers=headers)
    assert duplicate.status_code == 202
    assert duplicate.json()["accepted"] == 0
    assert duplicate.json()["duplicates"] == 1
    assert duplicate.json()["tracking_ids"] == data["tracking_ids"]

    status = client.get(
        f"/api/alerts/{data['tracking_ids'][0]}",
        headers={"X-API-Key": "admin-test-secret-" + "y" * 32},
    )
    assert status.status_code == 200
    assert status.json()["status"] == "RECEIVED"

    from agentic_ops.core.alert_processing import (
        AlertClassificationStore,
        AlertClassifier,
        AlertTriageWorker,
    )
    worker = AlertTriageWorker(
        app.state.alert_outbox,
        AlertClassifier(
            Path(__file__).resolve().parents[1]
            / "agentic_ops"
            / "governance"
            / "alert_classification.yaml"
        ),
        AlertClassificationStore(str(tmp_path / "alerts.db")),
        "test-worker",
    )
    assert worker.run_once()
    completed = client.get(
        f"/api/alerts/{data['tracking_ids'][0]}",
        headers={"X-API-Key": "admin-test-secret-" + "y" * 32},
    )
    assert completed.status_code == 200
    assert completed.json()["status"] == "COMPLETED"
    assert completed.json()["triage"]["status"] == "CLASSIFIED"
    assert completed.json()["triage"]["risk_id"] == "DATA-042"


def test_grafana_webhook_rejects_missing_or_invalid_secret(monkeypatch):
    from fastapi.testclient import TestClient
    from agentic_ops.cli.main import app

    monkeypatch.delenv("GRAFANA_WEBHOOK_SECRET", raising=False)
    monkeypatch.delenv("GRAFANA_WEBHOOK_SECRET_PREVIOUS", raising=False)
    client = TestClient(app)
    body = {"alerts": [{"status": "firing", "labels": {"alertname": "test"}}]}
    assert client.post("/webhook/alerts", json=body).status_code == 503

    monkeypatch.setenv("GRAFANA_WEBHOOK_SECRET", "grafana-test-secret-" + "x" * 32)
    assert client.post("/webhook/alerts", json=body, headers={"X-Grafana-Token": "wrong"}).status_code == 401


def test_grafana_webhook_rejects_malformed_json(monkeypatch):
    """Verify that POST /webhook/alerts rejects invalid payloads with 400."""
    from fastapi.testclient import TestClient
    from agentic_ops.cli.main import app

    monkeypatch.setenv("GRAFANA_WEBHOOK_SECRET", "grafana-test-secret-" + "x" * 32)
    client = TestClient(app)
    resp = client.post(
        "/webhook/alerts",
        content=b"not-json-content",
        headers={
            "Content-Type": "application/json",
            "X-Grafana-Token": "grafana-test-secret-" + "x" * 32,
        },
    )
    assert resp.status_code == 400
