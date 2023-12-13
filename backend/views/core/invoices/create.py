from django.http import HttpRequest
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.decorators.http import require_http_methods
from backend.models import Invoice, InvoiceItem, Client
from datetime import datetime


def invoice_page_get(request: HttpRequest):
    context = {}

    return render(request, "pages/invoices/create/create.html", context)


def invoice_page_post(request: HttpRequest):
    invoice_items = [
        InvoiceItem.objects.create(
            name=row[0], description=row[1], hours=row[2], price_per_hour=row[3]
        )
        for row in zip(
            request.POST.getlist("service_name[]"),
            request.POST.getlist("service_description[]"),
            request.POST.getlist("hours[]"),
            request.POST.getlist("price_per_hour[]"),
        )
    ]  # TODO: add products to this for logic (so that they can be loaded without manually making each time)

    invoice = Invoice.objects.create(
        user=request.user,
        date_due=datetime.strptime(request.POST.get("date_due"), "%Y-%m-%d").date(),
        date_issued=request.POST.get("date_issued"),
        client_name=request.POST.get("to_name"),
        client_company=request.POST.get("to_company"),
        client_address=request.POST.get("to_address"),
        client_city=request.POST.get("to_city"),
        client_county=request.POST.get("to_county"),
        client_country=request.POST.get("to_country"),
        self_name=request.POST.get("from_name"),
        self_company=request.POST.get("from_company"),
        self_address=request.POST.get("from_address"),
        self_city=request.POST.get("from_city"),
        self_county=request.POST.get("from_county"),
        self_country=request.POST.get("from_country"),
        notes=request.POST.get("notes"),
        invoice_number=request.POST.get("invoice_number"),
        vat_number=request.POST.get("vat_number"),
        # logo = request.POST.get("logo"),
        reference=request.POST.get("reference"),
        sort_code=request.POST.get("sort_code"),
        account_number=request.POST.get("account_number"),
        account_holder_name=request.POST.get("account_holder_name"),
    )

    invoice.payment_status = invoice.dynamic_payment_status
    print(invoice.date_due)
    invoice.save()
    invoice.items.set(invoice_items)

    return redirect("invoices dashboard")
    
@require_http_methods(["GET", "POST"])
def create_invoice_page(request: HttpRequest):
    if request.method == "POST":
        return invoice_page_post(request)
    return invoice_page_get(request)
