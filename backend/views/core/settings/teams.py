from django.http import HttpRequest
from django.shortcuts import render
from django.urls import reverse

from backend.decorators import *
from backend.models import *
from backend.utils import Modals
from settings.settings import EMAIL_SERVER_ENABLED, EMAIL_FROM_ADDRESS

Modals = Modals()


def teams_dashboard(request: HttpRequest):
    modal_data = []  # [Modals.create_team(), Modals.invite_user_to_team()]

    user_has_team: bool = False
    user_is_team_leader: bool = False
    users_team: Team = None

    user_team = Team.objects.filter(leader=request.user).first()
    if user_team:
        user_has_team = True
        users_team = user_team
        user_is_team_leader = True
        [
            modal_data.append(Modals.team_kick_user(usr))
            for usr in user_team.members.all()
        ]
    else:
        user_team = request.user.teams_joined.first()

        if user_team:
            user_has_team = True
            users_team = user_team

    return render(
        request,
        "pages/settings/teams/main.html",
        {
            "modal_data": modal_data,
            "has_team": user_has_team,
            "team": users_team,
            "all_teams": Team.objects.all(),
            "is_team_leader": user_is_team_leader,
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
    user_email = request.POST.get("post_email")

    if not user_email:
        messages.error(request, "No user email provided")
        return redirect("user settings teams")

    if not team:
        messages.error(
            request, "You are not in a team or you dont have permission to invite users"
        )
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


def check_team_invitation_is_valid(request, invitation, code=None):
    valid: bool = True
    if not invitation:
        messages.error(request, "Invalid Invite Code")
        # Force break early to avoid "no invitation" on invitation.code
        notification = Notification.objects.filter(
            user=request.user,
            action="redirect",
            action_value=reverse("user settings teams join", kwargs={"code": code}),
        ).first()

        if notification:
            notification.delete()
        return False

    if not invitation.is_active:
        valid = False
        messages.error(request, "Invitation has expired")

    if not valid:
        notification = Notification.objects.filter(
            user=request.user,
            action="redirect",
            action_value=reverse(
                "user settings teams join", kwargs={"code": invitation.code}
            ),
        ).first()

        if notification:
            notification.delete()
        return False

    return True


def join_team_page(request: HttpRequest, code):
    invitation: TeamInvitation = TeamInvitation.objects.filter(code=code).first()

    if not check_team_invitation_is_valid(request, invitation, code):
        return redirect("user settings teams")

    if invitation.team.members.filter(id=request.user.id).exists():
        messages.error(request, "You are already in the team")
        return redirect("user settings teams")

    team = invitation.team

    modals = [
        Modals.invited_to_team_accept(invitation),
        Modals.invited_to_team_decline(invitation),
    ]

    return render(
        request,
        "pages/settings/teams/join.html",
        {
            "invitation": invitation,
            "team": team,
            "modal_data": modals,
        },
    )


def join_team_accepted(request: HttpRequest, code):
    invitation: TeamInvitation = TeamInvitation.objects.filter(code=code).first()

    if not check_team_invitation_is_valid(request, invitation, code):
        return redirect("user settings teams")

    if request.user.teams_joined.exists():
        messages.error(
            request, "You are already in a team, please leave the team first"
        )

    invitation.team.members.add(request.user)

    notification = Notification.objects.filter(
        user=request.user,
        action="redirect",
        action_value=reverse(
            "user settings teams join", kwargs={"code": invitation.code}
        ),
    ).first()

    if notification:
        notification.delete()

    Notification.objects.create(
        user=request.user,
        message=f"You have now joined the team {invitation.team.name}",
        action="normal",
    )
    Notification.objects.create(
        user=invitation.invited_by,
        message=f"{request.user.username} has joined your team",
        action="normal",
    )

    invitation.delete()

    return redirect("user settings teams")


def join_team_declined(request: HttpRequest, code):
    invitation: TeamInvitation = TeamInvitation.objects.filter(code=code).first()
    confirmation_text = request.POST.get("confirmation_text")

    if not check_team_invitation_is_valid(request, invitation, code):
        return redirect("user settings teams")

    if confirmation_text != "i confirm i want to decline " + invitation.team.name:
        messages.error(request, "Invalid confirmation text")
        return redirect("user settings teams join", code=code)  # kwargs={"code": code})

    invitation.team.members.remove(request.user)

    Notification.objects.create(
        user=request.user,
        message=f"You have declined the team invitation",
        action="normal",
    )

    Notification.objects.create(
        user=invitation.invited_by,
        message=f"{request.user.username} has declined the team invitation",
        action="normal",
    )

    invitation.delete()
    messages.success(request, "You have successfully declined the team invitation")

    return redirect("user settings teams")


def leave_team(request: HttpRequest):
    team: Team = Team.objects.filter(leader=request.user).first()

    if team:
        messages.error(request, "You cannot leave your own team")
        return redirect("user settings teams")

    team = request.user.teams_joined.first()

    if not team:
        messages.error(request, "You are not in a team")
        return redirect("user settings teams")

    return render(request, "pages/settings/teams/leave.html")


def leave_team_confirm(request: HttpRequest):
    team: Team = Team.objects.filter(leader=request.user).first()

    if team:
        messages.error(request, "You cannot leave your own team")
        return redirect("user settings teams")

    team = request.user.teams_joined.first()

    if not team:
        messages.error(request, "You are not in a team")
        return redirect("user settings teams")

    team.members.remove(request.user)
    messages.success(request, f"You have successfully left the team {team.name}")
    return redirect("user settings teams")


def manage_permissions_dashboard(request: HttpRequest):
    return render(request, "pages/settings/teams/permissions.html")
