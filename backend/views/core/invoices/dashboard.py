from django.http import HttpRequest
from django.shortcuts import render

from backend.decorators import *
from backend.models import *


def invoices_dashboard(request: HttpRequest):
    context = {}

    return render(request, "pages/invoices/dashboard/dashboard.html", context)


def invoices_dashboard_id(request: HttpRequest, invoice_id):
    if invoice_id == "create":
        return redirect("invoices dashboard create")
    elif type(invoice_id) != "int":
        messages.error(request, "Invalid invoice ID")
        return redirect("invoices dashboard")
    invoices = Invoice.objects.get(id=invoice_id)
    if not invoices:
        return redirect("invoices dashboard")
    return render(
        request,
        "pages/invoices/dashboard/dashboard.html",
    )
