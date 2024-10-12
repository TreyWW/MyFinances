from logging import exception
from typing import TypedDict

from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST
from django_ratelimit.core import is_ratelimited
from mypy_boto3_sesv2.type_defs import GetMessageInsightsResponseTypeDef, InsightsEventTypeDef

from backend.decorators import htmx_only, feature_flag_check, web_require_scopes
from backend.models import EmailSendStatus
from backend.core.types.htmx import HtmxHttpRequest
from settings.helpers import EMAIL_CLIENT


@require_POST
@htmx_only("emails:dashboard")
@feature_flag_check("areUserEmailsAllowed", status=True, api=True, htmx=True)
@web_require_scopes("emails:read", True, True)
def get_status_view(request: HtmxHttpRequest, status_id: str) -> HttpResponse:
    try:
        if request.user.logged_in_as_team:
            EMAIL_STATUS = EmailSendStatus.objects.get(organization=request.user.logged_in_as_team, id=status_id)
        else:
            EMAIL_STATUS = EmailSendStatus.objects.get(user=request.user, id=status_id)
    except EmailSendStatus.DoesNotExist:
        messages.error(request, "Status not found")
        return render(request, "base/toast.html")

    message_insight = get_message_insights(message_id=EMAIL_STATUS.aws_message_id)  # type: ignore[arg-type]

    if isinstance(message_insight, str):
        messages.error(request, message_insight)
        return render(request, "base/toast.html", {"autohide": False})

    important_info = get_important_info_from_response(message_insight)

    EMAIL_STATUS.status = important_info["status"]
    EMAIL_STATUS.updated_status_at = important_info["most_recent_event"]["Timestamp"]
    EMAIL_STATUS.save()

    messages.success(request, f"Status updated to {important_info['status']}")
    return render(request, "base/toast.html", {"autohide": False})


@require_POST
@htmx_only("emails:dashboard")
@feature_flag_check("areUserEmailsAllowed", status=True, api=True, htmx=True)
def refresh_all_statuses_view(request: HtmxHttpRequest) -> HttpResponse:
    if is_ratelimited(request, group="email-refresh_all_statuses", key="user", rate="5/10m", increment=True) or is_ratelimited(
        request, group="email-refresh_all_statuses", key="user", rate="1/m", increment=True
    ):
        messages.error(request, "Woah, slow down! Refreshing the statuses takes a while, give us a break!")
        return render(request, "base/toast.html")
    if request.user.logged_in_as_team:
        ALL_STATUSES = EmailSendStatus.objects.filter(organization=request.user.logged_in_as_team)
    else:
        ALL_STATUSES = EmailSendStatus.objects.filter(user=request.user)

    for status in ALL_STATUSES:
        response = get_message_insights(message_id=status.aws_message_id)  # type: ignore[arg-type]

        if isinstance(response, str):
            messages.error(request, response)
            continue

        important_info = get_important_info_from_response(response)

        status.status = important_info["status"]
        status.updated_status_at = important_info["most_recent_event"]["Timestamp"]

    ALL_STATUSES.bulk_update(ALL_STATUSES, fields=["status", "updated_status_at", "updated_at"])

    messages.success(request, "All statuses have been refreshed")
    http_response = HttpResponse(status=200)
    http_response["HX-Refresh"] = "true"
    return http_response


class ImportantInfo(TypedDict):
    most_recent_event: InsightsEventTypeDef
    status: str


def get_important_info_from_response(response: GetMessageInsightsResponseTypeDef) -> ImportantInfo:
    return {"most_recent_event": (most_recent_event := response["Insights"][0]["Events"][0]), "status": most_recent_event["Type"].lower()}


def get_message_insights(message_id: str) -> GetMessageInsightsResponseTypeDef | str:
    try:
        response = EMAIL_CLIENT.get_message_insights(MessageId=message_id)
        return response
    except EMAIL_CLIENT.exceptions.NotFoundException:
        return "A message was not found with this ID. Maybe wait for it to process"
    except EMAIL_CLIENT.exceptions.BadRequestException:
        return "Something went wrong when trying to fetch the email with this ID"
    except Exception as err:
        exception(err)
        return "Something went wrong when trying to fetch the email with this ID"
