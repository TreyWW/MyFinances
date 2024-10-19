from typing import Type

from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed

from backend.core.api.public.models import APIAuthToken
from backend.models import User, Organization


class CustomBearerAuthentication(TokenAuthentication):
    keyword = "Bearer"

    def get_model(self) -> Type[APIAuthToken]:
        return APIAuthToken

    def authenticate_credentials(self, raw_key) -> tuple[User | Organization | None, APIAuthToken]:
        model = self.get_model()

        try:
            token = model.objects.get(hashed_key=model.hash_raw_key(raw_key), active=True)
        except model.DoesNotExist:
            raise AuthenticationFailed("Invalid token.")

        if token.has_expired:
            raise AuthenticationFailed("Token has expired.")

        # todo: make sure this is safe to set request.user = <Team> obj
        return token.user or token.organization, token

    # todo: override more methods + add hashing
