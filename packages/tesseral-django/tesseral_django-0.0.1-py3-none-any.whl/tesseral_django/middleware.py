from functools import wraps
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse
from tesseral.client import Tesseral
from tesseral.access_tokens import (
    AccessTokenAuthenticator,
    _InvalidAccessTokenException,
)
from tesseral.errors import BadRequestError

from .context import _AuthContext, _AccessTokenDetails, _APIKeyDetails
from .credentials import is_jwt_format, is_api_key_format

import os

_PREFIX_BEARER = "Bearer "


class AuthMiddleware(MiddlewareMixin):
    def __init__(self, get_response=None):
        super().__init__(get_response)
        self.get_response = get_response

        # Read config from Django settings
        self.backend_api_key = getattr(
            settings,
            "TESSERAL_BACKEND_API_KEY",
            os.environ.get("TESSERAL_BACKEND_API_KEY", None),
        )
        self.publishable_key = getattr(settings, "TESSERAL_PUBLISHABLE_KEY", None)
        self.config_api_hostname = getattr(
            settings, "TESSERAL_CONFIG_API_HOSTNAME", "config.tesseral.com"
        )
        self.jwks_refresh_interval_seconds = getattr(
            settings, "TESSERAL_JWKS_REFRESH_INTERVAL_SECONDS", 3600
        )
        self.api_keys_enabled = getattr(settings, "TESSERAL_API_KEYS_ENABLED", False)

        if self.api_keys_enabled and "TESSERAL_BACKEND_API_KEY" not in os.environ:
            raise RuntimeError(
                "If api_keys_enabled is True, you must provide TESSERAL_BACKEND_API_KEY in the environment."
            )

        self.tesseral_client = Tesseral(backend_api_key=self.backend_api_key)
        self.access_token_authenticator = AccessTokenAuthenticator(
            publishable_key=self.publishable_key,
            config_api_hostname=self.config_api_hostname,
            jwks_refresh_interval_seconds=self.jwks_refresh_interval_seconds,
        )
        self.project_id = self.access_token_authenticator.project_id()

    def process_request(self, request):
        credential = _credential(request, self.project_id)

        if is_jwt_format(credential):
            try:
                claims = self.access_token_authenticator.authenticate_access_token(
                    access_token=credential
                )
            except _InvalidAccessTokenException:
                return JsonResponse({"error": "Unauthorized"}, status=401)
            except Exception as e:
                raise e

            access = _AccessTokenDetails()
            access.access_token = credential
            access.access_token_claims = claims

            auth_context = _AuthContext()
            auth_context.access_token = access
            request.tesseral_auth = auth_context
            return None

        if self.api_keys_enabled and is_api_key_format(credential):
            try:
                resp = self.tesseral_client.api_keys.authenticate_api_key(
                    secret_token=credential
                )
            except BadRequestError:
                return JsonResponse({"error": "Unauthorized"}, status=401)
            except Exception as e:
                raise e

            api_key = _APIKeyDetails()
            api_key.api_key_secret_token = credential
            api_key.authenticate_api_key_response = resp

            auth_context = _AuthContext()
            auth_context.api_key = api_key
            request.tesseral_auth = auth_context
            return None

        return JsonResponse({"error": "Unauthorized"}, status=401)


def require_auth(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not _user_is_authenticated(request):
            return JsonResponse({"error": "Unauthorized"}, status=401)
        return view_func(request, *args, **kwargs)

    return _wrapped_view


def _credential(request, project_id: str) -> str:
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith(_PREFIX_BEARER):
        return auth_header[len(_PREFIX_BEARER) :]

    cookie_name = f"tesseral_{project_id}_access_token"
    if cookie_name in request.COOKIES:
        return request.COOKIES[cookie_name]

    return ""


def _user_is_authenticated(request) -> bool:
    return hasattr(request, "tesseral_auth") and (
        request.tesseral_auth.access_token is not None
        or request.tesseral_auth.api_key is not None
    )
