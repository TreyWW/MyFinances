from rest_framework.request import Request

from backend.models import User, Team


class APIRequest(Request):
    user: User
    team: Team | None
    team_id: int | None
