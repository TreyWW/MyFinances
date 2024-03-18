from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django_ratelimit.core import is_ratelimited

from backend.decorators import feature_flag_check
from backend.models import Invoice
from infrastructure.aws.schedules.create_schedule import (
    create_onetime_schedule,
    CreateOnetimeScheduleInputData,
    SuccessResponse as CreateOnetimeScheduleSuccessResponse,
)


@csrf_exempt
@feature_flag_check("isInvoiceSchedulingEnabled", True, api=True)
def create_schedule(request: HttpRequest):
    option = request.POST.get("option")  # 1=one time 2=recurring

    if option in ["1", "one-time", "onetime", "one"]:
        ratelimited = (
            is_ratelimited(request, group="create_schedule", key="user", rate="2/30s", increment=True)
            or is_ratelimited(request, group="create_schedule", key="user", rate="5/m", increment=True)
            or is_ratelimited(request, group="create_schedule", key="ip", rate="5/m", increment=True)
            or is_ratelimited(request, group="create_schedule", key="ip", rate="10/h", increment=True)
        )

        if ratelimited:
            messages.error(request, "Woah, slow down!")
            return render(request, "base/toasts.html")
        return create_ots(request)

    messages.error(request, "Invalid option. Something went wrong.")
    return render(request, "base/toasts.html")


def create_ots(request: HttpRequest) -> HttpResponse:
    invoice_id = request.POST.get("invoice_id") or request.POST.get("invoice")

    try:
        invoice = Invoice.objects.get(id=invoice_id)
    except Invoice.DoesNotExist:
        messages.error(request, "Invoice not found")
        return render(request, "base/toasts.html")

    if (request.user.logged_in_as_team and invoice.organization != request.user.logged_in_as_team) or (
        not request.user.logged_in_as_team and invoice.user != request.user
    ):
        messages.error(request, "You do not have permission to create schedules for this invoice")
        return render(request, "base/toasts.html")

    print("[BACKEND] About to create ots", flush=True)
    schedule = create_onetime_schedule(
        CreateOnetimeScheduleInputData(
            invoice=invoice, option=1, datetime=request.POST.get("date_time"), email_type=request.POST.get("email_type")
        )
    )

    print(schedule, flush=True)

    if isinstance(schedule, CreateOnetimeScheduleSuccessResponse):
        messages.success(request, "Schedule created!")
        return render(request, "pages/invoices/schedules/_table_row.html", {"schedule": schedule.schedule})

    messages.error(request, schedule.message)
    return render(request, "base/toasts.html")
