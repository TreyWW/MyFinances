from textwrap import dedent

from django.urls import reverse
from django.utils.crypto import get_random_string

from backend.core.models import User, Organization, TeamMemberPermission
from backend.core.utils.dataclasses import BaseServiceResponse
from settings.helpers import send_email


class CreateUserServiceResponse(BaseServiceResponse[User]): ...


def create_user_service(
    request, email: str, team: Organization, first_name: str, last_name: str, permissions: list[str]
) -> CreateUserServiceResponse:

    if not first_name:
        return CreateUserServiceResponse(error_message="Please enter a valid first name")

    if not email:
        return CreateUserServiceResponse(error_message="Please enter a valid user email")

    if User.objects.filter(email=email).exists():
        return CreateUserServiceResponse(error_message="This user already exists, invite them instead!")

    temporary_password = get_random_string(length=8)

    user: User = User.objects.create_user(email=email, first_name=first_name, last_name=last_name, username=email)
    user.set_password(temporary_password)
    user.awaiting_email_verification = False
    user.require_change_password = True
    user.save()

    send_email(
        destination=email,
        subject="You have been invited to join an organization",
        content=dedent(
            f"""
                Hi {user.first_name or "User"},

                You have been invited by {request.user.email} to join the organization '{team.name}'.

                Your account email is: {email}
                Your temporary password is: {temporary_password}

                We suggest that you change your password as soon as you login, however no other user including the organization have
                access to this password.

                Upon login, you will be added to the \"{team.name}\" organization. However, if required, you may leave at any point.

                Login to your new account using this link:
                {request.build_absolute_uri(reverse("auth:login"))}

                Didn't give permission to be added to this organization? You can safely ignore the email, no actions can be done on
                behalf of you without your permission.
            """
        ),
    )

    team.members.add(user)

    TeamMemberPermission.objects.create(user=user, team=team, scopes=permissions)

    return CreateUserServiceResponse(True, response=user)
