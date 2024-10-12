from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import redirect, render

from backend.decorators import web_require_scopes
from backend.finance.models import Invoice, InvoiceURL
from backend.core.service.invoices.single.get_invoice import get_invoice_by_actor
from backend.core.types.htmx import HtmxHttpRequest
from backend.core.types.requests import WebRequest


@web_require_scopes("invoices:write", False, False, "finance:invoices:single:dashboard")
def manage_access(request: WebRequest, invoice_id):
    invoice_resp = get_invoice_by_actor(request.actor, invoice_id, ["invoice_urls"])
    if invoice_resp.failed:
        messages.error(request, "Invoice not found")
        return redirect("finance:invoices:single:dashboard")

    all_access_codes = invoice_resp.response.invoice_urls.values_list("uuid", "created_on").order_by("-created_on")

    return render(
        request,
        "pages/invoices/single/manage_access/manage_access.html",
        {"all_codes": all_access_codes, "invoice": invoice_resp.response},
    )


@web_require_scopes("invoices:write", False, False, "finance:invoices:single:dashboard")
def create_code(request: WebRequest, invoice_id):
    if not request.htmx:
        return redirect("finance:invoices:single:dashboard")

    if request.method != "POST":
        return HttpResponse("Invalid request", status=400)

    invoice_resp = get_invoice_by_actor(request.actor, invoice_id, ["invoice_urls"])
    if invoice_resp.failed:
        messages.error(request, "Invoice not found")
        return redirect("finance:invoices:single:dashboard")

    code = InvoiceURL.objects.create(invoice=invoice_resp.response, created_by=request.user)

    messages.success(request, "Successfully created code")

    return render(
        request,
        "pages/invoices/single/manage_access/_table_row.html",
        {"code": code.uuid, "created_on": code.created_on, "created_by": code.get_created_by, "added": True},
    )


@web_require_scopes("invoices:write", False, False, "finance:invoices:single:dashboard")
def delete_code(request: HtmxHttpRequest, code):
    if request.method != "DELETE" or not request.htmx:
        return HttpResponse("Request invalid", status=400)

    try:
        code_obj = InvoiceURL.objects.get(uuid=code)
        invoice = Invoice.objects.get(id=code_obj.invoice.id)
        if not invoice.has_access(request.user):
            raise Invoice.DoesNotExist

        # url was created by system | user cannot delete
        if not code_obj.created_by:
            raise InvoiceURL.DoesNotExist
    except (Invoice.DoesNotExist, InvoiceURL.DoesNotExist):
        messages.error(request, "Invalid URL")
        return render(request, "base/toasts.html")

    # QuotaLimit.delete_quota_usage("invoices-access_codes", request.user, invoice.id, code_obj.created_on)

    code_obj.delete()

    messages.success(request, "Successfully deleted code")
    return render(
        request,
        "pages/invoices/single/manage_access/_table_row.html",
        {},
    )
