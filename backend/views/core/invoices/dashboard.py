from django.http import HttpRequest
from django.shortcuts import render

from backend.decorators import *
from backend.models import *


def invoices_dashboard(request: HttpRequest):
    context = {}
    context["invoices"] = (Invoice.objects
                           .filter(user=request.user)
                           .prefetch_related("items")
                           .only("invoice_id", "id", "payment_status", "date_due"))
    # May need to add more logic later

    # context["modal_data"] = [
    #     {
    #         "id": "modal_confirm_delete",
    #         "title": "Are you sure you would like to delete this invoice?",
    #     }
    #     ]

    return render(request, 'core/pages/invoices/dashboard/dashboard.html', context)


def invoices_dashboard_id(request: HttpRequest, invoice_id):
    if invoice_id == "create":
        return redirect("invoices dashboard create")
    elif type(invoice_id) != "int":
        messages.error(request, "Invalid invoice ID")
        return redirect("invoices dashboard")
    invoices = Invoice.objects.get(id=invoice_id)
    if not invoices:
        return redirect('invoices dashboard')
    return render(request, 'core/pages/invoices/dashboard/dashboard.html', )
