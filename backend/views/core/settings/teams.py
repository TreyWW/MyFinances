from django.contrib.sessions.models import Session
from django.http import HttpRequest
from django.shortcuts import render
from django.contrib.auth import update_session_auth_hash

from backend.decorators import *
from backend.models import *
from backend.utils import Modals

Modals = Modals()


def teams_dashboard(request: HttpRequest):
    modal_data = [Modals.create_team(), Modals.invite_user_to_team()]

    user_has_team: bool = False
    users_team: Team = None

    user_team = Team.objects.filter(leader=request.user).first()
    if user_team:
        user_has_team = True
        users_team = user_team

    else:
        user_team = request.user.team_set.first()

        if user_team:
            user_has_team = True
            users_team = user_team

    return render(
        request,
        "core/pages/settings/teams/main.html",
        {
            "modal_data": modal_data,
            "has_team": user_has_team,
            "team": users_team,
            "all_teams": Team.objects.all(),
        },
    )


def create_team(request: HttpRequest):
    team_name = request.POST.get("name")

    if not team_name:
        messages.error(request, "No team name provided")
        return redirect("user settings teams")

    if Team.objects.filter(name=team_name).exists():
        messages.error(request, "Team already exists")
        return redirect("user settings teams")

    if request.user.team_set.exists():
        messages.error(request, "You are already in a team")
        return redirect("user settings teams")

    team = Team.objects.create(name=team_name, leader=request.user)

    messages.success(request, "Team created")

    return redirect("user settings teams")
