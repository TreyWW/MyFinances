from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from backend.models import UserSettings


@require_http_methods(["POST"])
def update_currency_view(request):
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

    if usersettings.currency == currency:
        messages.warning(request, "You are already using this currency, no change was made")
        return render(request, htmx_return)

    usersettings.currency = currency
    usersettings.save()
    messages.success(request, "Successfully updated currency")

    return render(request, htmx_return)
