from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render

from backend.models import User, Team


def switch_team(request: HttpRequest, team_id):
    team: Team = Team.objects.filter(id=team_id).first()

    if not team:
        messages.error(request, "Team not found")
        return render(request, "partials/messages_list.html")

    if request.user.logged_in_as_team == team:
        messages.error(request, "You are already logged in for this team")
        return render(request, "partials/messages_list.html")

    if not request.user.teams_leader_of.filter(id=team_id).exists() and not request.user.teams_joined.filter(
        id=team_id).exists():
        messages.error(request, "You are not a member of this team")
        return render(request, "partials/messages_list.html")

    messages.success(request, f"Now signing in for {team.name}")
    request.user.logged_in_as_team = team
    request.user.save()
    return render(request, "components/+logged_in_for.html")