from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import redirect, render

from backend.decorators import quota_usage_check
from backend.models import Invoice, InvoiceURL, QuotaUsage, QuotaLimit
from backend.types.htmx import HtmxHttpRequest
from backend.utils.quota_limit_ops import quota_usage_check_under


def manage_access(request: HtmxHttpRequest, invoice_id):
    try:
        invoice = Invoice.objects.prefetch_related("invoice_urls").get(id=invoice_id, user=request.user)
    except Invoice.DoesNotExist:
        messages.error(request, "Invoice not found")
        return redirect("invoices:dashboard")

    all_access_codes = invoice.invoice_urls.values_list("uuid", "created_on").order_by("-created_on")

    return render(
        request,
        "pages/invoices/manage_access/manage_access.html",
        {"all_codes": all_access_codes, "invoice": invoice},
    )


def create_code(request: HtmxHttpRequest, invoice_id):
    if not request.htmx:
        return redirect("invoices:dashboard")

    if request.method != "POST":
        return HttpResponse("Invalid request", status=400)

    try:
        invoice = Invoice.objects.get(id=invoice_id, user=request.user)
    except Invoice.DoesNotExist:
        return HttpResponse("Invoice not found", status=400)

    limit = QuotaLimit.objects.get(slug="invoices-access_codes").get_quota_limit(user=request.user)

    current_amount = InvoiceURL.objects.filter(invoice_id=invoice_id).count()

    if current_amount >= limit:
        messages.error(request, f"You have reached the quota limit for this service 'access_codes'")
        return render(request, "partials/messages_list.html", {"autohide": False})

    code = InvoiceURL.objects.create(invoice=invoice, created_by=request.user)

    messages.success(request, "Successfully created code")

    # QuotaUsage.create_str(request.user, "invoices-access_codes", invoice_id)

    return render(
        request,
        "pages/invoices/manage_access/_table_row.html",
        {"code": code.uuid, "created_on": code.created_on, "added": True},
    )


def delete_code(request: HtmxHttpRequest, code):
    if request.method != "DELETE" or not request.htmx:
        return HttpResponse("Request invalid", status=400)

    try:
        code_obj = InvoiceURL.objects.get(uuid=code)
        invoice = Invoice.objects.get(id=code_obj.invoice.id)
        if not invoice.has_access(request.user):
            raise Invoice.DoesNotExist
    except (Invoice.DoesNotExist, InvoiceURL.DoesNotExist):
        messages.error(request, "Invalid URL")
        return render(request, "base/toasts.html")

    # QuotaLimit.delete_quota_usage("invoices-access_codes", request.user, invoice.id, code_obj.created_on)

    code_obj.delete()

    messages.success(request, "Successfully deleted code")
    return render(
        request,
        "pages/invoices/manage_access/_table_row.html",
        {},
    )
