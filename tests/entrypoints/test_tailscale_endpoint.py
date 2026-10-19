"""
Unit & DevSecOps Security Tests for the Tailscale Status Endpoint (/api/tailscale/status).
Verifies:
1. GET /api/tailscale/status never exposes raw Tailscale private state (ts_state_b64 is removed).
2. IPv4 addresses are masked as '100.X.***.***' to prevent internal network leakage.
3. IPv6 ULA addresses are masked as 'fd7a:115c:****:****'.
4. auth_url is strictly redacted on the public endpoint and redirected to private Render logs.
5. Graceful fallback when the tailscaled daemon is unreachable or stopped.
"""

import json
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient

from agentic_ops.cli.main import app

client = TestClient(app)


def test_tailscale_status_default_live_call():
    """Default invocation of /api/tailscale/status must return 200 with standard schema."""
    resp = client.get("/api/tailscale/status")
    assert resp.status_code == 200
    data = resp.json()
    assert "backend_state" in data
    assert "tailscale_ips" in data
    assert "has_persisted_state" in data
    assert "ts_state_b64" not in data, "ts_state_b64 MUST NOT be exposed"


@patch("os.path.exists", return_value=True)
@patch("subprocess.run")
def test_tailscale_status_masks_ipv4_and_ipv6_and_omits_state(mock_run, mock_exists):
    """Running node status must mask both IPv4 and IPv6 and omit private state."""
    mock_run.return_value = MagicMock(
        returncode=0,
        stdout=json.dumps({
            "BackendState": "Running",
            "AuthURL": "https://login.tailscale.com/a/secret_token",
            "Self": {
                "HostName": "agentic-ops-render",
                "TailscaleIPs": [
                    "100.85.198.81",
                    "fd7a:115c:a1e2:ab12:4843:cd96:6255:c651",
                ],
            },
        }),
    )

    resp = client.get("/api/tailscale/status")
    assert resp.status_code == 200
    data = resp.json()

    assert data["backend_state"] == "Running"
    assert data["hostname"] == "agentic-ops-render"
    assert "ts_state_b64" not in data

    # When Running, auth_url must be None
    assert data["auth_url"] is None

    # Verify IP masking
    assert data["tailscale_ips"] == [
        "100.85.***.***",
        "fd7a:115c:****:****",
    ]


@patch("os.path.exists", return_value=True)
@patch("subprocess.run")
def test_tailscale_status_needs_login_redacts_auth_url(mock_run, mock_exists):
    """NeedsLogin state must strictly redact auth_url to prevent rogue claims."""
    mock_run.return_value = MagicMock(
        returncode=0,
        stdout=json.dumps({
            "BackendState": "NeedsLogin",
            "AuthURL": "https://login.tailscale.com/a/secret_login_token",
            "Self": {
                "HostName": "agentic-ops-render",
                "TailscaleIPs": [],
            },
        }),
    )

    resp = client.get("/api/tailscale/status")
    assert resp.status_code == 200
    data = resp.json()

    assert data["backend_state"] == "NeedsLogin"
    assert "https://login.tailscale.com" not in str(data["auth_url"])
    assert "[REDACTED_FOR_SECURITY" in data["auth_url"]


@patch("subprocess.run", side_effect=FileNotFoundError("tailscale not found"))
def test_tailscale_status_daemon_error_fallback(mock_run):
    """When tailscale daemon binary or socket fails, endpoint returns clean fallback."""
    resp = client.get("/api/tailscale/status")
    assert resp.status_code == 200
    data = resp.json()

    assert data["backend_state"] in ("Stopped", "NeedsLogin")
    assert data["tailscale_ips"] == []
    assert data["auth_url"] is None
