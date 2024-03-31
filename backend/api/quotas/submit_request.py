from dataclasses import dataclass
from typing import Union

from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render

from backend.models import QuotaIncreaseRequest, QuotaLimit, QuotaUsage
from backend.utils import quota_usage_check_under


def submit_request(request: HttpRequest, slug) -> HttpResponse:
    if not request.htmx:
        return redirect("quotas")

    new_value = request.POST.get("new_value")
    reason = request.POST.get("reason")

    try:
        quota_limit = QuotaLimit.objects.get(slug=slug)
    except QuotaLimit.DoesNotExist:
        return error(request, "Failed to get the quota limit type")

    check_usage = quota_usage_check_under(request, "quota_increase-request", extra_data=quota_limit.id, api=True, htmx=True)

    if not isinstance(check_usage, bool):
        return check_usage

    current = quota_limit.get_quota_limit(request.user)

    validate = validate_request(new_value, reason, current)

    if isinstance(validate, Error):
        return error(request, validate.message)

    QuotaIncreaseRequest.objects.create(
        user=request.user,
        quota_limit=quota_limit,
        new_value=new_value,
        current_value=current
    )

    QuotaUsage.create_str(request.user, "quota_increase-request", quota_limit.id)

    messages.success(request, "Successfully submitted a quota increase request")
    return render(request, "partials/messages_list.html")


@dataclass
class Error:
    message: str


def error(request: HttpRequest, message: str) -> HttpResponse:
    messages.error(request, message)
    return render(request, "partials/messages_list.html")


def validate_request(new_value, reason, current) -> Union[True, Error]:
    if not new_value:
        return Error("Please enter a valid increase value")

    try:
        new_value = int(new_value)
        if new_value <= current:
            raise ValueError
    except ValueError:
        return Error("Please enter a valid increase value that is above your current limit.")

    if len(reason) < 25:
        return Error("Please enter a valid reason for the increase.")

    return True
