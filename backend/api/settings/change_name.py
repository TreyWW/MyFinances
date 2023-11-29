from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from backend.models import User, Team


@require_http_methods(["POST"])
def change_account_name(request: HttpRequest):
    if not request.htmx:
        return HttpResponse("Invalid Request", status=405)

    first_name = request.POST.get("first_name")
    last_name = request.POST.get("last_name")

    if not first_name and not last_name:
        messages.error(request, "Please enter a valid firstname or lastname.")
        return render(request, "partials/base/toasts.html")

    if first_name:
        request.user.first_name = first_name

    if last_name:
        request.user.last_name = last_name

    request.user.save()

    messages.success(
        request, f"Successfully changed your name to {request.user.get_full_name()}"
    )

    return render(request, "partials/base/toasts.html")
