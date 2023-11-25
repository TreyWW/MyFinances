from django.contrib.sessions.models import Session
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.contrib.auth import update_session_auth_hash
from PIL import Image
from django.contrib import messages

from backend.decorators import *
from backend.models import *
from backend.utils import Modals

Modals = Modals()


def settings_page(request: HttpRequest):
    context = {}

    usersettings, created = UserSettings.objects.get_or_create(user=request.user)
    context.update(
        {
            "sessions": Session.objects.filter(),
            "currency_signs": usersettings.CURRENCIES,
            "currency": usersettings.currency,
            "user_settings": usersettings,
        }
    )

    if request.method == "POST" and request.htmx:
        currency = request.POST.get("currency")
        section = request.POST.get("section")
        profile_picture = request.FILES.get("profile_image")

        if section == "account_preferences":
            if currency in usersettings.CURRENCIES:
                usersettings.currency = currency
                usersettings.save()
                messages.success(request, "Successfully updated currency")
            else:
                messages.error(request, "Invalid currency")

            context.update(
                {
                    "post_return": "currency",
                    "currency": usersettings.currency,
                    "user_settings": usersettings,
                }
            )
        if section == "profile_picture":
            if profile_picture:
                try:
                    # Max file size is 10MB (Change the first number to determine the size in MB)
                    max_file_size = 10 * 1024 * 1024

                    if profile_picture.size <= max_file_size:
                        img = Image.open(profile_picture)
                        img.verify()

                        if img.format.lower() in ["jpeg", "png", "jpg"]:
                            usersettings.profile_picture = profile_picture
                            usersettings.save()
                            messages.success(
                                request, "Successfully updated profile picture"
                            )
                        else:
                            messages.error(
                                request,
                                "Unsupported image format. We support only JPEG, JPG, PNG.",
                            )
                    else:
                        messages.error(request, "File size should be up to 10MB.")

                except (FileNotFoundError, Image.UnidentifiedImageError):
                    messages.error(request, "Invalid or unsupported image file")
            else:
                messages.error(request, "Invalid or unsupported image file")

            return render(
                request,
                "pages/settings/settings/_post_profile_pic.html",
                {"users_profile_picture": usersettings.profile_picture_url},
            )

        return render(request, "pages/settings/settings/preferences.html", context)

    context.update(
        {
            "sessions": [],  # Session.objects.filter(),
            "currency": usersettings.currency,
            "currency_signs": usersettings.CURRENCIES,
            "user_settings": usersettings,
        }
    )

    return render(request, "pages/settings/main.html", context)


def change_password(request: HttpRequest):
    if request.method == "POST":
        error: str = ""

        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if password != confirm_password:
            error = "Passwords don't match"

        if not password:
            error = "Something went wrong, no password was provided."

        if not error and len(password) > 128:
            error = "Password either too short, or too long. Minimum characters is eight, maximum is 128."

        if not error and len(password) < 8:
            error = "Password either too short, or too long. Minimum characters is eight, maximum is 128."

        if error:
            messages.error(request, error)
            return redirect("user settings change_password")

        request.user.set_password(password)
        request.user.save()
        update_session_auth_hash(request, request.user)
        messages.success(request, "Successfully changed your password.")
        return redirect("user settings")

    return render(request, "pages/reset_password.html", {"type": "change"})
