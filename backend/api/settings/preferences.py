from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from backend.models import UserSettings


@require_http_methods(["POST"])
def update_account_preferences(request):
    currency = request.POST.get("currency", None)
    try:
        usersettings = request.user.user_profile
    except UserSettings.DoesNotExist:
        usersettings = UserSettings.objects.create(user=request.user)

    htmx_return = "base/toasts.html"

    if not request.htmx and not currency:
        return HttpResponse("Invalid Request", status=400)
    elif not currency or currency not in usersettings.CURRENCIES:
        messages.error(request, "Invalid Currency")
        return render(request, htmx_return)

    usersettings.currency = currency

    updated_features: bool = False

    for choice, _ in usersettings.CoreFeatures.choices:
        selected: str | None = request.POST.get(f"selected_{choice}", None)

        if choice in usersettings.disabled_features:  # currently disabled
            if selected:  # enabled
                updated_features = True
                usersettings.disabled_features.remove(choice)
        else:
            if not selected:  # disabled
                updated_features = True
                usersettings.disabled_features.append(choice)

    usersettings.save(update_fields=["disabled_features", "currency"])
    messages.success(request, "Successfully updated preferences")

    if updated_features:
        response = HttpResponse("Success")
        response["HX-Refresh"] = "true"
        return response
    return render(request, htmx_return)
