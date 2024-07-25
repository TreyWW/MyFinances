from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from backend.decorators import web_require_scopes
from backend.types.requests import WebRequest


@require_http_methods(["GET"])
@web_require_scopes("invoices:read", False, False, "dashboard")
def invoices_dashboard_core_endpoint(request: WebRequest):
    return render(request, "pages/invoices/dashboard/core/main.html")
