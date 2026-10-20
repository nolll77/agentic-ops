from __future__ import annotations

import hmac
import os
import logging
from collections.abc import Iterable
from functools import lru_cache

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.concurrency import run_in_threadpool
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from jwt.exceptions import InvalidTokenError, PyJWKClientError

from agentic_ops.core.entra_oidc import (
    EntraConfigurationError,
    EntraJWKSUnavailable,
    EntraTokenVerifier,
)

log = logging.getLogger(__name__)

PROTECTED_PATH_PREFIXES = (
    "/api/alerts/",
    "/mcp",
)


def _configured_api_keys() -> tuple[str, ...]:
    return tuple(
        key
        for key in (
            os.environ.get("ADMIN_API_KEY", ""),
            os.environ.get("ADMIN_API_KEY_PREVIOUS", ""),
        )
        if len(key) >= 32
    )


def _valid_key(candidate: str, keys: Iterable[str]) -> bool:
    matches = [hmac.compare_digest(candidate, key) for key in keys]
    return any(matches)


@lru_cache(maxsize=8)
def _entra_verifier(tenant_id: str, audience: str, required_role: str) -> EntraTokenVerifier:
    return EntraTokenVerifier(tenant_id, audience, required_role)


class AdminAPIKeyMiddleware(BaseHTTPMiddleware):
    """Fail-closed API-key or Entra application-role gate for admin routes."""

    async def dispatch(self, request: Request, call_next) -> Response:
        path = request.url.path
        if not any(path == prefix.rstrip("/") or path.startswith(prefix) for prefix in PROTECTED_PATH_PREFIXES):
            return await call_next(request)

        keys = _configured_api_keys()
        tenant_id = os.environ.get("ENTRA_TENANT_ID", "")
        audience = os.environ.get("ENTRA_API_AUDIENCE", "")
        required_role = os.environ.get("ENTRA_REQUIRED_ROLE", "AgenticOps.Admin")
        entra_configured = bool(tenant_id or audience)
        authorization = request.headers.get("authorization", "")
        bearer = authorization[7:] if authorization.lower().startswith("bearer ") else ""
        if entra_configured:
            try:
                verifier = _entra_verifier(tenant_id, audience, required_role)
            except EntraConfigurationError:
                log.exception("Entra admin authentication is misconfigured")
                return JSONResponse(
                    {"detail": "Entra administrative authentication is misconfigured"},
                    status_code=503,
                )
            if not bearer:
                return JSONResponse({"detail": "unauthorized"}, status_code=401)
            try:
                await run_in_threadpool(verifier.verify, bearer)
            except EntraJWKSUnavailable:
                log.exception("Entra signing-key service is unavailable")
                return JSONResponse(
                    {"detail": "identity provider temporarily unavailable"},
                    status_code=503,
                )
            except (InvalidTokenError, PyJWKClientError):
                log.warning("Entra bearer token rejected", exc_info=True)
                return JSONResponse({"detail": "unauthorized"}, status_code=401)
            return await call_next(request)

        if not keys:
            return JSONResponse(
                {"detail": "administrative authentication is not configured"},
                status_code=503,
            )
        candidate = request.headers.get("x-api-key", "") or bearer
        if candidate and _valid_key(candidate, keys):
            return await call_next(request)
        return JSONResponse({"detail": "unauthorized"}, status_code=401)
