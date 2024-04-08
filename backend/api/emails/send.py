from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List, Tuple

from collections.abc import Iterator

from django.contrib import messages
from django.core.exceptions import ValidationError
from django.core.handlers.wsgi import WSGIRequest
from django.core.validators import validate_email
from django.db.models import QuerySet
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST
from mypy_boto3_sesv2.type_defs import BulkEmailEntryResultTypeDef

from backend.decorators import feature_flag_check
from backend.decorators import htmx_only
from backend.models import Client
from backend.models import EmailSendStatus
from backend.models import QuotaLimit
from backend.models import QuotaUsage
from backend.types.emails import (
    SingleEmailInput,
    BulkEmailEmailItem,
    BulkEmailSuccessResponse,
    BulkEmailErrorResponse,
    BulkTemplatedEmailInput,
)
from backend.utils import quota_usage_check_under
from settings.helpers import send_email, send_templated_bulk_email


@dataclass
class Ok: ...


@dataclass
class Invalid:
    message: str


@require_POST
@htmx_only("emails:dashboard")
@feature_flag_check("areUserEmailsAllowed", status=True, api=True, htmx=True)
def send_single_email_view(request: WSGIRequest) -> HttpResponse:
    check_usage = quota_usage_check_under(request, "emails-single-count", api=True, htmx=True)
    if not isinstance(check_usage, bool):
        return check_usage

    return _send_single_email_view(request)


@require_POST
@htmx_only("emails:dashboard")
@feature_flag_check("areUserEmailsAllowed", status=True, api=True, htmx=True)
def send_bulk_email_view(request: WSGIRequest) -> HttpResponse:
    email_count = len(request.POST.getlist("emails"))

    check_usage = quota_usage_check_under(request, "emails-single-count", add=email_count, api=True, htmx=True)
    if not isinstance(check_usage, bool):
        return check_usage
    return _send_bulk_email_view(request)


def _send_bulk_email_view(request: WSGIRequest) -> HttpResponse:
    emails: list[str] = request.POST.getlist("emails")
    subject: str = request.POST.get("subject")
    message: str = request.POST.get("content")

    if request.user.logged_in_as_team:
        clients = Client.objects.filter(organization=request.user.logged_in_as_team, email__in=emails)
    else:
        clients = Client.objects.filter(user=request.user, email__in=emails)

    emaillist_validation = validator.email_list(emails=emails)
    if isinstance(emaillist_validation, Invalid):
        messages.error(request, emaillist_validation.message)
        return render(request, "base/toast.html")

    client_list_validation = validator.client_list(clients=clients, emails=emails)
    if isinstance(client_list_validation, Invalid):
        messages.error(request, client_list_validation.message)
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

    email_list: list[BulkEmailEmailItem] = []

    for email in emails:
        client = clients.get(email=email)
        email_list.append(
            BulkEmailEmailItem(
                destination=email,
                template_data={
                    # "subject": subject,
                    # "sender_name": request.user.first_name or request.user.email,
                    # "sender_id": request.user.id,
                    # "content_text": message,
                    # "content_html": message_single_line_html,
                    "users_name": client.name.split()[0],
                    "content_text": message.format(users_name=client.name.split()[0]),
                    "content_html": message_single_line_html.format(users_name=client.name.split()[0]),
                },
            )
        )

    EMAIL_DATA = BulkTemplatedEmailInput(
        email_list=email_list,
        template_name="user_send_client_email",
        default_template_data={
            "sender_name": request.user.first_name or request.user.email,
            "sender_id": request.user.id,
            "subject": subject,
        },
    )

    EMAIL_SENT: BulkEmailSuccessResponse | BulkEmailErrorResponse = send_templated_bulk_email(data=EMAIL_DATA)

    if isinstance(EMAIL_SENT, BulkEmailErrorResponse):
        messages.error(request, EMAIL_SENT.message)
        return render(request, "base/toast.html")

    EMAIL_RESPONSES: Iterator[tuple[BulkEmailEmailItem, BulkEmailEntryResultTypeDef]] = zip(
        EMAIL_DATA.email_list, EMAIL_SENT.response.get("BulkEmailEntryResults")
    )

    print(list(EMAIL_RESPONSES))

    if request.user.logged_in_as_team:
        SEND_STATUS_OBJECTS: QuerySet[EmailSendStatus] = EmailSendStatus.objects.bulk_create(
            [
                EmailSendStatus(
                    organization=request.user.logged_in_as_team,
                    sent_by=request.user,
                    recipient=response[0].destination,
                    aws_message_id=response[1],
                    status="pending",
                )
                for response in EMAIL_RESPONSES
            ]
        )
    else:
        SEND_STATUS_OBJECTS: QuerySet[EmailSendStatus] = EmailSendStatus.objects.bulk_create(
            [
                EmailSendStatus(
                    user=request.user,
                    sent_by=request.user,
                    recipient=response[0].destination,
                    aws_message_id=response[1].get("MessageId"),
                    status="pending",
                )
                for response in EMAIL_RESPONSES
            ]
        )

    messages.success(request, f"Successfully emailed {len(email_list)} people.")

    try:
        quota_limit = QuotaLimit.objects.get(slug="emails-single-count")
        QuotaUsage.objects.bulk_create(
            [QuotaUsage(user=request.user, quota_limit=quota_limit, extra_data=status.id) for status in SEND_STATUS_OBJECTS]
        )
    except QuotaLimit.DoesNotExist:
        ...

    return render(request, "base/toast.html")


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

    EMAIL_DATA = SingleEmailInput(
        destination=email,
        subject=subject,
        content={
            "template_name": "user_send_client_email",
            "template_data": {
                "subject": subject,
                "sender_name": request.user.first_name or request.user.email,
                "sender_id": request.user.id,
                "content_text": message,
                "content_html": message_single_line_html,
            },
        },
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

    def email_list(self, emails: list[str]) -> Ok | Invalid:
        if not emails:
            return Invalid("There was no emails provided")

        for email in emails:
            try:
                validate_email(email)
            except ValidationError:
                return Invalid(f"The email {email} is invalid.")
        return Ok()

    def client_list(self, clients: QuerySet[Client], emails: list[str]) -> Ok | Invalid:
        for email in emails:
            try:
                client = clients.get(email=email)
                if not client.email_verified:
                    return Invalid(f"Client {email} isn't yet verified so we can't send them an email yet!")
            except Client.DoesNotExist:
                return Invalid(f"Could not find client object for {email}")
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
