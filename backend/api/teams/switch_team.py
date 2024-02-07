from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from backend.models import Team


def switch_team(request: HttpRequest, team_id):
    if not team_id:
        if not request.user.logged_in_as_team:
            messages.error(request, "You are not logged into an organization")
        request.user.logged_in_as_team = None
        request.user.save()
        messages.success(request, "You are now logged into your personal account")
        return render(request, "components/+logged_in_for.html")

    team: Team = Team.objects.filter(id=team_id).first()

    if not team:
        messages.error(request, "Team not found")
        return render(request, "partials/messages_list.html")

    if request.user.logged_in_as_team == team:
        messages.error(request, "You are already logged in for this team")
        return render(request, "partials/messages_list.html")

    if (
        not request.user.teams_leader_of.filter(id=team_id).exists()
        and not request.user.teams_joined.filter(id=team_id).exists()
    ):
        messages.error(request, "You are not a member of this team")
        return render(request, "partials/messages_list.html")

    messages.success(request, f"Now signing in for {team.name}")
    request.user.logged_in_as_team = team
    request.user.save()
    response = HttpResponse(request, status=200)
    response["HX-Refresh"] = "true"
    return response
    # return render(request, "components/+logged_in_for.html")


def get_dropdown(request: HttpRequest):
    if not request.htmx:
        return HttpResponse("Invalid Request", status=405)

    return render(request, "base/topbar/_organizations_list.html")
