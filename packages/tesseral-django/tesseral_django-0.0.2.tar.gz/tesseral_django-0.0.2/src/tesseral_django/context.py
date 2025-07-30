from typing import Optional
from tesseral import AccessTokenClaims
from tesseral.types import AuthenticateApiKeyResponse
from django.http import HttpRequest

from .errors import NotAnAccessTokenError


class _AccessTokenDetails:
    access_token: str
    access_token_claims: AccessTokenClaims


class _APIKeyDetails:
    api_key_secret_token: str
    authenticate_api_key_response: AuthenticateApiKeyResponse


class _AuthContext:
    access_token: Optional[_AccessTokenDetails] = None
    api_key: Optional[_APIKeyDetails] = None


def _extract_auth_context(request: HttpRequest, name: str) -> _AuthContext:
    if not hasattr(request, "tesseral_auth"):
        raise RuntimeError(
            f"Called {name}() outside of an authenticated request. Did you forget to use RequireAuthMiddleware?"
        )
    return request.tesseral_auth


def credentials_type(request: HttpRequest) -> str:
    auth_context = _extract_auth_context(request, "credentials_type")
    if auth_context.access_token:
        return "access_token"
    if auth_context.api_key:
        return "api_key"
    raise RuntimeError("Unreachable")


def organization_id(request: HttpRequest) -> str:
    auth_context = _extract_auth_context(request, "organization_id")
    if auth_context.access_token:
        return auth_context.access_token.access_token_claims.organization.id  # type: ignore[union-attr,return-value]
    if (
        auth_context.api_key
        and auth_context.api_key.authenticate_api_key_response.organization_id
        is not None
    ):
        return auth_context.api_key.authenticate_api_key_response.organization_id
    raise RuntimeError("Unreachable")


def access_token_claims(request: HttpRequest) -> AccessTokenClaims:
    auth_context = _extract_auth_context(request, "access_token_claims")
    if auth_context.access_token:
        return auth_context.access_token.access_token_claims
    if auth_context.api_key:
        raise NotAnAccessTokenError(
            "access_token_claims() called with API key credentials."
        )
    raise RuntimeError("Unreachable")


def credentials(request: HttpRequest) -> str:
    auth_context = _extract_auth_context(request, "credentials")
    if auth_context.access_token:
        return auth_context.access_token.access_token
    if auth_context.api_key:
        return auth_context.api_key.api_key_secret_token
    raise RuntimeError("Unreachable")


def has_permission(request: HttpRequest, action: str) -> bool:
    """
    Check if the user has permission to perform a specific action.
    """
    auth_context = _extract_auth_context(request, "has_permission")
    if auth_context.access_token:
        actions = auth_context.access_token.access_token_claims.actions
        return bool(actions and action in actions)
    if auth_context.api_key:
        actions = auth_context.api_key.authenticate_api_key_response.actions
        return bool(actions and action in actions)
    raise RuntimeError("Unreachable")
