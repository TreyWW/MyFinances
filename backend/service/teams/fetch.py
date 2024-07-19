from django.db.models import QuerySet, Q

from backend.models import Organization, User
from backend.types.requests import WebRequest


def get_all_users_teams(request: WebRequest) -> QuerySet[Organization]:
    return request.user.teams_joined.all() | request.user.teams_leader_of.all()
