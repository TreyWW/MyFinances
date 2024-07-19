from typing import Optional

from django.db.models import When, Case, BooleanField
from django.shortcuts import render

from backend.models import *
from backend.service.teams.fetch import get_all_users_teams
from backend.types.requests import WebRequest


def teams_dashboard(request: WebRequest):
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
            .prefetch_related("members")
            .get(id=users_team.id)
        )

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
        context | {"team": team},
    )


def login_to_team_page(request: WebRequest, all_teams: QuerySet[Organization]):
    print(all_teams)
    return render(request, "pages/settings/teams/login_to_team.html", {"team_list": all_teams})


def teams_dashboard_handler(request: WebRequest):
    all_teams: QuerySet[Organization] = get_all_users_teams(request)
    logged_in_team: Organization | None = request.user.logged_in_as_team

    if not logged_in_team:
        return login_to_team_page(request, all_teams)
    return teams_dashboard(request)
