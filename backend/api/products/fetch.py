from django.db.models import Q, QuerySet
from django.shortcuts import render

from backend.models import InvoiceProduct
from backend.types.htmx import HtmxHttpRequest


def fetch_products(request: HtmxHttpRequest):
    results: QuerySet
    search_text = request.GET.get("search_existing_service")
    if search_text:
        results = (
            InvoiceProduct.objects.filter(user=request.user)
            .filter(Q(name__icontains=search_text) | Q(description__icontains=search_text))
            .order_by("name")
        )
    else:
        results = InvoiceProduct.objects.filter(user=request.user).order_by("name")

    return render(request, "pages/products/fetched_items.html", {"products": results[:5]})
