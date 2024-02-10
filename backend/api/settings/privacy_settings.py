from django.contrib import messages
from django.http import HttpRequest
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods


@require_http_methods(["POST"])
def allow_receipt_parsing(request: HttpRequest):
    if not request.htmx:
        return redirect("user settings")

    htmx_return = "partials/messages_list.html"

    allow_receipt_parsing = request.POST.get("allow_receipt_parsing", False)

    if allow_receipt_parsing:
        if request.user.user_profile.allow_receipt_parsing:
            messages.warning(request, "You already have allow receipt parsing enabled.")
            return render(request, htmx_return)

        request.user.user_profile.allow_receipt_parsing = True

    else:
        if not request.user.user_profile.allow_receipt_parsing:
            messages.warning(request, "You already have allow receipt parsing disabled.")
            return render(request, htmx_return)

        request.user.user_profile.allow_receipt_parsing = False

    request.user.user_profile.save()

    messages.success(
        request,
        f"Successfully <strong>{'enabled' if allow_receipt_parsing else 'disabled'}</strong> receipt parsing.",
    )

    return render(request, htmx_return)
