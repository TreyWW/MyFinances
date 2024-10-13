from django.shortcuts import render

from backend.core.types.requests import WebRequest
from backend.decorators import web_require_scopes
from backend.models import OnboardingForm


@web_require_scopes("onboarding:read", True, True)
def list_forms_endpoint(request: WebRequest):
    forms = OnboardingForm.filter_by_owner(request.actor).all()

    return render(request, "pages/onboarding/forms/list/_rows.html", {"forms": forms})
