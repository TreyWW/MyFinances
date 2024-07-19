from django.contrib import messages
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from backend.service.settings.update import update_profile_picture
from backend.service.settings.view import get_user_profile
from backend.types.requests import WebRequest


@require_http_methods(["POST"])
def change_profile_picture_endpoint(request: WebRequest):
    if not request.htmx:
        messages.error(request, "Invalid request")
        return redirect("settings:dashboard with page", page="profile")

    user_profile = get_user_profile(request)

    print(request.FILES)

    status, message = update_profile_picture(request.FILES.get("profile_picture_image"), user_profile)

    if not status:
        messages.error(request, message)
    else:
        messages.success(request, message)

    return render(
        request,
        "pages/settings/settings/_post_profile_pic.html",
        {"users_profile_picture": user_profile.profile_picture_url},
    )
