from django.contrib.auth.decorators import login_required
from django.http import HttpRequest
from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from backend.models import Invoice, InvoiceItem, Client


@login_required
@require_http_methods(['GET', 'POST'])
def create_invoice_page(request: HttpRequest):
    if request.method == "POST":
        return post(request)
    return get(request)


def get(request):
    return render(request, "core/pages/invoices/create/create.html")


def post(request):
    context = {}

    invoice_items = [
        InvoiceItem.objects.create(
            description = row[0],
            hours = row[1],
            price_per_hour = row[2]
        ) for row in zip(
            request.POST.getlist('service_name[]'),
            request.POST.getlist('hours[]'),
            request.POST.getlist('price_per_hour[]')
        )
    ] # Todo: add products to this for logic

    invoice = Invoice.objects.create(
        user = request.user,
        date_due = request.POST.get('date_due'),
        date_issued = request.POST.get('date_issued')
    )

    invoice.items.set(invoice_items)
    return render(request, "core/pages/invoices/create/create.html")
