from django.contrib import messages
from django.shortcuts import render, redirect

from backend.core.types.requests import WebRequest
from backend.decorators import web_require_scopes
from backend.models import OnboardingForm, AuditLog


@web_require_scopes("onboarding:write")
def edit_form_endpoint(request: WebRequest, uuid):
    form: OnboardingForm | None = OnboardingForm.filter_by_owner(request.actor).filter(uuid=uuid).first()

    if not form:
        messages.error(request, "Form not found")
        return redirect("onboarding:forms:list")

    return render(request, "pages/onboarding/forms/edit/main.html", {"form": form})
