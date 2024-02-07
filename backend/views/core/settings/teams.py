from typing import Optional

from django.http import HttpRequest
from django.shortcuts import render

from backend.models import *
from backend.utils import Modals

Modals = Modals()


def teams_dashboard(request: HttpRequest):
    user_is_logged_into_team: bool = False
    user_is_team_leader: bool = False
    users_team: Optional[Team] = None

    users_team = request.user.logged_in_as_team

    if users_team:
        user_is_logged_into_team = True
        user_is_team_leader = True
    else:
        users_team = request.user.teams_joined.first()

        if users_team:
            user_is_logged_into_team = True

    print(users_team)
    return render(
        request,
        "pages/settings/teams/main.html",
        {
            "has_team": user_is_logged_into_team,
            "team": users_team,
            "is_team_leader": user_is_team_leader,
            "team_count": request.user.teams_joined.count() + request.user.teams_leader_of.count(),
        },
    )

def manage_permissions_dashboard(request: HttpRequest):
    return render(request, "pages/settings/teams/permissions.html")
