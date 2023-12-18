from django.contrib import messages
from django.http import HttpRequest
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.decorators.http import require_http_methods
from backend.models import Invoice, InvoiceItem, Client, InvoiceProduct
from datetime import datetime


def invoice_page_get(request: HttpRequest):
    context = {
        "clients": Client.objects.filter(user=request.user),
        "existing_products": InvoiceProduct.objects.filter(user=request.user),
    }
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
    ]

    invoice = Invoice.objects.create(
        user=request.user,
        date_due=datetime.strptime(request.POST.get("date_due"), "%Y-%m-%d").date(),
        date_issued=request.POST.get("date_issued"),
    )

    is_existing_client = True if request.POST.get("selected_client") else False

    if is_existing_client:
        try:
            client = Client.objects.get(
                user=request.user, id=request.POST.get("selected_client")
            )
        except:
            messages.error(request, "Client not found")
            invoice.delete()
            return render(request, "pages/invoices/create/create.html")
        invoice.client_to = client

    else:
        invoice.client_name = request.POST.get("to_name")
        invoice.client_company = request.POST.get("to_company")
        invoice.client_address = request.POST.get("to_address")
        invoice.client_city = request.POST.get("to_city")
        invoice.client_county = request.POST.get("to_county")
        invoice.client_country = request.POST.get("to_country")
        if request.POST.get("is_representative") == "on":
            invoice.client_is_representative = True
        else:
            invoice.client_is_representative = False

    invoice.self_name = request.POST.get("from_name")
    invoice.self_company = request.POST.get("from_company")
    invoice.self_address = request.POST.get("from_address")
    invoice.self_city = request.POST.get("from_city")
    invoice.self_county = request.POST.get("from_county")
    invoice.self_country = request.POST.get("from_country")

    invoice.notes = request.POST.get("notes")
    invoice.invoice_number = request.POST.get("invoice_number")
    invoice.vat_number = request.POST.get("vat_number")
    invoice.logo = request.FILES.get("logo")
    invoice.reference = request.POST.get("reference")
    invoice.sort_code = request.POST.get("sort_code")
    invoice.account_number = request.POST.get("account_number")
    invoice.account_holder_name = request.POST.get("account_holder_name")

    invoice.payment_status = invoice.dynamic_payment_status

    invoice.save()
    invoice.items.set(invoice_items)

    return redirect("invoices dashboard")


@require_http_methods(["GET", "POST"])
def create_invoice_page(request: HttpRequest):
    if request.method == "POST":
        return invoice_page_post(request)
    return invoice_page_get(request)


@require_http_methods(["GET", "POST"])
def edit_invoice_page(request: HttpRequest):
    if request.method == "POST":
        return invoice_page_post(request)
    return invoice_page_get(request)
