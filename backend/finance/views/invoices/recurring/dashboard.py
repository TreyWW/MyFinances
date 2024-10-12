from django.views.decorators.http import require_http_methods

from backend.decorators import web_require_scopes, has_entitlements
from backend.core.types.requests import WebRequest
from backend.finance.views.invoices.handler import invoices_core_handler


@require_http_methods(["GET"])
@has_entitlements("invoice-schedules")
@web_require_scopes("invoices:read", False, False, "dashboard")
def invoices_recurring_dashboard_endpoint(request: WebRequest):
    return invoices_core_handler(request, "pages/invoices/recurring/dashboard/dashboard.html")
