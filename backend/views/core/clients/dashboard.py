from django.shortcuts import render

from backend.types.htmx import HtmxHttpRequest


def clients_dashboard(request: HtmxHttpRequest):
    return render(request, "pages/clients/dashboard/dashboard.html")
