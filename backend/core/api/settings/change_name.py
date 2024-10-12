from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from backend.core.types.htmx import HtmxHttpRequest


@require_http_methods(["POST"])
def change_account_name(request: HtmxHttpRequest):
    if not request.htmx:
        return HttpResponse("Invalid Request", status=405)

    htmx_return = "base/toasts.html"

    first_name = request.POST.get("first_name")
    last_name = request.POST.get("last_name")

    if not first_name and not last_name:
        messages.error(request, "Please enter a valid firstname or lastname.")
        return render(request, htmx_return)

    if request.user.first_name == first_name and request.user.last_name == last_name:
        messages.warning(request, "You already have this name.")
        return render(request, htmx_return)

    if first_name:
        request.user.first_name = first_name

    if last_name:
        request.user.last_name = last_name

    request.user.save()

    messages.success(
        request,
        f"Successfully changed your name to <strong>{request.user.get_full_name()}</strong>",
    )

    return render(request, htmx_return)
