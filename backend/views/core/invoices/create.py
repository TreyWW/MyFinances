from django.http import HttpRequest
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.decorators.http import require_http_methods
from backend.models import Invoice, InvoiceItem, Client


def invoice_page_get(request: HttpRequest):
    context = {}
    context["modal_data"] = [{
        "id": "modal_from_destination",
        "title": "Update your info",
        "action": {
            "text": "Update", "method": "post",
            "extra": f"hx-post={reverse_lazy('api v1 invoices create set_destination from')} hx-target=#from_destination hx-swap=outerHTML",  # hx-refresh=true
            "fields": [
                {
                    "type": "text", "name": "name",
                    "required": True, "label": "Name",
                    "placeholder": "John Smith", "value": "John Smith",
                    "class_extra": "input-ghost-secondary"
                },
                {
                    "type": "text", "name": "address",
                    "required": True, "label": "Address", "placeholder": "128 Road",
                    "value": "128 Road",
                    "class_extra": "input-ghost-secondary"
                },
                {
                    "type": "text", "name": "city",
                    "required": True, "label": "City", "placeholder": "Street",
                    "value": "Street",
                    "class_extra": "input-ghost-secondary"
                },
                {
                    "type": "text", "name": "country",
                    "required": True, "label": "City", "placeholder": "England",
                    "value": "England",
                    "class_extra": "input-ghost-secondary"
                },
                {
                    "type": "hidden",
                    "name": "modal_from_"
                }
            ]
        }
    }, ]

    context["modal_data"].append({
        "id": "modal_to_destination",
        "title": "Update their info",
        "action": {
            "text": "Update", "method": "post",
            "extra": f"hx-post={reverse_lazy('api v1 invoices create set_destination to')} hx-target=#to_destination hx-swap=outerHTML",  # hx-refresh=true
            "fields": [
                {
                    "type": "text", "name": "name",
                    "required": True, "label": "Name",
                    "placeholder": "John Smith", "value": "John Smith",
                    "class_extra": "input-ghost-secondary"
                },
                {
                    "type": "text", "name": "address",
                    "required": True, "label": "Address",
                    "placeholder": "128 Road", "value": "128 Road",
                    "class_extra": "input-ghost-secondary"
                },
                {
                    "type": "text", "name": "city",
                    "required": True, "label": "City",
                    "placeholder": "Street", "value": "Street",
                    "class_extra": "input-ghost-secondary"
                },
                {
                    "type": "text", "name": "country",
                    "required": True, "label": "City",
                    "placeholder": "England", "value": "England",
                    "class_extra": "input-ghost-secondary"
                },
                {
                    "type": "hidden",
                    "name": "modal_from_",
                    "value": ""
                }
            ]
        }
    })

    return render(request, "core/pages/invoices/create/create.html", context)


def invoice_page_post(request: HttpRequest):
    invoice_items = [
        InvoiceItem.objects.create(
            description=row[0],
            hours=row[1],
            price_per_hour=row[2]
        ) for row in zip(
            request.POST.getlist('service_name[]'),
            request.POST.getlist('hours[]'),
            request.POST.getlist('price_per_hour[]')
        )
    ]  # Todo: add products to this for logic

    invoice = Invoice.objects.create(
        user=request.user,
        date_due=request.POST.get('date_due'),
        date_issued=request.POST.get('date_issued')
    )

    invoice.items.set(invoice_items)

    return redirect("index")


@require_http_methods(['GET', 'POST'])
def create_invoice_page(request: HttpRequest):
    if request.method == "POST":
        return invoice_page_post(request)
    return invoice_page_get(request)

