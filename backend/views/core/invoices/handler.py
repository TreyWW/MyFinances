from typing import Dict, Any

from django.http import HttpResponse
from django.shortcuts import render

from backend.types.requests import WebRequest


def invoices_core_handler(request: WebRequest, template_name: str, context: Dict[str, Any] = None, **kwargs) -> HttpResponse:
    context: dict = context or {}
    if not request.GET.get("invoice_structure_main", None) or not request.htmx:
        context["page_template"] = template_name
        return render(request, "pages/invoices/dashboard/core/main.html", context, **kwargs)

    response = render(request, template_name, context, **kwargs)
    response.no_retarget = True
    response["HX-Trigger-After-Settle"] = "update_breadcrumbs"
    return response
