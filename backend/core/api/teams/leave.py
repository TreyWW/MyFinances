from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import render

from backend.models import Organization
from backend.core.types.htmx import HtmxHttpRequest


def return_error_notif(request: HtmxHttpRequest, message: str):
    messages.error(request, message)
    resp = render(request, "partials/messages_list.html", status=200)
    resp["HX-Trigger-After-Swap"] = "leave_team_error"
    return resp


def leave_team_confirmed(request: HtmxHttpRequest, team_id):
    team: Organization | None = Organization.objects.filter(id=team_id).first()

    if not team:
        return return_error_notif(request, "Team not found")

    if team.leader == request.user:  # may be changed in the future. If no members allow delete
        return return_error_notif(request, "You cannot leave your own team")

    if request.user.teams_joined.filter(id=team_id).exists():
        team.members.remove(request.user)
        messages.success(request, f"You have successfully left the team {team.name}")
        response = HttpResponse(status=200)
        response["HX-Refresh"] = "true"
        return response
    else:
        return return_error_notif(request, "You are not a member of this team")
