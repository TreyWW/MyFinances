from django.contrib import messages
from django.shortcuts import render
from django.views.decorators.http import require_POST

from backend.decorators import has_entitlements
from backend.models import Organization, QuotaUsage
from backend.core.types.htmx import HtmxHttpRequest


@require_POST
@has_entitlements("organizations")
# @quota_usage_check("teams-count", api=True, htmx=True)
def create_team(request: HtmxHttpRequest):
    name = request.POST.get("name")

    if not name:
        messages.error(request, "A team name field must be filled.")
        return render(request, "partials/messages_list.html")

    if Organization.objects.filter(name=name).exists():
        messages.error(request, "A team with this name already exists.")
        return render(request, "partials/messages_list.html")

    team = Organization.objects.create(name=name, leader=request.user)

    QuotaUsage.create_str(request.user, "teams-count", team.id)
    QuotaUsage.create_str(request.user, "teams-joined", team.id)

    if not request.user.logged_in_as_team:
        request.user.logged_in_as_team = team
        request.user.save()

    messages.success(request, f"Successfully created team {name} with the ID of #{team.id}")
    response = render(request, "partials/messages_list.html")
    response["HX-Refresh"] = "true"
    return response
