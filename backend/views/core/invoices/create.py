from datetime import datetime

from django.contrib import messages
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods

from backend.decorators import quota_usage_check
from backend.models import Invoice, InvoiceItem, Client, InvoiceProduct, QuotaUsage
from backend.utils.quota_limit_ops import quota_usage_check_under
from backend.types.htmx import HtmxHttpRequest


def invoice_page_get(request: HtmxHttpRequest):
    check_usage = quota_usage_check_under(request, "invoices-count")
    if not isinstance(check_usage, bool):
        return check_usage
    context = {
        "clients": Client.objects.filter(user=request.user),
        "existing_products": InvoiceProduct.objects.filter(user=request.user),
    }
    return render(request, "pages/invoices/create/create.html", context)


@quota_usage_check("invoices-count")
def invoice_page_post(request: HtmxHttpRequest):
    invoice_items = [
        InvoiceItem.objects.create(name=row[0], description=row[1], hours=row[2], price_per_hour=row[3])
        for row in zip(
            request.POST.getlist("service_name[]"),
            request.POST.getlist("service_description[]"),
            request.POST.getlist("hours[]"),
            request.POST.getlist("price_per_hour[]"),
        )
    ]
    currency = request.user.user_profile.currency

    invoice = Invoice(
        date_due=datetime.strptime(request.POST.get("date_due"), "%Y-%m-%d").date(),  # type: ignore[arg-type]
        date_issued=request.POST.get("date_issued"),
        currency=currency,
    )

    if request.user.logged_in_as_team:
        invoice.organization = request.user.logged_in_as_team
    else:
        invoice.user = request.user

    is_existing_client = True if request.POST.get("selected_client") else False

    if is_existing_client:
        try:
            client = Client.objects.get(user=request.user, id=request.POST.get("selected_client", ""))
        except Client.DoesNotExist:
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
        invoice.client_is_representative = True if request.POST.get("is_representative") == "on" else False

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

    QuotaUsage.create_str(request.user, "invoices-count", invoice.id)

    return redirect("invoices:dashboard")


@require_http_methods(["GET", "POST"])
def create_invoice_page(request: HtmxHttpRequest):
    if request.method == "POST":
        return invoice_page_post(request)
    return invoice_page_get(request)
