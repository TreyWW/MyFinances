from django.views.decorators.http import require_http_methods
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from django.shortcuts import redirect
from django.shortcuts import render

from backend.core.service.settings.view import (
    validate_page,
    account_page_context,
    api_keys_page_context,
    account_defaults_context,
    email_templates_context,
)
from backend.core.types.requests import WebRequest


@require_http_methods(["GET"])
def view_settings_page_endpoint(request: WebRequest, page: str | None = None):
    if not validate_page(page):
        messages.error(request, "Invalid settings page")
        if request.htmx:
            return render(request, "base/toast.html")
        return redirect("settings:dashboard")

    context: dict = {}

    match page:
        case "account":
            account_page_context(request, context)
        case "api_keys":
            api_keys_page_context(request, context)
        case "account_defaults":
            account_defaults_context(request, context)
        case "email_templates":
            email_templates_context(request, context)

    template = f"pages/settings/pages/{page or 'profile'}.html"

    if not page or not request.GET.get("on_main"):
        context["page_template"] = template
        return render(request, "pages/settings/main.html", context)

    response = render(request, template, context)

    response.no_retarget = True  # type: ignore[attr-defined]
    return response


def change_password(request: WebRequest):
    if request.method == "POST":
        current_password = request.POST.get("current_password")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        error = validate_password_change(request.user, current_password, password, confirm_password)

        if error:
            messages.error(request, error)
            return redirect("settings:change_password")

        # If no errors, update the password
        request.user.set_password(password)
        request.user.save()
        update_session_auth_hash(request, request.user)
        messages.success(request, "Successfully changed your password.")
        return redirect("settings:dashboard")

    return render(request, "pages/reset_password.html", {"type": "change"})


def validate_password_change(user, current_password, new_password, confirm_password):
    if not user.check_password(current_password):
        return "Incorrect current password"

    if new_password != confirm_password:
        return "Passwords don't match"

    if not new_password:
        return "Something went wrong, no password was provided."

    if len(new_password) < 8 or len(new_password) > 128:
        return "Password must be between 8 and 128 characters."

    return None
