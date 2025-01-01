from django.shortcuts import render

from core.decorators import web_require_scopes
from core.types.htmx import HtmxHttpRequest


@web_require_scopes("clients:read", False, False, "dashboard")
def clients_dashboard_endpoint(request: HtmxHttpRequest):
    return render(request, "pages/clients/dashboard/dashboard.html")
