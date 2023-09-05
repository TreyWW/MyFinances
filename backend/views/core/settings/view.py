from django.contrib.auth.decorators import login_required
from django.contrib.sessions.models import Session
from django.http import HttpRequest
from django.shortcuts import render, redirect
from django.contrib.auth import update_session_auth_hash

from backend.decorators import *
from backend.models import *


@login_required
def settings_page(request: HttpRequest):
    context = {}
    
    usersettings, created = UserSettings.objects.get_or_create(user=request.user)

    if request.method == "POST":
        currency = request.POST.get('currency')
        if currency:
            usersettings.currency = currency
            usersettings.save()

    context.update ({
        'sessions': Session.objects.filter(),
        'currency': usersettings.currency,
        'currency_signs': usersettings.CURRENCIES
    })

    return render(request, "core/pages/settings/main.html", context)


@login_required
def change_password(request: HttpRequest):
    if request.method == "POST":
        password = request.POST.get('password')
        if not password or 129 < len(password) > 7:
            messages.error(request, "Something went wrong, no password was provided." if not password else "Password either too short, or too long. Minimum characters is eight, maximum is 128.")
            return redirect("user settings change_password")

        request.user.set_password(password)
        request.user.save()
        update_session_auth_hash(request, request.user)
        messages.success(request, "Successfully changed your password.")
        return redirect("user settings")

    return render(request, "core/pages/reset_password.html", {"type": "change"})
