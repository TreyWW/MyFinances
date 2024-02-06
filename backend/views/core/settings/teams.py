from django.http import HttpRequest
from django.shortcuts import render

from backend.decorators import *
from backend.models import *
from backend.utils import Modals

Modals = Modals()


def teams_dashboard(request: HttpRequest):
    modal_data = []  # [Modals.create_team(), Modals.invite_user_to_team()]

    user_has_team: bool = False
    user_is_team_leader: bool = False
    users_team: Team = None

    user_team = Team.objects.filter(leader=request.user).first()
    if user_team:
        user_has_team = True
        users_team = user_team
        user_is_team_leader = True
        [
            modal_data.append(Modals.team_kick_user(usr))
            for usr in user_team.members.all()
        ]
    else:
        user_team = request.user.teams_joined.first()

        if user_team:
            user_has_team = True
            users_team = user_team

    return render(
        request,
        "pages/settings/teams/main.html",
        {
            "modal_data": modal_data,
            "has_team": user_has_team,
            "team": users_team,
            "all_teams": Team.objects.all(),
            "is_team_leader": user_is_team_leader,
        },
    )

def manage_permissions_dashboard(request: HttpRequest):
    return render(request, "pages/settings/teams/permissions.html")
