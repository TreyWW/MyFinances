from django.contrib import messages
from django.shortcuts import render
from django.urls import reverse

from backend.core.types.requests import WebRequest
from backend.decorators import web_require_scopes
from backend.models import OnboardingForm


@web_require_scopes("onboarding:write", True, True)
def create_form_endpoint(request: WebRequest):
    form = OnboardingForm.objects.create(owner=request.actor, title=f"{request.user.name}'s Untitled Form")

    visit_form_url = reverse("onboarding:forms:edit", args=[form.uuid])

    messages.success(
        request,
        f"""
        Successfully created a new form. Click <a class="link link-primary" href="{visit_form_url}">here</a> to view it!
    """,
    )
    resp = render(request, "base/toast.html")

    resp["HX-Trigger-After-Swap"] = "onboarding_forms_list_refresh"

    return resp
