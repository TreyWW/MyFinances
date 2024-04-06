from __future__ import annotations

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

from backend.decorators import feature_flag_check
from backend.decorators import htmx_only
from backend.models import Client
from backend.models import QuotaLimit
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

    if bulk:
        return _send_bulk_email_view(request)
    return _send_single_email_view(request)


def _send_bulk_email_view(request: WSGIRequest) -> HttpResponse:
    return


def _send_single_email_view(request: WSGIRequest) -> HttpResponse:
    email = request.POST.get("email")
    message = request.POST.get("content")

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

    send_email(destination=email, subject="")


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

    def email_content(self, message: str, request: WSGIRequest):
        min_count = 64
        max_count = QuotaLimit.objects.get(slug="emails-email_character_count").get_quota_limit(user=request.user)

        if len(message) < min_count:
            return Invalid("The minimum character count is 64 for an email")

        if len(message) > max_count:
            return Invalid("The maximum character count is 1000 characters for an email")
        return Ok()


validator = Validator()
