from django.contrib.auth.decorators import login_required
from django.http import HttpRequest
from django.shortcuts import render, redirect

from backend.decorators import *
from backend.models import *


@login_required
def invoices_dashboard(request: HttpRequest):
    context = {}
    context["invoices"] = (Invoice.objects
                           .filter(user=request.user)
                           .prefetch_related("items")
                           .only("invoice_id", "id", "payment_status", "date_due"))
    # May need to add more logic later

    return render(request, 'core/pages/invoices/dashboard/dashboard.html', context)


@login_required
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
