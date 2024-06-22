from django.utils.deprecation import MiddlewareMixin
from rest_framework.response import Response

from backend.api.public import APIAuthToken
from backend.models import Team


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


class HandleTeamContextMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if not request.path.startswith("/api/public/"):
            return

        if hasattr(request, "query_params"):
            team_id = request.query_params.get("team_id")
        else:
            team_id = request.GET.get("team_id")
        request.team = None
        request.team_id = team_id

        if not team_id:
            # No team_id provided, proceed with user context
            return

        team = Team.objects.filter(id=team_id).first()

        request.team = team
