from django.http import HttpRequest
from django.shortcuts import render
from django.urls import resolve, Resolver404
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login

import settings.settings
from backend.decorators import *
from backend.models import *

from django.contrib.auth import logout


@csrf_exempt
@not_authenticated
def login_page(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    #
    # user = User.objects.first()
    # login(request, user)
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        remember_me = request.POST.get("remember_me")

        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)
            LoginLog.objects.create(user=user)
            AuditLog.objects.create(user=user, action="Login")

            try:
                resolve(request.POST.get("next"))
                if request.POST.get("logout"):
                    redirect("dashboard")
                return redirect(request.POST.get("next"))
            except Resolver404:
                return redirect("dashboard")
        else:
            messages.error(request, "Invalid email or password")
            return render(request, "core/pages/login.html", {"attempted_email": email})

    github_enabled = (
        True
        if settings.SOCIAL_AUTH_GITHUB_KEY and settings.SOCIAL_AUTH_GITHUB_SECRET
        else False
    )
    google_enabled = (
        True
        if settings.SOCIAL_AUTH_GOOGLE_OAUTH2_KEY
        and settings.SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET
        else False
    )

    return render(
        request,
        "core/pages/login.html",
        {"github_enabled": github_enabled, "google_enabled": google_enabled},
    )


def logout_view(request):
    logout(request)

    messages.success(request, "You've now been logged out.")

    return redirect("login")  # + "?next=" + request.POST.get('next'))


def create_account_page(request: HttpRequest):
    if request.user.is_authenticated:
        return redirect("dashboard")
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        password_confirm = request.POST.get("confirm_password")

        if password != password_confirm:
            messages.error(request, "Passwords don't match")
            return render(
                request, "core/pages/create_account.html", {"attempted_email": email}
            )

        emails_taken = (User.objects.filter(email=email).count() > 0) or (
            User.objects.filter(username=email).count() > 0
        )
        if emails_taken:
            messages.error(request, "Email is already taken")
            return render(request, "core/pages/create_account.html")

        user = User.objects.create_user(email=email, username=email, password=password)
        user = authenticate(request, username=email, password=password)
        login(request, user)

        return redirect("dashboard")
    return render(request, "core/pages/create_account.html")


@not_authenticated
def forgot_password_page(request: HttpRequest):
    if request.user.is_authenticated:
        return redirect("dashboard")
    return render(request, "core/pages/forgot_password.html")
