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
    messages.success(
        request, f"Successfully created team {name} with the ID of #{team.id}"
    )
    return render(request, "partials/messages_list.html")
