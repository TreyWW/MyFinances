from typing import Type

from rest_framework import exceptions
from rest_framework.authentication import TokenAuthentication, get_authorization_header
from rest_framework.exceptions import AuthenticationFailed

from backend.api.public import APIAuthToken
from backend.models import User, Team


class CustomBearerAuthentication(TokenAuthentication):
    keyword = "Bearer"

    def get_model(self) -> Type[APIAuthToken]:
        return APIAuthToken

    def authenticate_credentials(self, raw_key) -> tuple[User | Team, APIAuthToken]:
        model = self.get_model()

        try:
            token = model.objects.get(hashed_key=model.hash_raw_key(raw_key), active=True)
        except model.DoesNotExist:
            raise AuthenticationFailed("Invalid token.")

        if token.has_expired():
            raise AuthenticationFailed("Token has expired.")

        # todo: make sure this is safe to set request.user = <Team> obj
        return token.user or token.team, token

    # todo: override more methods + add hashing
