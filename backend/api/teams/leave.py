from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from backend.decorators import not_customer
from backend.models import *


@not_customer
def return_error_notif(request: HttpRequest, message: str):
    messages.error(request, message)
    resp = render(request, "partials/messages_list.html", status=200)
    resp["HX-Trigger-After-Swap"] = "leave_team_error"
    return resp


@not_customer
def leave_team_confirmed(request: HttpRequest, team_id):
    team: Team = Team.objects.filter(id=team_id).first()

    if not team:
        return return_error_notif(request, "Team not found")

    if team.leader == request.user:  # may be changed in the future. If no members allow delete
        return return_error_notif(request, "You cannot leave your own team")

    if not request.user.teams_joined.filter(id=team_id).exists():
        return return_error_notif(request, "You are not a member of this team")

    team.members.remove(request.user)
    messages.success(request, f"You have successfully left the team {team.name}")
    response = HttpResponse(request, status=200)
    response["HX-Refresh"] = "true"
    return response
