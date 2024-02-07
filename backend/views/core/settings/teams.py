from typing import Optional

from django.db.models import F, When, Case
from django.http import HttpRequest
from django.shortcuts import render

from backend.models import *
from backend.utils import Modals

Modals = Modals()


def teams_dashboard(request: HttpRequest):
    request.user: User = request.user
    user_is_logged_into_team: bool = False
    user_is_team_leader: bool = False
    users_team: Optional[Team] = None

    users_team = request.user.logged_in_as_team

    team = Team.objects.filter(id=users_team.id).annotate(
        has_members=Case(
            When(members__isnull=True, then=False),
            default=True,
            output_field=BooleanField()
        ),
        is_leader=Case(
          When(leader=request.user, then=True),
            default=False,
            output_field=BooleanField()
        )

    )

    if users_team:
        user_is_logged_into_team = True
        user_is_team_leader = True
    else:
        users_team = request.user.teams_joined.first()

        if users_team:
            user_is_logged_into_team = True


    return render(
        request,
        "pages/settings/teams/main.html",
        {
            "has_team": user_is_logged_into_team,
            "team": team,
            "is_team_leader": user_is_team_leader,
            "team_count": request.user.teams_joined.count() + request.user.teams_leader_of.count(),
        },
    )

def manage_permissions_dashboard(request: HttpRequest):
    return render(request, "pages/settings/teams/permissions.html")
