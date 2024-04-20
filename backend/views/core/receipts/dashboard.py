from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from backend.types.htmx import HtmxHttpRequest


@login_required
def receipts_dashboard(request: HtmxHttpRequest):
    return render(request, "pages/receipts/dashboard.html")
