from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST

from backend.decorators import web_require_scopes
from backend.models import InvoiceRecurringSet
from backend.service.boto3.scheduler.pause import pause_boto_schedule, PauseScheduleServiceResponse
from backend.types.requests import WebRequest


@require_POST
@web_require_scopes("invoices:write", True, True)
def recurring_set_change_status_endpoint(request: WebRequest, invoice_set_id: int, status: str) -> HttpResponse:
    status = status.lower() if status else ""

    if not request.htmx:
        return redirect("invoices:recurring:dashboard")

    if status not in ["pause", "unpause"]:
        return return_message(request, "Invalid status. Please choose from: paused, ongoing, cancelled")

    try:
        invoice_set: InvoiceRecurringSet = InvoiceRecurringSet.objects.get(pk=invoice_set_id)
    except InvoiceRecurringSet.DoesNotExist:
        return return_message(request, "Recurring Invoice Set not found")

    if not invoice_set.has_access(request.actor):
        return return_message(request, "You don't have permission to make changes to this invoice.")

    if status == "pause" and invoice_set.status != "ongoing":
        return return_message(request, "Can only pause an ongoing invoice schedule")
    elif status == "unpause" and invoice_set.status != "paused":
        return return_message(request, "Can only unpause a paused invoice schedule")

    boto_response: PauseScheduleServiceResponse | None = None

    if status == "pause":
        boto_response = pause_boto_schedule(str(invoice_set.schedule_name), pause=True)
    elif status == "unpause":
        boto_response = pause_boto_schedule(str(invoice_set.schedule_name), pause=False)

    if boto_response and boto_response.failed:
        return return_message(request, boto_response.error_message, success=False)

    invoice_set.status = "ongoing" if status == "unpause" else "paused"
    invoice_set.save()

    send_message(request, f"Invoice status been changed to <strong>{status}</strong>", success=True)

    return render(request, "pages/invoices/recurring/dashboard/_modify_status.html", {"status": status, "invoice_set_id": invoice_set_id})


def return_message(request: HttpRequest, message: str, success: bool = True) -> HttpResponse:
    send_message(request, message, success)
    return render(request, "base/toasts.html")


def send_message(request: HttpRequest, message: str, success: bool = False) -> None:
    if success:
        messages.success(request, message)
    else:
        messages.error(request, message)
