from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from backend.core.service.invoices.common.create.services.add import add
from backend.core.types.requests import WebRequest


@require_http_methods(["POST"])
def add_service_endpoint(request: WebRequest):
    return render(request, "pages/invoices/create/services/_services_table_body.html", add(request))
