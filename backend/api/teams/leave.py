from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.urls import reverse

from backend.decorators import *
from backend.models import *


def leave_team_confirmed(request: HttpRequest, team_id):
    team: Team = Team.objects.filter(id=team_id).first()

    if not team:
        messages.error(request, "Team not found")
        return render(request, "partials/messages_list.html")

    if team.leader == request.user:  # may be changed in the future. If no members allow delete
        messages.error(request, "You cannot leave your own team")
        return render(request, "partials/messages_list.html")

    if not request.user.teams_joined.filter(id=team_id).exists():
        messages.error(request, "You are not in this team.")
        return render(request, "partials/messages_list.html")

    team.members.remove(request.user)
    messages.success(request, f"You have successfully left the team {team.name}")
    return HttpResponse(request, status=200) #render(request, "partials/messages_list.html")
