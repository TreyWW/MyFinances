from django.contrib import messages
from django.db.models import Q
from django.http import HttpRequest
from django.shortcuts import render

from backend.api.products.fetch import fetch_products
from backend.models_db.invoice import InvoiceProduct


def create_product(request: HttpRequest):
    try:
        quantity = int(request.POST.get("post_quantity"))
        service_name = request.POST.get("post_service_name")
        service_description = request.POST.get("post_service_description")
        rate = int(request.POST.get("post_rate"))

        product = InvoiceProduct.objects.create(
            user=request.user,
            name=service_name,
            description=service_description,
            rate=rate,
            quantity=quantity,
        )

        messages.success(request, "Product created")
        return fetch_products(request)
    except ValueError:
        messages.error(request, "Invalid inputs")
