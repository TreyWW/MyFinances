from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods

from backend.service.invoices.create.create import get_invoice_context, create_invoice_items, save_invoice
from backend.types.htmx import HtmxHttpRequest
from backend.types.requests import WebRequest


@require_http_methods(["GET", "POST"])
def create_invoice_page(request: WebRequest):
    if request.method == "POST":
        invoice_items = create_invoice_items(request)
        invoice = save_invoice(request, invoice_items)
        if not invoice:
            return render(request, "pages/invoices/create/create.html")
        return redirect("invoices:dashboard")

    context = get_invoice_context(request)
    return render(request, "pages/invoices/create/create.html", context)
