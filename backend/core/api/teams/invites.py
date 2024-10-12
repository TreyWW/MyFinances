from textwrap import dedent

from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import reverse

from backend.core.models import QuotaLimit
from backend.decorators import web_require_scopes
from backend.models import Notification, Organization, TeamInvitation, User
from backend.core.types.htmx import HtmxHttpRequest
from settings.helpers import send_email


def delete_notification(user: User, code: TeamInvitation):
    notification = Notification.objects.filter(
        user=user,
        message="New Organization Invite",
        action="modal",
        action_value="accept_invite",
        extra_type="accept_invite_with_code",
        extra_value=code,
    ).first()

    if notification:
        notification.delete()


def check_team_invitation_is_valid(request, invitation: TeamInvitation, code=None):
    valid: bool = True

    if not invitation.is_active():
        valid = False
        messages.error(request, "Invitation has expired")

    try:
        quota_limit = QuotaLimit.objects.get(slug="teams-user_count")
        if invitation.team.members.count() >= quota_limit.get_quota_limit(invitation.team.leader):
            valid = False
            messages.error(request, "Unfortunately this team is currently full")
    except QuotaLimit.DoesNotExist:
        valid = False
        messages.error(request, "Something went wrong with fetching the quota limit")

    if not valid:
        delete_notification(request.user, code)
        return False

    return True


@web_require_scopes("team:invite", True, True)
def send_user_team_invite(request: HtmxHttpRequest):
    user_email = request.POST.get("email")
    team_id = request.POST.get("team_id", "")
    team: Organization | None = Organization.objects.filter(leader=request.user, id=team_id).first()

    def return_error_notif(request: HtmxHttpRequest, message: str, autohide=None):
        messages.error(request, message)
        context = {"autohide": False} if autohide is False else {}
        resp = render(request, "partials/messages_list.html", context=context, status=200)
        resp["HX-Trigger-After-Swap"] = "invite_user_error"
        return resp

    if not user_email:
        return return_error_notif(request, "Please enter a valid user email")

    if not team:
        return return_error_notif(request, "You are not the leader of this team")

    user: User | None = User.objects.filter(email=user_email).first()

    if not user:
        return return_error_notif(request, 'User not found. Either ask them to create an account or press "Create User"')

    if user.teams_joined.filter(pk=team_id).exists():
        return return_error_notif(request, "User already is in this team")

    try:
        quota_limit = QuotaLimit.objects.get(slug="teams-user_count")
        if team.members.count() >= quota_limit.get_quota_limit(team.leader):
            return return_error_notif(
                request,
                "Unfortunately your team has reached the maximum members limit. Go to the service quotas "
                "page to request a higher number or kick some users to make space.",
                autohide=False,
            )
    except QuotaLimit.DoesNotExist:
        return return_error_notif(request, "Something went wrong with fetching the quota limit")

    invitation = TeamInvitation.objects.create(team=team, user=user, invited_by=request.user)

    Notification.objects.create(
        user=user,
        message=f"New Organization Invite",
        action="modal",
        action_value="accept_invite",
        extra_type="accept_invite_with_code",
        extra_value=invitation.code,
    )

    send_email(
        destination=user.email,
        subject="New Organization Invite",
        content=dedent(
            f"""
                Hi {user.first_name or "User"},

                {request.user.first_name or f"User {request.user.email}"} has invited you to join the organization \"{team.name}\" (#{team.id})


                Click the url below to accept the invite!
                {request.build_absolute_uri(reverse("api:teams:join accept", kwargs={"code": invitation.code}))}

                Didn't give permission to be added to this organization? You can safely ignore the email, no actions can be done on
                behalf of you without your action.
            """
        ),
    )

    messages.success(request, "Invitation successfully sent")
    response = HttpResponse(status=200)
    response["HX-Refresh"] = "true"
    return response


def accept_team_invite(request: HtmxHttpRequest, code):
    invitation: TeamInvitation | None = TeamInvitation.objects.filter(code=code).prefetch_related("team").first()

    if not invitation:
        messages.error(request, "Invalid Invite Code")
        # Force break early to avoid "no invitation" on invitation.code
        delete_notification(request.user, code)
        return render(request, "partials/messages_list.html")

    if not check_team_invitation_is_valid(request, invitation, code):
        messages.error(request, "Invalid invite - Maybe it has expired?")
        return render(request, "partials/messages_list.html")

    if request.user.teams_joined.filter(pk=invitation.team_id).exists():
        messages.error(request, "You are already in this team")
        response = render(request, "partials/messages_list.html", status=200)
        response["HX-Trigger-After-Swap"] = "accept_invite_error"
        return response

    invitation.team.members.add(request.user)

    notification = Notification.objects.filter(
        user=request.user,
        action="modal",
        action_value="accept_invite",
        extra_type="accept_invite_with_code",
        extra_value=code,
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
    response = HttpResponse(status=200)
    response["HX-Refresh"] = "true"
    return response
    # return render(request, "partials/messages_list.html")


def decline_team_invite(request: HtmxHttpRequest, code):
    invitation: TeamInvitation | None = TeamInvitation.objects.filter(code=code).first()
    confirmation_text = request.POST.get("confirmation_text")

    if not invitation:
        messages.error(request, "Invalid Invite Code")
        # Force break early to avoid "no invitation" on invitation.code
        delete_notification(request.user, code)
        return render(request, "partials/messages_list.html")

    if not check_team_invitation_is_valid(request, invitation, code):
        return render(request, "partials/messages_list.html")

    # if confirmation_text != "i confirm i want to decline " + invitation.team.name:
    #     messages.error(request, "Invalid confirmation text")
    # return redirect("teams:dashboard join", code=code)  # kwargs={"code": code})

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
