from textwrap import dedent

from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.urls import reverse

from backend.models import User
from backend.templatetags.feature_enabled import feature_enabled
from backend.utils.dataclasses import BaseServiceResponse
from backend.views.core.auth.verify import create_magic_link
from settings.helpers import send_email


class SendMagicLinkServiceResponse(BaseServiceResponse[str]): ...


def send_magic_link_service(request, user: User) -> SendMagicLinkServiceResponse:
    magic_link, plain_token = create_magic_link(user, service="login")

    magic_link_url = request.build_absolute_uri(
        reverse("auth:login magic_link verify", kwargs={"uuid": str(magic_link.uuid), "token": plain_token})
    )

    send_email(
        destination=user.email,
        subject="Login Request",
        content=dedent(
            f"""
                Hi {user.first_name if user.first_name else "User"},

                A login request was made on your MyFinances account. If this was not you, please ignore
                this email.

                If you would like to login, please use the following link: \n {magic_link_url}
            """
        ),
    )
