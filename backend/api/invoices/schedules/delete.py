from django.contrib import messages
from django.http import HttpRequest, HttpResponseForbidden
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from backend.decorators import feature_flag_check
from backend.models import InvoiceOnetimeSchedule
from infrastructure.aws.schedules.delete_schedule import delete_schedule


@require_http_methods(["DELETE", "POST"])
@feature_flag_check("isInvoiceSchedulingEnabled", True, api=True)
def cancel_onetime_schedule(request: HttpRequest, schedule_id: str):
    if not request.htmx:
        return HttpResponseForbidden()
    try:
        schedule = InvoiceOnetimeSchedule.objects.get(id=schedule_id, invoice__user=request.user)
    except InvoiceOnetimeSchedule.DoesNotExist:
        messages.error(request, "Schedule not found!")
        return render(request, "base/toasts.html")

    original_status = schedule.status
    schedule.status = InvoiceOnetimeSchedule.StatusTypes.DELETING
    schedule.save()

    delete_status: dict = delete_schedule(schedule.invoice.id, schedule.id)

    if not delete_status["success"]:
        if delete_status["error"] == "Schedule not found":
            schedule.status = InvoiceOnetimeSchedule.StatusTypes.CANCELLED
            schedule.save()

            messages.success(request, "Schedule cancelled.")
            return render(request, "pages/invoices/schedules/_table_row.html", {"schedule": schedule})
        else:
            schedule.status = original_status
            schedule.save()
            messages.error(request, f"Failed to delete schedule: {delete_status['error']}")
            return render(request, "base/toasts.html")

    schedule.status = InvoiceOnetimeSchedule.StatusTypes.CANCELLED
    schedule.save()

    messages.success(request, "Schedule cancelled.")
    return render(request, "pages/invoices/schedules/_table_row.html", {"schedule": schedule})
