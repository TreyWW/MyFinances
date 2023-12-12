from django.contrib import messages
from django.http import HttpRequest, JsonResponse, QueryDict
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from backend.models import Invoice
from datetime import datetime


@require_http_methods(["POST"])
def edit_invoice(request: HttpRequest):

    try:
        invoice = Invoice.objects.get(id=request.POST.get('invoice_id'))
    except:
        return JsonResponse({"message": "Invoice not found"}, status=404)

    attributes_to_updates = {
        "date_due": datetime.strptime(request.POST.get('date_due'), '%Y-%m-%d').date(),
        "date_issued": request.POST.get('date_issued'),
        "client_name": request.POST.get('to_name'),
        "client_company": request.POST.get('to_company'),
        "client_address": request.POST.get('to_address'),
        "client_city": request.POST.get('to_city'),
        "client_county": request.POST.get('to_county'),
        "client_country": request.POST.get('to_country'),
        "self_name": request.POST.get('from_name'),
        "self_company": request.POST.get('from_company'),
        "self_address": request.POST.get('from_address'),
        "self_city": request.POST.get('from_city'),
        "self_county": request.POST.get('from_county'),
        "self_country": request.POST.get('from_country'),
        "notes": request.POST.get('notes'),
        "invoice_number": request.POST.get('invoice_number'),
        "vat_number": request.POST.get('vat_number'),
        "reference": request.POST.get('reference'),
        "sort_code": request.POST.get('sort_code'),
        "account_number": request.POST.get('account_number'),
        "account_holder_name": request.POST.get('account_holder_name')
    }

    for column_name, new_value in attributes_to_updates.items():
        setattr(invoice, column_name, new_value)

    invoice.save()

    if request.htmx:
        messages.success(request, "Invoice edited")
        return render(request, "partials/base/toasts.html")

    return JsonResponse({"message": "Invoice successfully edited"}, status=200)
