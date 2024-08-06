from datetime import datetime

from django.contrib import messages
from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from backend.decorators import web_require_scopes, htmx_only
from backend.models import InvoiceRecurringSet
from backend.service.boto3.scheduler.create_schedule import update_boto_schedule
from backend.service.boto3.scheduler.get import get_boto_schedule

from backend.types.requests import WebRequest


def return_create_schedule(recurring_schedule):
    recurring_schedule.schedule_name = None
    recurring_schedule.schedule_arn = None
    recurring_schedule.save(update_fields=["schedule_name", "schedule_arn"])
    update_boto_schedule.delay(recurring_schedule.pk)
    return HttpResponse("continue poll", status=200)


@require_http_methods(["GET"])
@htmx_only("invoices:recurring:dashboard")
@web_require_scopes("invoices:read", False, False, "dashboard")
def poll_recurring_schedule_update_endpoint(request: WebRequest, invoice_set_id):
    try:
        decoded_timestamp = datetime.fromtimestamp(int(request.GET.get("t", "")))
    except ValueError:
        decoded_timestamp = None

    if decoded_timestamp and decoded_timestamp < datetime.now():
        return HttpResponse("cancel poll | too long wait", status=286)

    try:
        recurring_schedule: InvoiceRecurringSet = InvoiceRecurringSet.objects.get(id=invoice_set_id)
        if not recurring_schedule.has_access(request.user):
            raise InvoiceRecurringSet.DoesNotExist()
    except InvoiceRecurringSet.DoesNotExist:
        return HttpResponseNotFound()

    if recurring_schedule.schedule_name:
        get_response = get_boto_schedule(str(recurring_schedule.schedule_name))

        if get_response.failed and get_response.error == "Schedule not found":
            return return_create_schedule(recurring_schedule)
        elif get_response.failed:
            messages.error(request, get_response.error)

        return render(
            request,
            "pages/invoices/recurring/dashboard/poll_response.html",
            {"status": recurring_schedule.status, "invoice_set_id": invoice_set_id, "invoiceSet": recurring_schedule},
            status=286,
        )

    return return_create_schedule(recurring_schedule)
