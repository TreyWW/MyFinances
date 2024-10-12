from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from backend.core.types.htmx import HtmxHttpRequest
from backend.core.service.invoices.common.create.services.add import add


@require_http_methods(["POST"])
def add_service_endpoint(request: HtmxHttpRequest):
    return render(request, "pages/invoices/create/services/_services_table_body.html", add(request))
