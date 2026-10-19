import pytest

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


def test_grafana_webhook_endpoint_mounted_on_main_app():
    """Verify that POST /webhook/alerts is properly mounted and returns 202 on valid payload."""
    from fastapi.testclient import TestClient
    from agentic_ops.cli.main import app

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
    resp = client.post("/webhook/alerts", json=payload)
    assert resp.status_code == 202
    data = resp.json()
    assert data["status"] == "received"
    assert data["alerts_received"] == 1


def test_grafana_webhook_rejects_malformed_json():
    """Verify that POST /webhook/alerts rejects invalid payloads with 400."""
    from fastapi.testclient import TestClient
    from agentic_ops.cli.main import app

    client = TestClient(app)
    resp = client.post(
        "/webhook/alerts",
        content=b"not-json-content",
        headers={"Content-Type": "application/json"},
    )
    assert resp.status_code == 400
