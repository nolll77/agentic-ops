from fastapi.testclient import TestClient
from jwt.exceptions import InvalidTokenError

from agentic_ops.cli.main import app
from agentic_ops.entrypoints import auth_middleware


def test_admin_route_fails_closed_without_configured_key(monkeypatch):
    monkeypatch.delenv("ADMIN_API_KEY", raising=False)
    monkeypatch.delenv("ADMIN_API_KEY_PREVIOUS", raising=False)
    monkeypatch.delenv("ENTRA_TENANT_ID", raising=False)
    monkeypatch.delenv("ENTRA_API_AUDIENCE", raising=False)
    response = TestClient(app).get("/mcp/manifest")
    assert response.status_code == 503


def test_admin_route_rejects_invalid_key_and_accepts_current_or_previous(monkeypatch):
    current = "admin-current-" + "a" * 32
    previous = "admin-previous-" + "b" * 32
    monkeypatch.delenv("ENTRA_TENANT_ID", raising=False)
    monkeypatch.delenv("ENTRA_API_AUDIENCE", raising=False)
    monkeypatch.setenv("ADMIN_API_KEY", current)
    monkeypatch.setenv("ADMIN_API_KEY_PREVIOUS", previous)
    client = TestClient(app)

    assert client.get("/mcp/manifest").status_code == 401
    assert client.get("/mcp/manifest", headers={"X-API-Key": current}).status_code == 200
    assert client.get(
        "/mcp/manifest", headers={"Authorization": "Bearer " + previous}
    ).status_code == 200


def test_admin_route_accepts_only_verified_entra_application_role(monkeypatch):
    class FakeVerifier:
        def verify(self, token):
            if token != "valid-entra-token":
                raise InvalidTokenError("invalid")
            return {"roles": ["AgenticOps.Admin"]}

    monkeypatch.delenv("ADMIN_API_KEY", raising=False)
    monkeypatch.delenv("ADMIN_API_KEY_PREVIOUS", raising=False)
    monkeypatch.setenv("ENTRA_TENANT_ID", "tenant-guid")
    monkeypatch.setenv("ENTRA_API_AUDIENCE", "api://agentic-ops")
    machine_key = "legacy-api-key-" + "x" * 32
    monkeypatch.setenv("ADMIN_API_KEY", machine_key)
    monkeypatch.setattr(
        auth_middleware, "_entra_verifier", lambda *args: FakeVerifier()
    )
    client = TestClient(app)

    assert client.get(
        "/mcp/manifest",
        headers={"Authorization": "Bearer valid-entra-token"},
    ).status_code == 200
    assert client.get(
        "/mcp/manifest",
        headers={"Authorization": "Bearer invalid-token"},
    ).status_code == 401
    assert client.get(
        "/mcp/manifest", headers={"X-API-Key": machine_key}
    ).status_code == 401


def test_partial_entra_configuration_fails_closed_even_with_api_key(monkeypatch):
    monkeypatch.setenv("ADMIN_API_KEY", "admin-key-" + "x" * 32)
    monkeypatch.delenv("ADMIN_API_KEY_PREVIOUS", raising=False)
    monkeypatch.setenv("ENTRA_TENANT_ID", "not-a-tenant-guid")
    monkeypatch.delenv("ENTRA_API_AUDIENCE", raising=False)

    response = TestClient(app).get(
        "/mcp/manifest",
        headers={"X-API-Key": "admin-key-" + "x" * 32},
    )
    assert response.status_code == 503
