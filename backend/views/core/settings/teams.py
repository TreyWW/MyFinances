from typing import Optional

from django.db.models import When, Case, BooleanField, Prefetch, Subquery, OuterRef
from django.http import HttpRequest
from django.shortcuts import render

from backend.models import *
from backend.types.htmx import HtmxHttpRequest


def teams_dashboard(request: HtmxHttpRequest):
    context: dict[str, str | int] = {}

    users_team: Optional[Organization] = request.user.logged_in_as_team

    if not users_team:
        user_with_counts = User.objects.prefetch_related("teams_joined", "teams_leader_of").get(pk=request.user.pk)
        return render(
            request,
            "pages/settings/teams/main.html",
            context
            | {
                "team": None,
                "team_count": user_with_counts.teams_joined.count() + user_with_counts.teams_leader_of.count(),
            },
        )

    try:
        team = (
            Organization.objects.annotate(
                is_leader=Case(
                    When(leader=request.user, then=True),
                    default=False,
                    output_field=BooleanField(),
                ),
            )
            .prefetch_related("members", "permissions")
            .get(id=users_team.id)
        )
        user_permissions = {
            member: list(team.permissions.filter(user=member).values_list("scopes", flat=True))[0] for member in team.members.all()
        }

    except Organization.DoesNotExist:
        user_with_counts = User.objects.prefetch_related("teams_joined", "teams_leader_of").get(pk=request.user.pk)
        return render(
            request,
            "pages/settings/teams/main.html",
            context
            | {
                "team": None,
                "team_count": user_with_counts.teams_joined.count() + user_with_counts.teams_leader_of.count(),
            },
        )

    return render(
        request,
        "pages/settings/teams/main.html",
        context | {"team": team, "user_permissions": user_permissions},
    )


def manage_permissions_dashboard(request: HttpRequest):
    return render(request, "pages/settings/teams/permissions.html")
