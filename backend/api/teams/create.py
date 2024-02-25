from django.http import HttpRequest
from django.shortcuts import render
from django.views.decorators.http import require_POST

from backend.decorators import *
from backend.models import Team


@require_POST
def create_team(request: HttpRequest):
    name = request.POST.get("name")

    if Team.objects.filter(name=name).exists():
        messages.error(request, "A team with this name already exists.")
        return render(request, "partials/messages_list.html")

    team = Team.objects.create(name=name, leader=request.user)
    if not request.user.logged_in_as_team:
        request.user.logged_in_as_team = team
        request.user.save()

    messages.success(request, f"Successfully created team {name} with the ID of #{team.id}")
    response = render(request, "partials/messages_list.html")
    response["HX-Refresh"] = "true"
    return response
