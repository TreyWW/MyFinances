from django.shortcuts import render

from backend.core.types.requests import WebRequest
from backend.decorators import web_require_scopes


@web_require_scopes("onboarding:read")
def list_forms_endpoint(request: WebRequest):
    return render(request, "pages/onboarding/forms/list/dashboard.html")
