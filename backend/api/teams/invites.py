from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.urls import reverse

from backend.decorators import *
from backend.models import Notification, Team, TeamInvitation, User
from settings.settings import EMAIL_SERVER_ENABLED, EMAIL_FROM_ADDRESS


def delete_notification(user: User, code: TeamInvitation.code):
    Notification.objects.filter(
        user=user,
        message="New Team Invite",
        action="modal",
        action_value="accept_invite",
        extra_type="accept_invite_with_code",
        extra_value=code
    ).first().delete()

def check_team_invitation_is_valid(request, invitation: TeamInvitation, code=None):
    valid: bool = True
    if not invitation:
        messages.error(request, "Invalid Invite Code")
        # Force break early to avoid "no invitation" on invitation.code
        delete_notification(request.user, code)
        return False

    if not invitation.is_active:
        valid = False
        messages.error(request, "Invitation has expired")

    if not valid:
        delete_notification(request.user, code)
        return False

    return True


def send_user_team_invite(request: HttpRequest):
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
            {request.build_absolute_uri(reverse("api:teams:join accept", kwargs={"code": invitation.code}))}
            """,
            from_email=EMAIL_FROM_ADDRESS,
        )

    Notification.objects.create(
        user=user,
        message=f"New Team Invite",
        action="modal",
        action_value="accept_invite",
        extra_type="accept_invite_with_code",
        extra_value=invitation.code
    )

    print(
        f"Invitation: {request.build_absolute_uri(reverse('api:teams:join accept', kwargs={'code': invitation.code}))}"
    )

    messages.success(request, "Invitation successfully sent")
    return redirect("user settings teams")


def accept_team_invite(request: HttpRequest, code):
    invitation: TeamInvitation = TeamInvitation.objects.filter(code=code).first()

    if not check_team_invitation_is_valid(request, invitation, code):
        messages.error(request, "Invalid invite - Maybe it has expired?")
        return render(request, "partials/messages_list.html")

    if request.user.teams_joined.exists():
        messages.error(
            request, "You are already in a team, please leave the team first"
        )
        return render(request, "partials/messages_list.html")

    invitation.team.members.add(request.user)

    notification = Notification.objects.filter(
        user=request.user,
        action="modal",
        action_value="accept_invite",
        extra_type="accept_invite_with_code",
        extra_value=code
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

    messages.success(request, f"You have successfully joined the team {invitation.team.name}")
    return HttpResponse(request, status=200) #render(request, "partials/messages_list.html")
    # return render(request, "partials/messages_list.html")


def decline_team_invite(request: HttpRequest, code):
    invitation: TeamInvitation = TeamInvitation.objects.filter(code=code).first()
    confirmation_text = request.POST.get("confirmation_text")

    if not check_team_invitation_is_valid(request, invitation, code):
        return render(request, "partials/messages_list.html")

    # if confirmation_text != "i confirm i want to decline " + invitation.team.name:
    #     messages.error(request, "Invalid confirmation text")
        # return redirect("user settings teams join", code=code)  # kwargs={"code": code})

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

    delete_notification(request.user, code)

    invitation.delete()
    messages.success(request, "You have successfully declined the team invitation")

    return render(request, "partials/messages_list.html")
