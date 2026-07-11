"""Built-in auth plugins: open, API key, static bearer, OIDC JWT (optional PyJWT)."""

from __future__ import annotations

import os
from typing import Any

from src.auth.base import AuthContext, AuthError, AuthPlugin


class OpenAuthPlugin:
    """No auth — local demos only."""

    name = "open"

    def authenticate(self, authorization: str | None, api_key: str | None) -> AuthContext | None:
        return AuthContext(subject="anonymous", method="open", claims={})


class ApiKeyAuthPlugin:
    name = "api_key"

    def __init__(self, expected: str):
        self.expected = expected

    def authenticate(self, authorization: str | None, api_key: str | None) -> AuthContext | None:
        if not self.expected:
            return None
        if api_key and api_key == self.expected:
            return AuthContext(subject="api_key_user", method="api_key", claims={})
        # also accept Authorization: ApiKey xxx
        if authorization and authorization.lower().startswith("apikey "):
            token = authorization.split(" ", 1)[1].strip()
            if token == self.expected:
                return AuthContext(subject="api_key_user", method="api_key", claims={})
        return None  # not matched; chain continues / deny later


class StaticBearerAuthPlugin:
    name = "bearer"

    def __init__(self, token: str):
        self.token = token

    def authenticate(self, authorization: str | None, api_key: str | None) -> AuthContext | None:
        if not self.token or not authorization:
            return None
        if not authorization.lower().startswith("bearer "):
            return None
        got = authorization.split(" ", 1)[1].strip()
        if got == self.token:
            return AuthContext(subject="bearer_user", method="bearer", claims={})
        raise AuthError("invalid bearer token")


class OIDCAuthPlugin:
    """Optional OIDC JWT validation when PyJWT + jwks configured.

    Env:
      OIDC_ISSUER, OIDC_AUDIENCE, OIDC_JWKS_URL (or auto {issuer}/.well-known/openid-configuration)
    """

    name = "oidc"

    def __init__(
        self,
        issuer: str,
        audience: str,
        jwks_url: str | None = None,
    ):
        self.issuer = issuer.rstrip("/")
        self.audience = audience
        self.jwks_url = jwks_url
        self._jwks: dict[str, Any] | None = None

    def authenticate(self, authorization: str | None, api_key: str | None) -> AuthContext | None:
        if not self.issuer or not authorization:
            return None
        if not authorization.lower().startswith("bearer "):
            return None
        token = authorization.split(" ", 1)[1].strip()
        try:
            import jwt
            from jwt import PyJWKClient
        except ImportError as exc:
            raise AuthError(
                "OIDC configured but PyJWT not installed (pip install PyJWT cryptography)"
            ) from exc

        jwks_url = self.jwks_url
        if not jwks_url:
            # try well-known
            import httpx

            try:
                with httpx.Client(timeout=10.0) as client:
                    r = client.get(f"{self.issuer}/.well-known/openid-configuration")
                    r.raise_for_status()
                    jwks_url = (r.json() or {}).get("jwks_uri")
            except Exception as e:  # noqa: BLE001
                raise AuthError(f"OIDC discovery failed: {e}") from e
        if not jwks_url:
            raise AuthError("OIDC JWKS URL missing")

        try:
            jwks_client = PyJWKClient(jwks_url)
            signing_key = jwks_client.get_signing_key_from_jwt(token)
            claims = jwt.decode(
                token,
                signing_key.key,
                algorithms=["RS256", "ES256"],
                audience=self.audience,
                issuer=self.issuer,
            )
            sub = str(claims.get("sub") or claims.get("email") or "oidc_user")
            return AuthContext(subject=sub, method="oidc", claims=dict(claims))
        except AuthError:
            raise
        except Exception as exc:  # noqa: BLE001
            raise AuthError(f"OIDC token invalid: {exc}") from exc


def build_auth_chain() -> list[AuthPlugin]:
    """Build plugin chain from environment / settings."""
    from src.config import get_settings

    s = get_settings()
    plugins: list[AuthPlugin] = []

    # Prefer strict plugins when configured
    api_key = s.api_access_key or os.environ.get("API_ACCESS_KEY")
    bearer = os.environ.get("API_BEARER_TOKEN") or getattr(s, "api_bearer_token", None)
    oidc_issuer = os.environ.get("OIDC_ISSUER") or getattr(s, "oidc_issuer", None)
    oidc_aud = os.environ.get("OIDC_AUDIENCE") or getattr(s, "oidc_audience", None)
    oidc_jwks = os.environ.get("OIDC_JWKS_URL") or getattr(s, "oidc_jwks_url", None)

    if api_key:
        plugins.append(ApiKeyAuthPlugin(api_key))
    if bearer:
        plugins.append(StaticBearerAuthPlugin(bearer))
    if oidc_issuer and oidc_aud:
        plugins.append(OIDCAuthPlugin(oidc_issuer, oidc_aud, oidc_jwks))

    if not plugins:
        plugins.append(OpenAuthPlugin())
    return plugins


def authenticate_request(authorization: str | None, api_key: str | None) -> AuthContext:
    chain = build_auth_chain()
    # open-only short circuit
    if len(chain) == 1 and chain[0].name == "open":
        return chain[0].authenticate(authorization, api_key)  # type: ignore[return-value]

    last_err: AuthError | None = None
    for plugin in chain:
        try:
            ctx = plugin.authenticate(authorization, api_key)
            if ctx is not None:
                return ctx
        except AuthError as exc:
            last_err = exc
    if last_err:
        raise last_err
    raise AuthError("authentication required")
