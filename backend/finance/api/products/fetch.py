from django.db.models import Q, QuerySet
from django.shortcuts import render

from backend.decorators import web_require_scopes
from backend.finance.models import InvoiceProduct
from backend.core.types.htmx import HtmxHttpRequest


@web_require_scopes("invoices:read", True, True)
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
