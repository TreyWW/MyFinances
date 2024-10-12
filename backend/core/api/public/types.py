from rest_framework.request import Request

from backend.core.api.public import APIAuthToken
from backend.models import User, Organization


class APIRequest(Request):
    user: User
    auth: APIAuthToken
    api_token: APIAuthToken
    team: Organization | None
    team_id: int | None
