from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect

from backend.decorators import feature_flag_check
from backend.models import Invoice


@feature_flag_check("isInvoiceSchedulingEnabled", True)
def view_schedules(request: HttpRequest, invoice_id) -> HttpResponse:
    try:
        invoice = Invoice.objects.prefetch_related("onetime_invoice_schedules").get(id=invoice_id, user=request.user)
    except Invoice.DoesNotExist:
        messages.error(request, "Invoice not found")
        return redirect("invoices:dashboard")

    return render(request, "pages/invoices/schedules/view.html", {
        "invoice": invoice,
        "schedules": invoice.onetime_invoice_schedules.order_by("due").only("id", "due", "status")
    })
