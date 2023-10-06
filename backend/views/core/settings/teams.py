from django.contrib.sessions.models import Session
from django.http import HttpRequest
from django.shortcuts import render
from django.contrib.auth import update_session_auth_hash
from django.urls import reverse

from backend.decorators import *
from backend.models import *
from backend.utils import Modals
from settings.settings import EMAIL_SERVER_ENABLED, EMAIL_FROM_ADDRESS

Modals = Modals()


def teams_dashboard(request: HttpRequest):
    modal_data = [Modals.create_team(), Modals.invite_user_to_team()]

    user_has_team: bool = False
    users_team: Team = None

    user_team = Team.objects.filter(leader=request.user).first()
    if user_team:
        user_has_team = True
        users_team = user_team

    else:
        user_team = request.user.team_set.first()

        if user_team:
            user_has_team = True
            users_team = user_team

    return render(
        request,
        "core/pages/settings/teams/main.html",
        {
            "modal_data": modal_data,
            "has_team": user_has_team,
            "team": users_team,
            "all_teams": Team.objects.all(),
        },
    )


def create_team(request: HttpRequest):
    team_name = request.POST.get("name")

    if not team_name:
        messages.error(request, "No team name provided")
        return redirect("user settings teams")

    if Team.objects.filter(name=team_name).exists():
        messages.error(request, "Team already exists")
        return redirect("user settings teams")

    if request.user.team_set.exists():
        messages.error(request, "You are already in a team")
        return redirect("user settings teams")

    team = Team.objects.create(name=team_name, leader=request.user)

    messages.success(request, "Team created")

    return redirect("user settings teams")


def invite_user_to_team(request: HttpRequest):
    team = Team.objects.filter(leader=request.user).first()
    user_email = request.POST.get("user_email")

    if not user_email:
        messages.error(request, "No user email provided")
        return redirect("user settings teams")

    if not team:
        messages.error(request, "You are not in a team")
        return redirect("user settings teams")

    user: User = User.objects.filter(email=user_email).first()

    if not user:
        messages.error(request, "User not found")
        return redirect("user settings teams")

    if user.teams_joined.exists():
        messages.error(request, "User already in a team")
        return redirect("user settings teams")

    invitation = TeamInvitation.objects.create(
        team=team, user=user, invited_by=request.user
    )

    if EMAIL_SERVER_ENABLED and EMAIL_FROM_ADDRESS:
        SEND_SENDGRID_EMAIL(
            user.email,
            "You have been invited to join a team",
            f"""
            You have been invited to join the team {team.name}
            
            Invited by: {request.user}
            
            Click the link below to join:
            {request.build_absolute_uri(reverse("user settings teams join", args=(invitation.code,)))}
            """,
            from_email=EMAIL_FROM_ADDRESS,
        )

    Notification.objects.create(
        user=user,
        message=f"New Team Invite",
        action="redirect",
        action_value=reverse(
            "user settings teams join", kwargs={"code": invitation.code}
        ),
    )

    print(
        f"Invitation: {request.build_absolute_uri(reverse('user settings teams join', args=(invitation.code,)))}"
    )

    messages.success(request, "Invitation successfully sent")
    return redirect("user settings teams")


def join_team(request: HttpRequest, code):
    invitation: TeamInvitation = TeamInvitation.objects.filter(code=code).first()
    if not invitation:
        messages.error(request, "Invalid Invite Code")
        return redirect("user settings teams")

    if not invitation.is_active:
        messages.error(request, "Invitation has expired")
        return redirect("user settings teams")

    if invitation.team.members.filter(id=request.user.id).exists():
        messages.error(request, "You are already in the team")

    invitation.team.members.add(request.user)
