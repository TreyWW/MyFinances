from django.contrib.auth import authenticate, login, logout
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db.models import Q
from django.http import HttpRequest
from django.shortcuts import render
from django.urls import resolve, Resolver404
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from backend.decorators import *
from backend.models import LoginLog, AuditLog, User
from backend.utils import get_feature_status

# from backend.utils import appconfig
from settings.settings import (
    SOCIAL_AUTH_GITHUB_ENABLED,
    SOCIAL_AUTH_GOOGLE_OAUTH2_ENABLED,
)


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
            "github_enabled": SOCIAL_AUTH_GITHUB_ENABLED,
            "google_enabled": SOCIAL_AUTH_GOOGLE_OAUTH2_ENABLED,
        },
    )


def logout_view(request):
    logout(request)

    messages.success(request, "You've now been logged out.")

    return redirect("auth:login")  # + "?next=" + request.POST.get('next'))


@not_authenticated
def forgot_password_page(request: HttpRequest):
    if request.user.is_authenticated:
        return redirect("dashboard")
    return render(request, "pages/login/forgot_password.html")
