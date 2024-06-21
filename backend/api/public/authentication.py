from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed

from backend.api.public import APIAuthToken


class CustomBearerAuthentication(TokenAuthentication):
    keyword = "Bearer"

    def get_model(self):
        return APIAuthToken

    def authenticate_credentials(self, key):
        model = self.get_model()
        try:
            token = model.objects.get(key=key, active=True)
        except model.DoesNotExist:
            raise AuthenticationFailed("Invalid token.")

        if token.has_expired():
            raise AuthenticationFailed("Token has expired.")

        token.team = token.team
        return (token.user, token)

    # todo: override more methods + add hashing
