from django.contrib.sessions.models import Session
from django.http import HttpRequest
from django.shortcuts import render
from django.contrib.auth import update_session_auth_hash

from backend.decorators import *
from backend.models import *
from backend.utils import Modals

Modals = Modals()


def settings_page(request: HttpRequest):
    context = {}

    usersettings, created = UserSettings.objects.get_or_create(user=request.user)

    if request.method == "POST":
        currency = request.POST.get("currency")
        profile_picture = request.FILES.get("profile_image")

        if currency:
            if currency in usersettings.CURRENCIES:
                usersettings.currency = currency
                usersettings.save()
            else:
                messages.error(request, "Invalid currency")

        if profile_picture:
            usersettings.profile_picture = profile_picture
            usersettings.save()

    context.update(
        {
            "sessions": Session.objects.filter(),
            "currency": usersettings.currency,
            "currency_signs": usersettings.CURRENCIES,
            "user_settings": usersettings,
        }
    )

    return render(request, "core/pages/settings/main.html", context)


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

    return render(request, "core/pages/reset_password.html", {"type": "change"})
