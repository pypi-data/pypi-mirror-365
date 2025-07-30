"""Helpers/overrides for django-allauth."""

from base64 import b64decode
from typing import Any, Optional

from django.contrib.auth import authenticate
from django.contrib.auth.validators import ASCIIUsernameValidator
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest
from django.utils.translation import gettext_lazy as _

from oauth2_provider.models import AbstractApplication
from oauth2_provider.oauth2_validators import OAuth2Validator
from oauth2_provider.scopes import BaseScopes
from oauth2_provider.views.mixins import (
    ClientProtectedResourceMixin as _ClientProtectedResourceMixin,
)
from oauthlib.common import Request as OauthlibRequest

from .apps import AppConfig
from .core_helpers import get_site_preferences


class CustomOAuth2Validator(OAuth2Validator):
    def get_additional_claims(self, request: OauthlibRequest) -> dict[str, Any]:
        # Pull together scopes from request and from access token
        scopes = request.scopes.copy()
        if request.access_token:
            scopes += request.access_token.scope.split(" ")

        claims = {}
        # Pull together claim data from all apps
        for app in AppConfig.__subclasses__():
            claims.update(app.get_additional_claims(scopes, request))

        return claims

    def get_userinfo_claims(self, request: OauthlibRequest) -> dict[str, Any]:
        oidc_claims = super().get_oidc_claims(request.access_token, None, request)
        additional_claims = self.get_additional_claims(request)
        return oidc_claims | additional_claims


class AppScopes(BaseScopes):
    """Scopes backend for django-oauth-toolkit gathering scopes from apps.

    Will call the respective method on all known AlekSIS app configs and
    join the results.
    """

    def get_all_scopes(self) -> dict[str, str]:
        scopes = {}
        for app in AppConfig.__subclasses__():
            scopes |= app.get_all_scopes()
        return scopes

    def get_available_scopes(
        self,
        application: Optional[AbstractApplication] = None,
        request: Optional[HttpRequest] = None,
        *args,
        **kwargs,
    ) -> list[str]:
        scopes = []
        for app in AppConfig.__subclasses__():
            scopes += app.get_available_scopes()
        # Filter by allowed scopes of requesting application
        if application and application.allowed_scopes:
            scopes = list(filter(lambda scope: scope in application.allowed_scopes, scopes))
        return scopes

    def get_default_scopes(
        self,
        application: Optional[AbstractApplication] = None,
        request: Optional[HttpRequest] = None,
        *args,
        **kwargs,
    ) -> list[str]:
        scopes = []
        for app in AppConfig.__subclasses__():
            scopes += app.get_default_scopes()
        # Filter by allowed scopes of requesting application
        if application and application.allowed_scopes:
            scopes = list(filter(lambda scope: scope in application.allowed_scopes, scopes))
        return scopes


class ClientProtectedResourceMixin(_ClientProtectedResourceMixin):
    """Mixin for protecting resources with client authentication as mentioned in rfc:`3.2.1`.

    This involves authenticating with any of: HTTP Basic Auth, Client Credentials and
    Access token in that order. Breaks off after first validation.

    This sub-class extends the functionality of Django OAuth Toolkit's mixin with support
    for AlekSIS's `allowed_scopes` feature. For applications that have configured allowed
    scopes, the required scopes for the view are checked to be a subset of the application's
    allowed scopes (best to be combined with ScopedResourceMixin).
    """

    def authenticate_client(self, request: HttpRequest) -> bool:
        """Return a boolean representing if client is authenticated with client credentials.

        If the view has configured required scopes, they are verified against the application's
        allowed scopes.
        """
        # Build an OAuth request so we can handle client information
        core = self.get_oauthlib_core()
        uri, http_method, body, headers = core._extract_params(request)
        oauth_request = OauthlibRequest(uri, http_method, body, headers)

        # Verify general authentication of the client
        if not core.server.request_validator.authenticate_client(oauth_request):
            # Client credentials were invalid
            return False

        # Verify scopes of configured application
        # The OAuth request was enriched with a reference to the Application when using the
        #  validator above.
        if not oauth_request.client.allowed_scopes:
            # If there are no allowed scopes, the client is not allowed to access this resource
            return False

        required_scopes = set(self.get_scopes() or [])
        allowed_scopes = set(AppScopes().get_available_scopes(oauth_request.client) or [])
        return required_scopes.issubset(allowed_scopes)


class BasicAuthMixin:
    """Mixin for protecting views using HTTP Basic Auth.

    Useful for views being used outside a regular session authenticated, e.g. a
    CalDAV client providing only username/password authentication.  For its
    `dispatch` method to be called, the BasicAuthMixin has to be the first
    parent class. Make sure to call `super().dispatch(self, *args, **kwargs)`
    if you implement a custom dispatch method.
    """

    def dispatch(self, request, *args, **kwargs):
        if request.user is not None and request.user.is_authenticated:
            return super().dispatch(request, *args, **kwargs)

        auth_header = request.headers.get("Authorization")

        if auth_header is None or not auth_header.startswith("Basic "):
            return HttpResponse(
                "Unauthorized",
                status=401,
                headers={"WWW-Authenticate": 'Basic realm="AlekSIS", charset="utf-8"'},
            )

        auth_data = auth_header.removeprefix("Basic ")
        try:
            auth_data_decoded = b64decode(auth_data).decode("ascii")
        except UnicodeDecodeError:
            try:
                auth_data_decoded = b64decode(auth_data).decode("utf-8")
            except UnicodeDecodeError:
                return HttpResponseBadRequest(
                    "HTTP Basic Auth credentials must be encoded in UTF-8 or ASCII"
                )
        username, password = auth_data_decoded.split(":", 1)
        user = authenticate(request, username=username, password=password)

        if user is not None:
            request.user = user
            return super().dispatch(request, *args, **kwargs)
        else:
            return HttpResponse("Unauthorized", status=401)


def validate_username_preference_regex(value: str):
    regex = get_site_preferences()["auth__allowed_username_regex"]
    return RegexValidator(regex)(value)


def validate_username_preference_disallowed_uid(value: str):
    if value in get_site_preferences()["auth__disallowed_uids"].split(","):
        raise ValidationError(_("This username is not allowed."))


custom_username_validators = [
    validate_username_preference_regex,
    ASCIIUsernameValidator(),
    validate_username_preference_disallowed_uid,
]
