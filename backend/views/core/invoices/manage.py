from django.http import HttpRequest
from django.shortcuts import render

from backend.decorators import *
from backend.models import *


def invoices_dashboard(request: HttpRequest):
    context = {}

    return render(request, "pages/invoices/dashboard/dashboard.html", context)


def manage_invoice(request: HttpRequest, invoice_id: str):
    if not invoice_id.isnumeric():
        messages.error(request, "Invalid invoice ID")
        return redirect("invoices dashboard")

    invoice = Invoice.objects.get(id=invoice_id)

    if not invoice:
        return redirect("invoices dashboard")
    return render(request, "pages/invoices/dashboard/manage.html", {"invoice": invoice})
