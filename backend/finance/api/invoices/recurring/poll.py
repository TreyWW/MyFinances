from datetime import datetime

from django.contrib import messages
from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from backend.decorators import web_require_scopes, htmx_only
from backend.finance.models import InvoiceRecurringProfile
from backend.core.service.asyn_tasks.tasks import Task
from backend.core.service.boto3.scheduler.create_schedule import create_boto_schedule
from backend.core.service.boto3.scheduler.get import get_boto_schedule

from backend.core.types.requests import WebRequest


def return_create_schedule(recurring_schedule):
    recurring_schedule.boto_schedule_uuid = None
    recurring_schedule.boto_schedule_arn = None
    recurring_schedule.save(update_fields=["boto_schedule_uuid", "boto_schedule_arn"])
    Task().queue_task(create_boto_schedule, recurring_schedule.pk)
    return HttpResponse("continue poll", status=200)


@require_http_methods(["GET"])
@htmx_only("finance:invoices:recurring:dashboard")
@web_require_scopes("invoices:read", False, False, "dashboard")
def poll_recurring_schedule_update_endpoint(request: WebRequest, invoice_profile_id):
    try:
        decoded_timestamp = datetime.fromtimestamp(int(request.GET.get("t", "")))
    except ValueError:
        decoded_timestamp = None

    if decoded_timestamp and decoded_timestamp < datetime.now():
        return HttpResponse("cancel poll | too long wait", status=286)

    try:
        recurring_schedule: InvoiceRecurringProfile = InvoiceRecurringProfile.objects.get(id=invoice_profile_id, active=True)
        if not recurring_schedule.has_access(request.user):
            raise InvoiceRecurringProfile.DoesNotExist()
    except InvoiceRecurringProfile.DoesNotExist:
        return HttpResponseNotFound()

    if recurring_schedule.boto_schedule_uuid:
        get_response = get_boto_schedule(str(recurring_schedule.boto_schedule_uuid))

        if get_response.failed and get_response.error == "Schedule not found":
            return return_create_schedule(recurring_schedule)
        elif get_response.failed:
            messages.error(request, get_response.error)

        return render(
            request,
            "pages/invoices/recurring/dashboard/poll_response.html",
            {"status": recurring_schedule.status, "invoice_profile_id": invoice_profile_id, "invoiceProfile": recurring_schedule},
            status=286,
        )

    return return_create_schedule(recurring_schedule)
