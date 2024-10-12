from dataclasses import dataclass
from typing import Union

from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from backend.decorators import superuser_only
from backend.models import QuotaIncreaseRequest, QuotaLimit, QuotaUsage, QuotaOverrides
from backend.core.types.htmx import HtmxHttpRequest


# from backend.utils.quota_limit_ops import quota_usage_check_under


def submit_request(request: HtmxHttpRequest, slug) -> HttpResponse:
    if not request.htmx:
        return redirect("quotas")

    new_value = request.POST.get("new_value", "")
    reason = request.POST.get("reason", "")

    try:
        quota_limit = QuotaLimit.objects.get(slug=slug)
    except QuotaLimit.DoesNotExist:
        return error(request, "Failed to get the quota limit type")

    # usage_per_item = quota_usage_check_under(request, "quota_increase-request", extra_data=quota_limit.id, api=True, htmx=True)
    # usage_per_month = quota_usage_check_under(
    #     request, "quota_increase-requests_per_month_per_quota", extra_data=quota_limit.id, api=True, htmx=True
    # )

    # if not isinstance(usage_per_item, bool):
    #     return usage_per_item

    # if not isinstance(usage_per_month, bool):
    #     return usage_per_month

    current = quota_limit.get_quota_limit(request.user)

    validate = validate_request(new_value, reason, current)

    if isinstance(validate, Error):
        return error(request, validate.message)

    quota_increase_request = QuotaIncreaseRequest.objects.create(
        user=request.user, quota_limit=quota_limit, new_value=new_value, current_value=current, reason=reason
    )

    QuotaUsage.create_str(request.user, "quota_increase-request", quota_increase_request.id)
    QuotaUsage.create_str(request.user, "quota_increase-requests_per_month_per_quota", quota_limit.id)

    messages.success(request, "Successfully submitted a quota increase request")
    return render(request, "base/toast.html")


@dataclass
class Error:
    message: str


def error(request: HtmxHttpRequest, message: str) -> HttpResponse:
    messages.error(request, message)
    return render(request, "partials/messages_list.html")


def validate_request(new_value, reason, current) -> Union[bool, Error]:
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


@superuser_only
@require_http_methods(["DELETE", "POST"])
def approve_request(request: HtmxHttpRequest, request_id) -> HttpResponse:
    if not request.htmx:
        return redirect("quotas")
    try:
        quota_request = QuotaIncreaseRequest.objects.get(id=request_id)
    except QuotaIncreaseRequest.DoesNotExist:
        return error(request, "Failed to get the quota increase request")

    try:
        quota_override_existing = QuotaOverrides.objects.get(user=quota_request.user, quota_limit=quota_request.quota_limit)
        quota_override_existing.value = quota_request.new_value
        quota_override_existing.save()
    except QuotaOverrides.DoesNotExist:
        QuotaOverrides.objects.create(
            user=quota_request.user,
            value=quota_request.new_value,
            quota_limit=quota_request.quota_limit,
        )

    quota_limit_for_increase = QuotaLimit.objects.get(slug="quota_increase-request")
    QuotaUsage.objects.filter(user=quota_request.user, quota_limit=quota_limit_for_increase, extra_data=quota_request.id).delete()
    quota_request.status = "approved"
    quota_request.save()

    try:
        QuotaUsage.objects.get(
            quota_limit=QuotaLimit.objects.get(slug="quota_increase-requests_per_month_per_quota"), extra_data=quota_request.quota_limit_id
        ).delete()
    except QuotaUsage.DoesNotExist:
        ...

    return HttpResponse(status=200)


@superuser_only
@require_http_methods(["DELETE", "POST"])
def decline_request(request: HtmxHttpRequest, request_id) -> HttpResponse:
    if not request.htmx:
        return redirect("quotas")
    try:
        quota_request = QuotaIncreaseRequest.objects.get(id=request_id)
    except QuotaIncreaseRequest.DoesNotExist:
        return error(request, "Failed to get the quota increase request")

    quota_limit_for_increase = QuotaLimit.objects.get(slug="quota_increase-request")
    QuotaUsage.objects.filter(user=quota_request.user, quota_limit=quota_limit_for_increase, extra_data=quota_request.id).delete()
    quota_request.status = "decline"
    quota_request.save()

    return HttpResponse(status=200)
