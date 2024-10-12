from __future__ import annotations

from django.http import HttpResponse
from django.shortcuts import render

from backend.decorators import feature_flag_check, web_require_scopes
from backend.core.types.htmx import HtmxHttpRequest


@feature_flag_check("areUserEmailsAllowed", status=True)
@web_require_scopes("emails:read", False, False, "dashboard")
def dashboard(request: HtmxHttpRequest) -> HttpResponse:
    return render(request, "pages/emails/dashboard.html", {})
