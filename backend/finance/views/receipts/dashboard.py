from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from backend.decorators import web_require_scopes
from backend.core.types.htmx import HtmxHttpRequest


@login_required
@web_require_scopes("receipts:read", False, False, "dashboard")
def receipts_dashboard(request: HtmxHttpRequest):
    return render(request, "pages/receipts/dashboard.html")
