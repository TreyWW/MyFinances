from datetime import datetime

from django.contrib import messages
from django.core.exceptions import ValidationError

from backend.models import InvoiceRecurringSet, Client, QuotaUsage
from backend.types.requests import WebRequest


def save_invoice(request: WebRequest, invoice_items):
    currency = request.user.user_profile.currency

    end_date = request.POST.get("end_date")

    try:
        if end_date:
            datetime.strptime(end_date, "%Y-%m-%d").date()
    except ValueError:
        messages.error(request, "Please enter a valid end date")
        return None
    finally:
        end_date = datetime.strptime(end_date, "%Y-%m-%d").date() if end_date else None

    invoice_set = InvoiceRecurringSet(
        end_date=end_date,
        date_issued=request.POST.get("date_issued"),
        currency=currency,
    )

    if request.user.logged_in_as_team:
        invoice_set.organization = request.user.logged_in_as_team
    else:
        invoice_set.user = request.user

    if request.POST.get("selected_client"):
        try:
            client = Client.objects.get(user=request.user, id=request.POST.get("selected_client", ""))
            invoice_set.client_to = client
        except Client.DoesNotExist:
            messages.error(request, "Client not found")
            return None
    else:
        invoice_set.client_name = request.POST.get("to_name")
        invoice_set.client_company = request.POST.get("to_company")
        invoice_set.client_address = request.POST.get("to_address")
        invoice_set.client_city = request.POST.get("to_city")
        invoice_set.client_county = request.POST.get("to_county")
        invoice_set.client_country = request.POST.get("to_country")
        invoice_set.client_is_representative = True if request.POST.get("is_representative") == "on" else False

    invoice_set.self_name = request.POST.get("from_name")
    invoice_set.self_company = request.POST.get("from_company")
    invoice_set.self_address = request.POST.get("from_address")
    invoice_set.self_city = request.POST.get("from_city")
    invoice_set.self_county = request.POST.get("from_county")
    invoice_set.self_country = request.POST.get("from_country")

    invoice_set.notes = request.POST.get("notes")
    invoice_set.invoice_number = request.POST.get("invoice_number")
    invoice_set.vat_number = request.POST.get("vat_number")
    invoice_set.logo = request.FILES.get("logo")
    invoice_set.reference = request.POST.get("reference")
    invoice_set.sort_code = request.POST.get("sort_code")
    invoice_set.account_number = request.POST.get("account_number")
    invoice_set.account_holder_name = request.POST.get("account_holder_name")

    try:
        invoice_set.full_clean()
    except ValidationError as validation_errors:
        for field, error in validation_errors.error_dict.items():
            for e in error:
                messages.error(request, f"{field}: {e.messages[0]}")
        return None

    invoice_set.save()
    invoice_set.items.set(invoice_items)

    QuotaUsage.create_str(request.user, "invoices-count", invoice_set.id)

    return invoice_set
