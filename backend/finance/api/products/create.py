from django.contrib import messages

from backend.finance.api.products.fetch import fetch_products
from backend.decorators import web_require_scopes
from backend.finance.models import InvoiceProduct
from backend.core.types.htmx import HtmxHttpRequest


@web_require_scopes("invoices:write", True, True)
def create_product(request: HtmxHttpRequest):
    try:
        quantity = int(request.POST.get("post_quantity", ""))
        service_name = request.POST.get("post_service_name", "")
        service_description = request.POST.get("post_service_description", "")
        rate = int(request.POST.get("post_rate", ""))

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
