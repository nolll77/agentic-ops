from __future__ import annotations

import importlib
import sqlite3
import time
from types import SimpleNamespace
import uuid

import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi.testclient import TestClient
from jwt.exceptions import InvalidTokenError

from agentic_ops.core.approvals import ApprovalRepo, FrozenProposal, Result
from agentic_ops.core.entra_oidc import EntraTokenVerifier
from agentic_ops.core.entra_scim import SCIMDirectory
from agentic_ops.entrypoints import approval_worker
from agentic_ops.cli.main import app


def _token_verifier():
    tenant_id = str(uuid.uuid4())
    issuer = f"https://login.microsoftonline.com/{tenant_id}/v2.0"
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public_key = private_key.public_key()
    verifier = EntraTokenVerifier(
        tenant_id,
        "api://agentic-ops",
        jwk_client=SimpleNamespace(
            get_signing_key_from_jwt=lambda token: SimpleNamespace(key=public_key)
        ),
    )
    claims = {
        "tid": tenant_id,
        "iss": issuer,
        "aud": "api://agentic-ops",
        "sub": "service-principal",
        "iat": int(time.time()),
        "exp": int(time.time()) + 300,
        "roles": ["AgenticOps.Admin"],
    }
    return tenant_id, private_key, verifier, claims


def test_entra_token_verifier_requires_signature_tenant_audience_and_app_role():
    tenant_id, private_key, verifier, claims = _token_verifier()
    valid = jwt.encode(claims, private_key, algorithm="RS256")
    assert verifier.verify(valid)["tid"] == tenant_id

    wrong_audience = jwt.encode(
        {**claims, "aud": "api://another-app"}, private_key, algorithm="RS256"
    )
    with pytest.raises(InvalidTokenError):
        verifier.verify(wrong_audience)

    missing_role = jwt.encode({**claims, "roles": []}, private_key, algorithm="RS256")
    with pytest.raises(InvalidTokenError):
        verifier.verify(missing_role)

    wrong_tenant = jwt.encode(
        {**claims, "tid": str(uuid.uuid4())}, private_key, algorithm="RS256"
    )
    with pytest.raises(InvalidTokenError):
        verifier.verify(wrong_tenant)

    expired = jwt.encode(
        {**claims, "exp": int(time.time()) - 60}, private_key, algorithm="RS256"
    )
    with pytest.raises(InvalidTokenError):
        verifier.verify(expired)


def test_scim_provisioning_maps_external_id_to_slack_and_revokes_roles(
    tmp_path, monkeypatch
):
    database = str(tmp_path / "identity.db")
    directory = SCIMDirectory(database, clock=lambda: 100.0)
    monkeypatch.setenv("SCIM_ENABLED", "true")
    monkeypatch.setenv("SCIM_DB_PATH", database)
    monkeypatch.setenv("SCIM_BEARER_TOKEN", "scim-token-" + "x" * 32)
    monkeypatch.setattr(app.state, "scim_directory", directory, raising=False)
    client = TestClient(app)

    assert client.get("/scim/v2/Users").status_code == 401
    headers = {"Authorization": "Bearer " + "scim-token-" + "x" * 32}
    user_response = client.post(
        "/scim/v2/Users",
        headers=headers,
        json={
            "schemas": ["urn:ietf:params:scim:schemas:core:2.0:User"],
            "externalId": "U_SLACK_123",
            "userName": "approver@example.invalid",
            "active": True,
        },
    )
    assert user_response.status_code == 201
    user = user_response.json()

    group_response = client.post(
        "/scim/v2/Groups",
        headers=headers,
        json={
            "schemas": ["urn:ietf:params:scim:schemas:core:2.0:Group"],
            "displayName": "SRE",
            "members": [{"value": user["id"]}],
        },
    )
    assert group_response.status_code == 201
    group = group_response.json()
    assert app.state.hitl.approvers.group_of("U_SLACK_123", "L2") == "SRE"
    assert client.get(
        "/scim/v2/Users",
        headers=headers,
        params={"filter": 'externalId eq "U_SLACK_123"'},
    ).json()["totalResults"] == 1

    removed = client.patch(
        f"/scim/v2/Groups/{group['id']}",
        headers=headers,
        json={
            "schemas": ["urn:ietf:params:scim:api:messages:2.0:PatchOp"],
            "Operations": [
                {
                    "op": "remove",
                    "path": f'members[value eq "{user["id"]}"]',
                }
            ],
        },
    )
    assert removed.status_code == 200
    assert app.state.hitl.approvers.group_of("U_SLACK_123", "L2") is None

    deactivated = client.patch(
        f"/scim/v2/Users/{user['id']}",
        headers=headers,
        json={
            "schemas": ["urn:ietf:params:scim:api:messages:2.0:PatchOp"],
            "Operations": [{"op": "replace", "path": "active", "value": False}],
        },
    )
    assert deactivated.status_code == 200
    assert deactivated.json()["active"] is False

    persisted = SCIMDirectory(database).get_user_by_external_id("U_SLACK_123")
    assert persisted is not None
    assert persisted["active"] is False


def test_approval_worker_rechecks_scim_membership_before_simulation(
    tmp_path, monkeypatch
):
    importlib.reload(approval_worker.executor)
    database = str(tmp_path / "approvals.db")
    directory = SCIMDirectory(database)
    user = directory.save_user(
        {"externalId": "U_APPROVER", "userName": "approver@example.invalid"}
    )
    group = directory.save_group(
        {"displayName": "SRE", "members": [{"value": user["id"]}]}
    )

    repo = ApprovalRepo(database, time.time)
    proposal = FrozenProposal(
        episode_id="EP-ENTRA-APPROVAL",
        action="create_issue",
        target="staging/api",
        risk_id="INFRA-001",
        policy_version="policy-1",
        required=1,
        required_groups=("SRE",),
        requester_id="U_REQUESTER",
    )
    digest = repo.open_request(proposal, ttl_s=60)
    assert repo.decide(
        proposal.episode_id,
        "U_APPROVER",
        "SRE",
        "approve",
        digest,
        digest,
        eligible_group_for=lambda user_id: directory.group_for_external_id(user_id, "L2"),
    )[0] is Result.CLAIMED

    directory.save_group({"displayName": "SRE", "members": []}, group["id"])
    monkeypatch.setenv("SCIM_ENABLED", "true")
    monkeypatch.setenv("SCIM_DB_PATH", database)
    monkeypatch.setenv("APPROVAL_DB_PATH", database)
    worker = approval_worker.build_worker()
    assert worker.run_once()

    with sqlite3.connect(database) as conn:
        request_status = conn.execute(
            "SELECT status FROM requests WHERE episode_id=?",
            (proposal.episode_id,),
        ).fetchone()[0]
        outbox_status = conn.execute(
            "SELECT status FROM execution_outbox WHERE episode_id=?",
            (proposal.episode_id,),
        ).fetchone()[0]
    assert request_status == "CLAIMED"
    assert outbox_status == "RETRY"
