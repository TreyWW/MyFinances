from django.contrib import messages
from django.shortcuts import render
from django.urls import reverse
from django.utils.crypto import get_random_string

from backend.decorators import web_require_scopes
from backend.models import Organization, User, TeamMemberPermission
from backend.service.permissions.scopes import get_permissions_from_request
from backend.types.emails import SingleEmailInput
from backend.types.requests import WebRequest
from settings.helpers import send_email


@web_require_scopes("team:invite", True, True)
def create_user_view(request: WebRequest):
    team_id = request.POST.get("team_id", "")

    team: Organization | None = Organization.objects.filter(id=team_id).first()

    if not team:
        messages.error("This team does not exist")
        return render(request, "base/toast.html")

    if not team.is_owner(request.user):
        messages.error(request, "Only the team owner can create users")
        return render(request, "base/toast.html")

    first_name = request.POST.get("first_name", "")
    last_name = request.POST.get("last_name", "")
    email = request.POST.get("email", "")
    permissions: list = get_permissions_from_request(request)

    if not email:
        messages.error(request, "Please enter a valid user email")
        return render(request, "base/toast.html")

    if User.objects.filter(email=email).exists():
        messages.error(request, "This user already exists, invite them instead!")
        return render(request, "base/toast.html")

    temporary_password = get_random_string(length=8)

    user: User = User.objects.create_user(email=email, first_name=first_name, last_name=last_name, username=email)
    user.set_password(temporary_password)
    user.awaiting_email_verification = False
    user.save()

    send_email(
        SingleEmailInput(
            destination=email,
            subject="MyFinances | You have been invited to join an organization",
            content=f"""
                Hi {user.first_name or "User"},

                You have been invited by {request.user.email} to join the organization {team.name}.

                Your account email is: {email}
                Your temporary password is: {temporary_password}

                We suggest that you change your password as soon as you login, however no other user including the organization have
                access to this password.

                Upon login, you will be added to the \"{team.name}\" organization. However, if required, you may leave at any point.

                Login to your new account using this link:
                {request.build_absolute_uri(reverse("auth:login manual"))}
            """,
        )
    )

    team.members.add(user)

    TeamMemberPermission.objects.create(user=user, team=team, scopes=permissions)

    messages.success(request, "User was created successfully. They have been emailed instructions.")
    return render(request, "base/toast.html")
