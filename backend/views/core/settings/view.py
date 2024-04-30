from PIL import Image
from django.contrib.auth import update_session_auth_hash
from django.contrib.sessions.models import Session
from django.contrib import messages
from django.shortcuts import redirect
from django.shortcuts import render

from backend.models import UserSettings
from backend.types.htmx import HtmxHttpRequest


def settings_page(request: HtmxHttpRequest):
    context = {}

    try:
        usersettings = request.user.user_profile
    except UserSettings.DoesNotExist:
        # Create a new UserSettings object
        usersettings = UserSettings.objects.create(user=request.user)

    context.update(
        {
            "sessions": Session.objects.filter(),
            "currency_signs": usersettings.CURRENCIES,
            "currency": usersettings.currency,
        }
    )

    if request.method == "POST" and request.htmx:
        section = request.POST.get("section")

        if section == "profile_picture":
            profile_picture = request.FILES.get("profile_image")
            if profile_picture:
                try:
                    # Max file size is 10MB (Change the first number to determine the size in MB)
                    max_file_size = 10 * 1024 * 1024

                    if profile_picture.size is not None and profile_picture.size <= max_file_size:
                        img = Image.open(profile_picture)
                        img.verify()

                        if img.format is not None and img.format.lower() in ["jpeg", "png", "jpg"]:
                            usersettings.profile_picture = profile_picture
                            usersettings.save()
                            messages.success(request, "Successfully updated profile picture")
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
        }
    )

    return render(request, "pages/settings/main.html", context)


def change_password(request: HtmxHttpRequest):
    if request.method == "POST":
        current_password = request.POST.get("current_password")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        error = validate_password_change(request.user, current_password, password, confirm_password)

        if error:
            messages.error(request, error)
            return redirect("user settings change_password")

        # If no errors, update the password
        request.user.set_password(password)
        request.user.save()
        update_session_auth_hash(request, request.user)
        messages.success(request, "Successfully changed your password.")
        return redirect("user settings")

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
