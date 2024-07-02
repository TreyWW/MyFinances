from django.http import HttpResponse
from django.urls import reverse
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.shortcuts import redirect
from django.shortcuts import render

from backend.service.onboarding.create import create_onboarding_form
from backend.service.onboarding.settings import validate_page, get_existing_forms, get_valid_form
from backend.types.requests import WebRequest
from backend.views.core.onboarding import OnboardingForm


@require_http_methods(["GET"])
def view_settings_page_endpoint(request: WebRequest, page: str | None = None, sub_page: str | None = None) -> HttpResponse:
    if not validate_page(page, sub_page):
        messages.error(request, "Invalid onboarding page")
        if request.htmx:
            response = render(request, "base/toast.html")
            response["HX-Redirect"] = reverse("onboarding:settings")
            return response
        return redirect("onboarding:settings")

    context: dict = {}

    match page:
        case "form-builder":
            forms = get_existing_forms(request.actor)
            context.update({"forms": forms})
        # case "form-builder":
        #     match sub_page:
        #         case

    template = f"pages/onboarding/settings/pages/{page or 'profile'}.html"
    if not page or not request.GET.get("onboarding_main"):
        context["page_template"] = template
        return render(request, "pages/onboarding/settings/main.html", context)
    response = render(request, template, context)

    response.no_retarget = True  # type: ignore[attr-defined]
    return response


@require_http_methods(["POST"])
def create_form_endpoint(request: WebRequest) -> HttpResponse:
    onboarding_form = create_onboarding_form(request.actor)
    # onboarding_form.uuid

    response = HttpResponse(status=200)
    # response.retarget =
    return response


@require_http_methods(["GET"])
def edit_form_endpoint(request: WebRequest, form_uuid) -> HttpResponse:

    try:
        form = get_valid_form(form_uuid, request.actor)
    except OnboardingForm.DoesNotExist:
        messages.error(request, "Form not found")
        if request.htmx:
            response = render(request, "base/toast.html")
            response["HX-Redirect"] = reverse("onboarding:settings with page", kwargs={"page": "form-builder"})
            return response
        return redirect("onboarding:settings with page", "form-builder")
    context: dict = {"form": form}
    template = f"pages/onboarding/form_builder/edit/content.html"

    if not request.GET.get("onboarding_form_builder_structure"):
        context["page_template"] = template
        return render(request, "pages/onboarding/form_builder/edit/structure.html", context)

    response = render(request, template, context)

    response.no_retarget = True  # type: ignore[attr-defined]
    return response
