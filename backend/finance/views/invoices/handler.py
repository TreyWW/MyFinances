from typing import Dict, Any

from django.http import HttpResponse
from django.shortcuts import render

from backend.core.types.requests import WebRequest


def invoices_core_handler(request: WebRequest, template_name: str, start_context: Dict[str, Any] | None = None, **kwargs) -> HttpResponse:
    context: dict[str, Any] = start_context or {}
    if not request.GET.get("invoice_structure_main", None) or not request.htmx:
        context["page_template"] = template_name
        if template_name == "pages/invoices/dashboard/manage.html":
            context["notoggler"] = True
        return render(request, "pages/invoices/dashboard/core/main.html", context, **kwargs)

    response = render(request, template_name, context, **kwargs)
    response.no_retarget = True  # type: ignore[attr-defined]
    response["HX-Trigger-After-Settle"] = "update_breadcrumbs"
    return response
