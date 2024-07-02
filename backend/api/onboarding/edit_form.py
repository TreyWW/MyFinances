from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import render

from backend.service.onboarding.settings import get_valid_form
from backend.types.requests import WebRequest
from backend.views.core.onboarding import OnboardingForm


def edit_form_name_endpoint(request: WebRequest, form_uuid: str) -> HttpResponse:
    new_form_name = request.POST.get("form_name")

    try:
        form = get_valid_form(form_uuid, request.actor)
    except OnboardingForm.DoesNotExist:
        messages.error(request, "Form not found")
        if request.htmx:
            response = render(request, "base/toast.html")
        else:
            response = HttpResponse(status=404)
        return response

    form.title = new_form_name
    form.save(update_fields=["title"])
    return HttpResponse(status=204)
