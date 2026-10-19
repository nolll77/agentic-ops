from __future__ import annotations

import hmac
import logging
import os
import re
import sqlite3
from typing import Any

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse, Response

from agentic_ops.core.entra_scim import SCIMDirectory, scim_database_path, scim_enabled


log = logging.getLogger("entra_scim")
router = APIRouter(prefix="/scim/v2")
_BEARER = re.compile(r"^Bearer\s+(.+)$", re.I)


def _error(status: int, detail: str, scim_type: str | None = None) -> JSONResponse:
    body: dict[str, Any] = {
        "schemas": ["urn:ietf:params:scim:api:messages:2.0:Error"],
        "status": str(status),
        "detail": detail,
    }
    if scim_type:
        body["scimType"] = scim_type
    return JSONResponse(body, status_code=status, media_type="application/scim+json")


def _success(payload: Any, status: int = 200) -> JSONResponse:
    return JSONResponse(payload, status_code=status, media_type="application/scim+json")


async def authenticate_scim(request: Request) -> JSONResponse | None:
    if not scim_enabled():
        return _error(503, "SCIM provisioning is not enabled")
    expected = os.environ.get("SCIM_BEARER_TOKEN", "")
    if len(expected) < 32:
        return _error(503, "SCIM bearer authentication is not configured")
    match = _BEARER.fullmatch(request.headers.get("authorization", ""))
    supplied = match.group(1) if match else ""
    if not supplied or not hmac.compare_digest(supplied, expected):
        return _error(401, "unauthorized")
    return None


def _directory(request: Request) -> SCIMDirectory:
    directory = getattr(request.app.state, "scim_directory", None)
    if directory is None:
        directory = SCIMDirectory(scim_database_path())
        request.app.state.scim_directory = directory
    return directory


async def _body(request: Request) -> dict[str, Any]:
    try:
        payload = await request.json()
    except (ValueError, UnicodeDecodeError):
        raise ValueError("request body must be valid JSON")
    if not isinstance(payload, dict):
        raise ValueError("SCIM resource must be a JSON object")
    return payload


def _translate_error(exc: Exception) -> JSONResponse:
    if isinstance(exc, KeyError):
        return _error(404, "resource not found")
    if isinstance(exc, ValueError):
        return _error(400, str(exc), "invalidValue")
    if isinstance(exc, sqlite3.IntegrityError):
        return _error(409, "resource conflicts with an existing resource", "uniqueness")
    log.exception("SCIM persistence operation failed")
    return _error(500, "SCIM operation failed")


@router.get("/ServiceProviderConfig")
async def service_provider_config(auth=Depends(authenticate_scim)):
    if auth:
        return auth
    return _success({
        "schemas": ["urn:ietf:params:scim:schemas:core:2.0:ServiceProviderConfig"],
        "patch": {"supported": True},
        "bulk": {"supported": False, "maxOperations": 0, "maxPayloadSize": 0},
        "filter": {"supported": True, "maxResults": 1000},
        "changePassword": {"supported": False},
        "sort": {"supported": False},
        "etag": {"supported": False},
        "authenticationSchemes": [
            {
                "type": "oauthbearertoken",
                "name": "Bearer Token",
                "description": "Provisioning token configured for this Entra enterprise application.",
                "primary": True,
            }
        ],
    })


@router.get("/Users")
async def list_users(
    request: Request,
    filter: str | None = None,
    startIndex: int = 1,
    count: int = 100,
    auth=Depends(authenticate_scim),
):
    if auth:
        return auth
    try:
        return _success(
            _directory(request).list_resources(
                "Users", filter_expression=filter, start_index=startIndex, count=count
            )
        )
    except (ValueError, TypeError) as exc:
        return _translate_error(exc)


@router.post("/Users")
async def create_user(request: Request, auth=Depends(authenticate_scim)):
    if auth:
        return auth
    try:
        result = _directory(request).save_user(await _body(request))
        return JSONResponse(result, status_code=201, media_type="application/scim+json")
    except (ValueError, KeyError, sqlite3.IntegrityError) as exc:
        return _translate_error(exc)


@router.get("/Users/{user_id}")
async def get_user(user_id: str, request: Request, auth=Depends(authenticate_scim)):
    if auth:
        return auth
    resource = _directory(request).get_user(user_id)
    return (
        JSONResponse(resource, media_type="application/scim+json")
        if resource
        else _error(404, "user not found")
    )


@router.put("/Users/{user_id}")
async def replace_user(user_id: str, request: Request, auth=Depends(authenticate_scim)):
    if auth:
        return auth
    try:
        return JSONResponse(
            _directory(request).save_user(await _body(request), user_id),
            media_type="application/scim+json",
        )
    except (ValueError, KeyError, sqlite3.IntegrityError) as exc:
        return _translate_error(exc)


@router.patch("/Users/{user_id}")
async def patch_user(user_id: str, request: Request, auth=Depends(authenticate_scim)):
    if auth:
        return auth
    directory = _directory(request)
    current = directory.get_user(user_id)
    if current is None:
        return _error(404, "user not found")
    try:
        payload = await _body(request)
        operations = payload.get("Operations")
        if not isinstance(operations, list) or not operations:
            raise ValueError("Operations must be a non-empty array")
        user = {
            "externalId": current["externalId"],
            "userName": current["userName"],
            "active": current["active"],
        }
        for operation in operations:
            if not isinstance(operation, dict):
                raise ValueError("each SCIM operation must be an object")
            op = str(operation.get("op", "")).lower()
            if op not in {"add", "replace"}:
                raise ValueError("only add and replace are supported for user attributes")
            path = str(operation.get("path", "")).lower()
            value = operation.get("value")
            if path in {"active", "username", "externalid"}:
                user[{"active": "active", "username": "userName", "externalid": "externalId"}[path]] = value
            elif not path and isinstance(value, dict):
                for field in ("active", "userName", "externalId"):
                    if field in value:
                        user[field] = value[field]
            else:
                raise ValueError("only active, userName, and externalId may be patched")
        result = directory.save_user(user, user_id)
        return JSONResponse(result, media_type="application/scim+json")
    except (ValueError, KeyError, sqlite3.IntegrityError) as exc:
        return _translate_error(exc)


@router.delete("/Users/{user_id}")
async def delete_user(user_id: str, request: Request, auth=Depends(authenticate_scim)):
    if auth:
        return auth
    return (
        Response(status_code=204)
        if _directory(request).delete_user(user_id)
        else _error(404, "user not found")
    )


@router.get("/Groups")
async def list_groups(
    request: Request,
    filter: str | None = None,
    startIndex: int = 1,
    count: int = 100,
    auth=Depends(authenticate_scim),
):
    if auth:
        return auth
    try:
        return _success(
            _directory(request).list_resources(
                "Groups", filter_expression=filter, start_index=startIndex, count=count
            )
        )
    except (ValueError, TypeError) as exc:
        return _translate_error(exc)


@router.post("/Groups")
async def create_group(request: Request, auth=Depends(authenticate_scim)):
    if auth:
        return auth
    try:
        result = _directory(request).save_group(await _body(request))
        return JSONResponse(result, status_code=201, media_type="application/scim+json")
    except (ValueError, KeyError, sqlite3.IntegrityError) as exc:
        return _translate_error(exc)


@router.get("/Groups/{group_id}")
async def get_group(group_id: str, request: Request, auth=Depends(authenticate_scim)):
    if auth:
        return auth
    resource = _directory(request).get_group(group_id)
    return (
        JSONResponse(resource, media_type="application/scim+json")
        if resource
        else _error(404, "group not found")
    )


@router.put("/Groups/{group_id}")
async def replace_group(group_id: str, request: Request, auth=Depends(authenticate_scim)):
    if auth:
        return auth
    try:
        return JSONResponse(
            _directory(request).save_group(await _body(request), group_id),
            media_type="application/scim+json",
        )
    except (ValueError, KeyError, sqlite3.IntegrityError) as exc:
        return _translate_error(exc)


@router.patch("/Groups/{group_id}")
async def patch_group(group_id: str, request: Request, auth=Depends(authenticate_scim)):
    if auth:
        return auth
    try:
        payload = await _body(request)
        operations = payload.get("Operations")
        if not isinstance(operations, list) or not operations:
            raise ValueError("Operations must be a non-empty array")
        return JSONResponse(
            _directory(request).patch_group(group_id, operations),
            media_type="application/scim+json",
        )
    except (ValueError, KeyError, sqlite3.IntegrityError) as exc:
        return _translate_error(exc)


@router.delete("/Groups/{group_id}")
async def delete_group(group_id: str, request: Request, auth=Depends(authenticate_scim)):
    if auth:
        return auth
    return (
        Response(status_code=204)
        if _directory(request).delete_group(group_id)
        else _error(404, "group not found")
    )
