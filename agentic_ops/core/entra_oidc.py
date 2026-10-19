from __future__ import annotations

import uuid
from typing import Any

import jwt
from jwt import PyJWKClient
from jwt.exceptions import InvalidTokenError, PyJWKClientConnectionError


class EntraConfigurationError(ValueError):
    pass


class EntraJWKSUnavailable(RuntimeError):
    pass


class EntraTokenVerifier:
    def __init__(
        self,
        tenant_id: str,
        audience: str,
        required_role: str = "AgenticOps.Admin",
        *,
        jwk_client: Any | None = None,
    ):
        try:
            self.tenant_id = str(uuid.UUID(tenant_id))
        except (ValueError, AttributeError) as exc:
            raise EntraConfigurationError("ENTRA_TENANT_ID must be a tenant UUID") from exc
        if not audience.strip():
            raise EntraConfigurationError("ENTRA_API_AUDIENCE is required")
        if not required_role.strip():
            raise EntraConfigurationError("ENTRA_REQUIRED_ROLE must not be empty")
        self.audience = audience
        self.required_role = required_role
        self.issuer = f"https://login.microsoftonline.com/{self.tenant_id}/v2.0"
        self._jwk_client = jwk_client or PyJWKClient(
            f"https://login.microsoftonline.com/{self.tenant_id}/discovery/v2.0/keys",
            cache_keys=True,
            lifespan=300,
            timeout=3,
        )

    def verify(self, token: str) -> dict[str, Any]:
        try:
            signing_key = self._jwk_client.get_signing_key_from_jwt(token).key
        except PyJWKClientConnectionError as exc:
            raise EntraJWKSUnavailable("Entra signing keys are unavailable") from exc
        try:
            claims = jwt.decode(
                token,
                signing_key,
                algorithms=["RS256"],
                audience=self.audience,
                issuer=self.issuer,
                options={"require": ["exp", "iat", "iss", "aud", "tid"]},
                leeway=30,
            )
        except InvalidTokenError:
            raise
        if claims.get("tid") != self.tenant_id:
            raise InvalidTokenError("token tenant does not match configured tenant")
        roles = claims.get("roles")
        if not isinstance(roles, list) or self.required_role not in roles:
            raise InvalidTokenError("required Entra application role is missing")
        return claims
