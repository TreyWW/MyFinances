from django.contrib import messages
from django.http import HttpRequest, JsonResponse, QueryDict
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from backend.models import Invoice
from datetime import datetime

# RELATED PATH FILES : \frontend\templates\pages\invoices\dashboard\_fetch_body.html, \backend\urls.py


# Function that takes an invoice object and makes a dict of its attributes
def invoice_get_existing_data(invoice_obj):
    stored_data = {
        "og_name": invoice_obj.self_name,
        "og_company": invoice_obj.self_company,
        "og_address": invoice_obj.self_address,
        "og_city": invoice_obj.self_city,
        "og_county": invoice_obj.self_county,
        "og_country": invoice_obj.self_country,
        "og_cilent_name": invoice_obj.client_name,
        "og_cilent_company": invoice_obj.client_company,
        "og_cilent_address": invoice_obj.client_address,
        "og_cilent_city": invoice_obj.client_city,
        "og_cilent_county": invoice_obj.client_county,
        "og_cilent_country": invoice_obj.client_country,
    }
    return stored_data


# gets invoice object from invoice id, convert obj to dict, and renders edit.html while passing the stored invoice values to frontend
def invoice_edit_page_get(request, invoice_id):
    context = {"type": "edit"}
    try:
        invoice = Invoice.objects.get(id=invoice_id)
    except:
        return JsonResponse({"message": "Invoice not found"}, status=404)

    # use to populate fields with existing data in edit_from_destination.html AND edit_to_destination.html
    data_to_populate = invoice_get_existing_data(invoice)
    return render(request, "pages/invoices/edit/edit.html", data_to_populate)


# when user changes/modifies any of the fields with new information (during edit invoice)
@require_http_methods(["POST"])
def edit_invoice(request: HttpRequest, invoice_id):
    try:
        invoice = Invoice.objects.get(id=invoice_id)
    except:
        return JsonResponse({"message": "Invoice not found"}, status=404)

    attributes_to_updates = {
        "date_due": datetime.strptime(request.POST.get("date_due"), "%Y-%m-%d").date(),
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

    for column_name, new_value in attributes_to_updates.items():
        setattr(invoice, column_name, new_value)

    invoice.save()

    if request.htmx:
        messages.success(request, "Invoice edited")
        return render(request, "partials/base/toasts.html")

    return render(request, "pages/invoices/dashboard/dashboard.html")
    # return JsonResponse({"message": "Invoice successfully edited"}, status=200)


# decorator & view function for rendering page and updating invoice items in the backend
@require_http_methods(["GET", "POST"])
def edit_invoice_page(request: HttpRequest, id):
    if request.method == "POST":
        return edit_invoice(request, id)
    return invoice_edit_page_get(request, id)
