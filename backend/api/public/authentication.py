from rest_framework.authentication import TokenAuthentication


class BearerAuthentication(TokenAuthentication):
    keyword = "Bearer"

    def get_model(self):
        if self.model is not None:
            return self.model
        from backend.api.public.models import APIAuthToken

        return APIAuthToken
