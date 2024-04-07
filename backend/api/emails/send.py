from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Union

from django.contrib import messages
from django.core.exceptions import ValidationError
from django.core.handlers.wsgi import WSGIRequest
from django.core.validators import validate_email
from django.http import HttpRequest
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.http import require_POST
from mypy_boto3_sesv2.type_defs import GetMessageInsightsResponseTypeDef

from backend.decorators import feature_flag_check
from backend.decorators import htmx_only
from backend.models import Client
from backend.models import EmailSendStatus
from backend.models import QuotaLimit
from backend.models import QuotaUsage
from backend.utils import quota_usage_check_under
from settings.helpers import EMAIL_CLIENT
from settings.helpers import EmailInput
from settings.helpers import EmailInputTemplatedEmail
from settings.helpers import send_email


@dataclass
class Ok: ...


@dataclass
class Invalid:
    message: str


@require_POST
@htmx_only("emails:dashboard")
@feature_flag_check("areUserEmailsAllowed", status=True, api=True, htmx=True)
def send_email_view(request: WSGIRequest) -> HttpResponse:
    bulk: bool = True if request.POST.get("is_bulk") else False

    check_usage = quota_usage_check_under(request, "emails-single-count", api=True, htmx=True)
    if not isinstance(check_usage, bool):
        return check_usage

    if bulk:
        return _send_bulk_email_view(request)
    return _send_single_email_view(request)


def _send_bulk_email_view(request: WSGIRequest) -> HttpResponse:
    return


def _send_single_email_view(request: WSGIRequest) -> HttpResponse:
    email: str = str(request.POST.get("email")).strip()
    subject: str = request.POST.get("subject")
    message: str = request.POST.get("content")

    if request.user.logged_in_as_team:
        client = Client.objects.filter(organization=request.user.logged_in_as_team, email=email).first()
    else:
        client = Client.objects.filter(user=request.user, email=email).first()

    email_validation = validator.email(email, client)
    if isinstance(email_validation, Invalid):
        messages.error(request, email_validation.message)
        return render(request, "base/toast.html")

    client_validation = validator.client(client)
    if isinstance(client_validation, Invalid):
        messages.error(request, client_validation.message)
        return render(request, "base/toast.html")

    content_validation = validator.email_content(message=message, request=request)
    if isinstance(content_validation, Invalid):
        messages.error(request, content_validation.message)
        return render(request, "base/toast.html")

    subject_validation = validator.email_subject(subject=subject)
    if isinstance(subject_validation, Invalid):
        messages.error(request, subject_validation.message)
        return render(request, "base/toast.html")

    message_single_line_html = message.replace("\r\n", "<br>").replace("\n", "<br>")

    EMAIL_DATA = EmailInput(
        destination=email,
        subject=subject,
        content=EmailInputTemplatedEmail(
            template_name="user_send_client_email",
            template_data={
                "subject": subject,
                "sender_name": request.user.first_name or request.user.email,
                "sender_id": request.user.id,
                "content_text": message,
                "content_html": message_single_line_html,
            },
        ),
    )

    EMAIL_SENT = send_email(data=EMAIL_DATA)

    status_object = EmailSendStatus(sent_by=request.user, recipient=email, aws_message_id=EMAIL_SENT.response.get("MessageId"))

    if EMAIL_SENT.success:
        messages.success(request, f"Successfully emailed {email}.")
        status_object.status = "pending"
    else:
        status_object.status = "failed_to_send"
        messages.error(request, f"Failed to send the email. Error: {EMAIL_SENT.message}")

    if request.user.logged_in_as_team:
        status_object.organization = request.user.logged_in_as_team
    else:
        status_object.user = request.user

    status_object.save()

    QuotaUsage.create_str(request.user, "emails-single-count", status_object.id)

    return render(request, "base/toast.html")


def validate_bulk_email_request(request) -> Ok | Invalid: ...


class Validator:
    def email(self, email, client) -> Ok | Invalid:
        if not email:
            return Invalid("No email provided")

        try:
            validate_email(email)
        except ValidationError:
            return Invalid("Invalid email")

        if client.email != email:
            return Invalid("Something went wrong when checking the email of the client")

        return Ok()

    def client(self, client: Client) -> Ok | Invalid:
        if not client:
            return Invalid("Could not find client object")

        if not client.email_verified:
            return Invalid("The clients email has not yet been verified")
        return Ok()

    def email_subject(self, subject: str):
        min_count = 8
        max_count = 64

        if len(subject) < min_count:
            return Invalid("The minimum character count is 16 for a subject")

        if len(subject) > max_count:
            return Invalid("The maximum character count is 64 characters for a subject")

        alpha_count = len(re.findall("[a-zA-Z ]", subject))
        non_alpha_count = len(subject) - alpha_count

        if non_alpha_count > 0 and alpha_count / non_alpha_count < 10:
            return Invalid("The subject should have at least 10 letters per 'symbol'")

        return Ok()

    def email_content(self, message: str, request: WSGIRequest):
        min_count = 64
        max_count = QuotaLimit.objects.get(slug="emails-email_character_count").get_quota_limit(user=request.user)

        if len(message) < min_count:
            return Invalid("The minimum character count is 64 for an email")

        if len(message) > max_count:
            return Invalid("The maximum character count is 1000 characters for an email")
        return Ok()


validator = Validator()
