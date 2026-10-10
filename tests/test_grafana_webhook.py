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
