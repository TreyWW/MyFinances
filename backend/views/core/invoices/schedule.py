from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import render, redirect

from backend.decorators import feature_flag_check
from backend.models import Invoice, QuotaLimit
from backend.types.htmx import HtmxHttpRequest


@feature_flag_check("isInvoiceSchedulingEnabled", True)
def view_schedules(request: HtmxHttpRequest, invoice_id) -> HttpResponse:
    context: dict = {}
    try:
        invoice = Invoice.objects.prefetch_related("onetime_invoice_schedules").get(id=invoice_id, user=request.user)
        context["invoice"] = invoice
    except Invoice.DoesNotExist:
        messages.error(request, "Invoice not found")
        return redirect("invoices:dashboard")

    context["schedules"] = invoice.onetime_invoice_schedules.order_by("due").only("id", "due", "status")

    quota_limit = QuotaLimit.objects.get(slug="invoices-schedules")

    if quota_limit.strict_goes_above_limit(request.user):
        context["quota_breached"] = True

    return render(
        request,
        "pages/invoices/schedules/view.html",
        context,
    )
