from django.http import HttpRequest
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.decorators.http import require_http_methods
from backend.models import Invoice, InvoiceItem, Client


def invoice_page_get(request: HttpRequest):
    context = {}

    return render(request, "core/pages/invoices/create/create.html", context)


def invoice_page_post(request: HttpRequest):
    invoice_items = [
        InvoiceItem.objects.create(
            description=row[0], hours=row[1], price_per_hour=row[2]
        )
        for row in zip(
            request.POST.getlist("service_name[]"),
            request.POST.getlist("hours[]"),
            request.POST.getlist("price_per_hour[]"),
        )
    ]  # Todo: add products to this for logic - wtf does this mean

    invoice = Invoice.objects.create(
        user=request.user,
        date_due=request.POST.get("date_due"),
        date_issued=request.POST.get("date_issued"),
    )

    invoice.items.set(invoice_items)

    return redirect("invoices dashboard")


@require_http_methods(["GET", "POST"])
def create_invoice_page(request: HttpRequest):
    if request.method == "POST":
        return invoice_page_post(request)
    return invoice_page_get(request)
