from django.contrib import messages

from backend.models import Invoice, InvoiceRecurringProfile, InvoiceItem, Client, QuotaUsage, DefaultValues
from backend.core.service.defaults.get import get_account_defaults
from backend.core.types.requests import WebRequest


def create_invoice_items(request: WebRequest):
    return [
        InvoiceItem.objects.create(name=row[0], description=row[1], hours=row[2], price_per_hour=row[3])
        for row in zip(
            request.POST.getlist("service_name[]"),
            request.POST.getlist("service_description[]"),
            request.POST.getlist("hours[]"),
            request.POST.getlist("price_per_hour[]"),
        )
    ]


def save_invoice_common(request: WebRequest, invoice_items, invoice: Invoice | InvoiceRecurringProfile):
    if request.user.logged_in_as_team:
        invoice.organization = request.user.logged_in_as_team
    else:
        invoice.user = request.user

    if request.POST.get("selected_client"):
        try:
            client = Client.filter_by_owner(request.actor).get(id=request.POST.get("selected_client"))
            invoice.client_to = client
        except Client.DoesNotExist:
            messages.error(request, "Client not found")
            invoice.delete()
            return None
    else:
        invoice.client_name = request.POST.get("to_name")
        invoice.client_company = request.POST.get("to_company")
        invoice.client_email = request.POST.get("to_email")
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
    invoice.vat_number = request.POST.get("vat_number")
    if request.FILES.get("logo") is not None:
        invoice.logo = request.FILES.get("logo")
    else:
        if invoice.client_to is not None and invoice.client_to.default_values.default_invoice_logo:
            invoice.logo = invoice.client_to.default_values.default_invoice_logo
        else:
            defaults: DefaultValues = get_account_defaults(request.actor)
            if defaults:
                invoice.logo = defaults.default_invoice_logo
    invoice.sort_code = request.POST.get("sort_code")
    invoice.account_number = request.POST.get("account_number")
    invoice.account_holder_name = request.POST.get("account_holder_name")

    invoice.save()
    invoice.items.set(invoice_items)

    QuotaUsage.create_str(request.user, "invoices-count", invoice.id)

    return invoice
