from __future__ import annotations

from django.http import HttpResponse
from django.shortcuts import render

from backend.types.htmx import HtmxHttpRequest


def dashboard(request: HtmxHttpRequest) -> HttpResponse:
    return render(request, "pages/emails/dashboard.html", {})
