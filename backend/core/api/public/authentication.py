from typing import Type

from rest_framework.authentication import TokenAuthentication, get_authorization_header
from rest_framework.exceptions import AuthenticationFailed
from django.utils.translation import gettext_lazy as _
from backend.core.api.public.models import APIAuthToken
from backend.models import User, Organization

from rest_framework import exceptions


class CustomBearerAuthentication(TokenAuthentication):
    keyword = "Bearer"

    def get_model(self) -> Type[APIAuthToken]:
        return APIAuthToken

    def authenticate(self, request):
        auth = get_authorization_header(request).split()

        if not auth or auth[0].lower() != self.keyword.lower().encode():
            return None

        if len(auth) == 1:
            msg = _("Invalid token header. No credentials provided.")
            raise exceptions.AuthenticationFailed(msg)
        elif len(auth) > 2:
            msg = _("Invalid token header. Token string should not contain spaces.")
            raise exceptions.AuthenticationFailed(msg)

        try:
            token = auth[1].decode()
        except UnicodeError:
            msg = _("Invalid token header. Token string should not contain invalid characters.")
            raise exceptions.AuthenticationFailed(msg)

        user_or_org, token = self.authenticate_credentials(token)

        request.actor = user_or_org

        if isinstance(user_or_org, Organization):
            request.team = user_or_org
            request.team_id = user_or_org.id
        else:
            request.team = None
            request.team_id = None

        return (user_or_org, token)

    def authenticate_credentials(self, raw_key) -> tuple[User | Organization | None, APIAuthToken]:
        model = self.get_model()

        try:
            token = model.objects.get(hashed_key=model.hash_raw_key(raw_key), active=True)
        except model.DoesNotExist:
            raise AuthenticationFailed(_("Invalid token."))

        if token.has_expired:
            raise AuthenticationFailed(_("Token has expired."))

        user_or_org = token.user or token.organization

        if user_or_org is None:
            raise AuthenticationFailed(_("Associated user or organization not found."))

        return user_or_org, token
