from django.utils.deprecation import MiddlewareMixin

from backend.api.public import APIAuthToken


class AttachTokenMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if not request.path.startswith("/api/public/"):
            return

        auth_header = request.headers.get("Authorization")

        if not (auth_header and auth_header.startswith("Bearer ")):
            request.auth = None
            return

        token_key = auth_header.split(" ")[1]
        try:
            token = APIAuthToken.objects.get(key=token_key, active=True)
            if not token.has_expired():
                request.auth = token
        except APIAuthToken.DoesNotExist:
            request.auth = None
