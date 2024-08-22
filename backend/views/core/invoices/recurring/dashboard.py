from django.contrib import messages
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods

from backend.decorators import web_require_scopes
from backend.models import Invoice
from backend.types.requests import WebRequest
from backend.views.core.invoices.handler import invoices_core_handler


@require_http_methods(["GET"])
@web_require_scopes("invoices:read", False, False, "dashboard")
def invoices_recurring_dashboard_endpoint(request: WebRequest):
    print("using this")
    return invoices_core_handler(request, "pages/invoices/recurring/dashboard/dashboard.html")
