from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from backend.decorators import web_require_scopes
from backend.models import InvoiceRecurringSet
from backend.service.invoices.recurring.get import get_invoice_set
from backend.service.invoices.recurring.validate.frequencies import validate_and_update_frequency
from backend.types.requests import WebRequest


@require_http_methods(["POST"])
@web_require_scopes("invoices:write", True, True)
def edit_invoice_recurring_set_endpoint(request: WebRequest, invoice_set_id):
    invoice_set_response = get_invoice_set(request, invoice_set_id)

    if invoice_set_response.failed:
        messages.error(request, invoice_set_response.error)
        return render(request, "base/toasts.html", {"autohide": False})

    invoice_set: InvoiceRecurringSet = invoice_set_response.response

    frequency_update_response = validate_and_update_frequency(
        invoice_set=invoice_set,
        frequency=request.POST.get("frequency"),
        frequency_day_of_week=request.POST.get("frequency_day_of_week"),
        frequency_day_of_month=request.POST.get("frequency_day_of_month"),
        frequency_month_of_year=request.POST.get("frequency_month_of_year"),
    )

    if frequency_update_response.failed:
        messages.error(request, frequency_update_response.error)
        return render(request, "base/toasts.html")

    attributes_to_update = {
        "date_due": request.POST.get("date_due"),
        "date_issued": request.POST.get("date_issued"),
        "client_name": request.POST.get("to_name"),
        "client_company": request.POST.get("to_company"),
        "client_address": request.POST.get("to_address"),
        "client_city": request.POST.get("to_city"),
        "client_county": request.POST.get("to_county"),
        "client_country": request.POST.get("to_country"),
        "self_name": request.POST.get("from_name"),
        "self_company": request.POST.get("from_company"),
        "self_address": request.POST.get("from_address"),
        "self_city": request.POST.get("from_city"),
        "self_county": request.POST.get("from_county"),
        "self_country": request.POST.get("from_country"),
        "notes": request.POST.get("notes"),
        "invoice_number": request.POST.get("invoice_number"),
        "vat_number": request.POST.get("vat_number"),
        "reference": request.POST.get("reference"),
        "sort_code": request.POST.get("sort_code"),
        "account_number": request.POST.get("account_number"),
        "account_holder_name": request.POST.get("account_holder_name"),
    }

    for column_name, new_value in attributes_to_update.items():
        if new_value is not None:
            if column_name == "date_due":
                try:
                    new_value = datetime.strptime(new_value, "%Y-%m-%d").date()  # type: ignore[assignment]
                except ValueError:
                    messages.error(request, "Invalid date format for date_due")
                    return render(request, "base/toasts.html")
            setattr(invoice_set, column_name, new_value)

    invoice_set.save()

    if request.htmx:
        messages.success(request, "Invoice edited")
        return render(request, "base/toasts.html")

    return JsonResponse({"message": "Invoice successfully edited"}, status=200)
