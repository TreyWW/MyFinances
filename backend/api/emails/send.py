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
    message = request.POST.get("message")

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


validator = Validator()
