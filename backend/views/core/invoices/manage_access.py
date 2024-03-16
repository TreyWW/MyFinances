from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render

from backend.models import Invoice, InvoiceURL


def manage_access(request: HttpRequest, invoice_id):
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


def create_code(request: HttpRequest, invoice_id):
    if not request.htmx:
        return redirect("invoices:dashboard")

    if request.method != "POST":
        return HttpResponse("Invalid request", status=400)

    try:
        invoice = Invoice.objects.get(id=invoice_id, user=request.user)
    except Invoice.DoesNotExist:
        return HttpResponse("Invoice not found", status=400)

    code = InvoiceURL.objects.create(invoice=invoice, created_by=request.user)

    messages.success(request, "Successfully created code")
    return render(
        request,
        "pages/invoices/manage_access/_table_row.html",
        {"code": code.uuid, "created_on": code.created_on, "added": True},
    )


def delete_code(request: HttpRequest, code):
    if request.method != "DELETE" or not request.htmx:
        return HttpResponse("Request invalid", status=400)

    try:
        code_obj = InvoiceURL.objects.get(uuid=code)
        invoice = Invoice.objects.get(id=code_obj.invoice.id, user=request.user)
    except (Invoice.DoesNotExist, InvoiceURL.DoesNotExist):
        return redirect("invoices:dashboard")

    code_obj.delete()

    # return HttpResponse("", status=200)
    messages.success(request, "Successfully deleted code")
    return render(
        request,
        "pages/invoices/manage_access/_table_row.html",
        {},
    )
