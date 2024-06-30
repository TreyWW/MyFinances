from rest_framework.request import Request

from backend.api.public import APIAuthToken
from backend.models import User, Team


class APIRequest(Request):
    user: User
    auth: APIAuthToken
    api_token: APIAuthToken
    team: Team | None
    team_id: int | None
