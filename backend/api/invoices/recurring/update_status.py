from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST

from backend.decorators import web_require_scopes
from backend.models import InvoiceRecurringProfile
from backend.service.asyn_tasks.tasks import Task
from backend.service.boto3.scheduler.create_schedule import create_boto_schedule
from backend.service.boto3.scheduler.get import get_boto_schedule, GetScheduleServiceResponse
from backend.service.boto3.scheduler.pause import pause_boto_schedule, PauseScheduleServiceResponse
from backend.types.requests import WebRequest

from datetime import timedelta, datetime
from typing import Optional


@require_POST
@web_require_scopes("invoices:write", True, True)
def recurring_profile_change_status_endpoint(request: WebRequest, invoice_set_id: int, status: str) -> HttpResponse:
    status = status.lower() if status else ""

    if not request.htmx:
        return redirect("invoices:recurring:dashboard")

    if status not in ["pause", "unpause", "refresh"]:
        return return_message(request, "Invalid status. Please choose from: paused, ongoing, refresh")

    try:
        invoice_set: InvoiceRecurringProfile = InvoiceRecurringProfile.objects.get(pk=invoice_set_id, active=True)
    except InvoiceRecurringProfile.DoesNotExist:
        return return_message(request, "Recurring Invoice Set not found")

    if not invoice_set.has_access(request.user):
        return return_message(request, "You don't have permission to make changes to this invoice.")

    if status == "pause" and invoice_set.status != "ongoing":
        return return_message(request, "Can only pause an ongoing invoice schedule")
    elif status == "unpause" and invoice_set.status != "paused":
        return return_message(request, "Can only unpause a paused invoice schedule")

    if status == "refresh":
        print("using refresh")
        if invoice_set.boto_schedule_uuid:
            boto_get_response = get_boto_schedule(str(invoice_set.boto_schedule_uuid))

            if boto_get_response.failed:
                print("TASK 1 - no schedule found, let's create one")
                Task().queue_task(create_boto_schedule, invoice_set.pk)
                return render(request, "pages/invoices/recurring/dashboard/poll_update.html", {"invoice_set_id": invoice_set_id})

            invoice_set.status = "ongoing" if boto_get_response.response["State"] == "ENABLED" else "paused"
            invoice_set.save(update_fields=["status"])
        else:
            Task().queue_task(create_boto_schedule, invoice_set.pk)
            return render(request, "pages/invoices/recurring/dashboard/poll_update.html", {"invoice_set_id": invoice_set_id})
        send_message(request, f"Invoice status has been refreshed!", success=True)
    else:
        if status == "pause":
            Task().queue_task(pause_boto_schedule, str(invoice_set.boto_schedule_uuid), pause=True)
        elif status == "unpause":
            Task().queue_task(pause_boto_schedule, str(invoice_set.boto_schedule_uuid), pause=False)

        new_status = "ongoing" if status == "unpause" else "paused"

        invoice_set.status = new_status
        invoice_set.save(update_fields=["status"])

        send_message(request, f"Invoice status been changed to <strong>{new_status}</strong>", success=True)

    # poll time stamp (now + 15 seconds) as dateTtime

    poll_end_timestamp_unix = int((datetime.now() + timedelta(seconds=15)).timestamp())

    return render(
        request,
        "pages/invoices/recurring/dashboard/_modify_status.html",
        {"status": status, "invoice_set_id": invoice_set_id, "poll_end_timestamp": poll_end_timestamp_unix},
    )


def return_message(request: HttpRequest, message: str, success: bool = True) -> HttpResponse:
    send_message(request, message, success)
    return render(request, "base/toasts.html")


def send_message(request: HttpRequest, message: str, success: bool = False) -> None:
    if success:
        messages.success(request, message)
    else:
        messages.error(request, message)
