from django.contrib.auth import authenticate, login, logout
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db.models import Q
from django.http import HttpRequest
from django.shortcuts import render
from django.urls import resolve, Resolver404
from django.views import View
from django.views.decorators.csrf import csrf_exempt

import settings.settings
from backend.decorators import *
from backend.models import LoginLog, AuditLog, User


@csrf_exempt
@not_authenticated
def login_page(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        user = authenticate(request, username=email, password=password)

        if not user:
            messages.error(request, "Invalid email or password")
            return render(request, "pages/login/login.html", {"attempted_email": email})

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

    return render(
        request,
        "pages/login/login.html",
        {
            "github_enabled": settings.SOCIAL_AUTH_GITHUB_ENABLED,
            "google_enabled": settings.SOCIAL_AUTH_GOOGLE_OAUTH2_ENABLED,
        },
    )


def logout_view(request):
    logout(request)

    messages.success(request, "You've now been logged out.")

    return redirect("login")  # + "?next=" + request.POST.get('next'))


class CreateAccountChooseView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect("dashboard")
        return render(
            request,
            "pages/login/create_account_choose.html",
            {
                "github_enabled": settings.SOCIAL_AUTH_GITHUB_ENABLED,
                "google_enabled": settings.SOCIAL_AUTH_GOOGLE_OAUTH2_ENABLED,
            },
        )


class CreateAccountManualView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect("dashboard")
        return render(request, "pages/login/create_account_manual.html")

    def post(self, request):
        if request.user.is_authenticated:
            return redirect("dashboard")

        email = request.POST.get("email")
        password = request.POST.get("password")
        password_confirm = request.POST.get("confirm_password")

        if password != password_confirm:
            messages.error(request, "Passwords don't match")
            return render(
                request,
                "pages/login/create_account_manual.html",
                {"attempted_email": email},
            )

        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, "Invalid email")
            return render(request, "pages/login/create_account_manual.html")

        emails_taken = User.objects.filter(
            Q(username=email) | Q(email=email)
        ).exists()  # may want to change to "email" once we add email
        # backend for logins

        if emails_taken:
            messages.error(request, "Email is already taken")
            return render(request, "pages/login/create_account_manual.html")

        if len(password) < 6:
            messages.error(request, "Password must be at least 6 characters")
            return render(request, "pages/login/create_account_manual.html")

        User.objects.create_user(email=email, username=email, password=password)
        user = authenticate(request, username=email, password=password)
        if not user:
            messages.error(request, "Something went wrong")
            return render(request, "pages/login/create_account_manual.html")

        login(request, user)
        return redirect("dashboard")


@not_authenticated
def forgot_password_page(request: HttpRequest):
    if request.user.is_authenticated:
        return redirect("dashboard")
    return render(request, "pages/login/forgot_password.html")
