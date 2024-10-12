from django.contrib import messages
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from backend.decorators import web_require_scopes, has_entitlements
from backend.finance.models import InvoiceRecurringProfile
from backend.core.service.invoices.recurring.get import get_invoice_profile
from backend.finance.views.invoices.handler import invoices_core_handler


# RELATED PATH FILES : \frontend\templates\pages\invoices\dashboard\_fetch_body.html, \backend\urls.py


# Function that takes an invoice object and makes a dict of its attributes
def invoice_get_existing_data(invoice_obj: InvoiceRecurringProfile):
    stored_data = {
        "from_name": invoice_obj.self_name,
        "from_company": invoice_obj.self_company,
        "from_address": invoice_obj.self_address,
        "from_city": invoice_obj.self_city,
        "from_county": invoice_obj.self_county,
        "from_country": invoice_obj.self_country,
        "from_date_issued": invoice_obj.date_issued,
        "from_end_date": invoice_obj.end_date,
        "issue_date": invoice_obj.date_issued,
        "end_date": invoice_obj.end_date,
        "invoice_object": invoice_obj,
        "currency_symbol": invoice_obj.get_currency_symbol(),
        "rows": invoice_obj.items.all(),
        "frequency": invoice_obj.frequency,
        "day_of_week": invoice_obj.day_of_week,
        "day_of_month": invoice_obj.day_of_month,
        "month_of_year": invoice_obj.month_of_year,
        "account_number": invoice_obj.account_number,
        "account_holder_name": invoice_obj.account_holder_name,
        "sort_code": invoice_obj.sort_code,
        "logo": invoice_obj.logo,
    }

    if invoice_obj.client_to:
        stored_data["to_name"] = invoice_obj.client_to.name
        stored_data["to_company"] = invoice_obj.client_to.company
        stored_data["to_email"] = invoice_obj.client_to.email
        stored_data["is_representative"] = invoice_obj.client_to.is_representative
        # stored_data["to_address"] = invoice_obj.client_to.address
        # stored_data["to_city"] = invoice_obj.client_to.city
        # stored_data["to_county"] = invoice_obj.client_to.county
        # stored_data["to_country"] = invoice_obj.client_to.country
    else:
        stored_data["to_name"] = invoice_obj.client_name
        stored_data["to_company"] = invoice_obj.client_company
        stored_data["to_email"] = invoice_obj.client_email
        stored_data["to_address"] = invoice_obj.client_address
        stored_data["to_city"] = invoice_obj.client_city
        stored_data["to_county"] = invoice_obj.client_county
        stored_data["to_country"] = invoice_obj.client_country
        stored_data["is_representative"] = invoice_obj.client_is_representative

    if invoice_obj.client_to:
        stored_data["existing_client"] = invoice_obj.client_to

    return stored_data


# gets invoice object from invoice id, convert obj to dict, and renders edit.html while passing the stored invoice values to frontend
@require_http_methods(["GET"])
@has_entitlements("invoice-schedules")
@web_require_scopes("invoices:write", False, False, "finance:invoices:recurring:dashboard")
def invoice_edit_page_endpoint(request, invoice_profile_id):
    get_response = get_invoice_profile(request, invoice_profile_id)

    if get_response.failed:
        messages.error(request, get_response.error_message)
        return render(request, "base/toast.html")

    invoice_profile: InvoiceRecurringProfile = get_response.response

    # use to populate fields with existing data in edit_from_destination.html AND edit_to_destination.html
    data_to_populate = invoice_get_existing_data(invoice_profile) | {"InvoiceRecurringProfile": InvoiceRecurringProfile}

    print(data_to_populate)

    return invoices_core_handler(request, "pages/invoices/recurring/edit/edit_recurring.html", data_to_populate)
