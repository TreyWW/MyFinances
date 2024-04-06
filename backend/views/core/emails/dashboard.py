from __future__ import annotations

from django.http import HttpRequest
from django.http import HttpResponse
from django.shortcuts import render


def dashboard(request: HttpRequest) -> HttpResponse:
    return render(request, "pages/emails/dashboard.html", {})
