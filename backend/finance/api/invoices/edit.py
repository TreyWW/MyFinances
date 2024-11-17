from datetime import datetime
from typing import Literal

from django.contrib import messages
from django.http import HttpRequest, JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods, require_POST

from backend.decorators import web_require_scopes
from backend.finance.models import Invoice
from backend.core.types.htmx import HtmxHttpRequest


@require_http_methods(["POST"])
@web_require_scopes("invoices:write", True, True)
def edit_invoice(request: HtmxHttpRequest):
    try:
        invoice = Invoice.objects.get(id=request.POST.get("invoice_id", ""))
    except Invoice.DoesNotExist:
        return JsonResponse({"message": "Invoice not found"}, status=404)

    if request.user.logged_in_as_team and request.user.logged_in_as_team != invoice.organization:
        return JsonResponse(
            {"message": "You do not have permission to edit this invoice"},
            status=403,
        )
    elif request.user != invoice.user:
        return JsonResponse(
            {"message": "You do not have permission to edit this invoice"},
            status=403,
        )

    attributes_to_updates = {
        "date_due": request.POST.get("date_due"),
        "date_issued": request.POST.get("date_issued"),
        "client_name": request.POST.get("to_name"),
        "client_company": request.POST.get("to_company"),
        "client_email": request.POST.get("to_email"),
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
        "vat_number": request.POST.get("vat_number"),
        "reference": request.POST.get("reference"),
        "sort_code": request.POST.get("sort_code"),
        "account_number": request.POST.get("account_number"),
        "account_holder_name": request.POST.get("account_holder_name"),
    }

    for column_name, new_value in attributes_to_updates.items():
        if new_value is not None:
            if column_name == "date_due":
                try:
                    new_value = datetime.strptime(new_value, "%Y-%m-%d").date()  # type: ignore[assignment]
                except ValueError:
                    messages.error(request, "Invalid date format for date_due")
                    return render(request, "base/toasts.html")
            setattr(invoice, column_name, new_value)

    invoice.save()

    if request.htmx:
        messages.success(request, "Invoice edited")
        return render(request, "base/toasts.html")

    return JsonResponse({"message": "Invoice successfully edited"}, status=200)


@require_POST
@web_require_scopes("invoices:write", True, True)
def change_status(request: HtmxHttpRequest, invoice_id: int, status: str) -> HttpResponse:
    status = status.lower() if status else ""

    if not request.htmx:
        return redirect("finance:invoices:single:dashboard")

    try:
        invoice = Invoice.objects.get(id=invoice_id)
    except Invoice.DoesNotExist:
        return return_message(request, "Invoice not found")

    if not invoice.has_access(request.user):
        return return_message(request, "You don't have permission to make changes to this invoice.")

    if status not in ["paid", "draft", "pending"]:
        return return_message(request, "Invalid status. Please choose from: pending, paid, draft")

    if invoice.status == status:
        return return_message(request, f"Invoice status is already {status}")

    invoice.set_status(status)

    send_message(request, f"Invoice status been changed to <strong>{status}</strong>", success=True)

    return render(request, "pages/invoices/dashboard/_modify_payment_status.html", {"status": status, "invoice_id": invoice_id})


@require_POST
@web_require_scopes("invoices:write", True, True)
def edit_discount(request: HtmxHttpRequest, invoice_id: str):
    discount_type = "percentage" if request.POST.get("discount_type") == "on" else "amount"
    discount_amount_str: str = request.POST.get("discount_amount", "")
    percentage_amount_str: str = request.POST.get("percentage_amount", "")

    if not request.htmx:
        return redirect("finance:invoices:single:dashboard")

    try:
        invoice: Invoice = Invoice.objects.get(id=invoice_id)
    except Invoice.DoesNotExist:
        return return_message(request, "Invoice not found", False)

    if not invoice.has_access(request.user):
        return return_message(request, "You don't have permission to make changes to this invoice.", False)

    if discount_type == "percentage":
        try:
            percentage_amount = int(percentage_amount_str)
            if percentage_amount < 0 or percentage_amount > 100:
                raise ValueError
        except ValueError:
            return return_message(request, "Please enter a valid percentage amount (between 0 and 100)", False)
        invoice.discount_percentage = percentage_amount
    else:
        try:
            discount_amount = int(discount_amount_str)
            if discount_amount < 0:
                raise ValueError
        except ValueError:
            return return_message(request, "Please enter a valid discount amount", False)
        invoice.discount_amount = discount_amount

    invoice.save()

    messages.success(request, "Discount was applied successfully")

    response = render(request, "base/toasts.html")
    response["HX-Trigger"] = "update_invoice"
    return response


def return_message(request: HttpRequest, message: str, success: bool = True) -> HttpResponse:
    send_message(request, message, success)
    return render(request, "base/toasts.html")


def send_message(request: HttpRequest, message: str, success: bool = False) -> None:
    if success:
        messages.success(request, message)
    else:
        messages.error(request, message)
