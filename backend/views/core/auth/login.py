from django.contrib.auth import authenticate, login, logout
from django.http import HttpRequest
from django.shortcuts import render
from django.urls import resolve, Resolver404, reverse
from django.views.decorators.http import require_GET, require_POST

from backend.decorators import *
from backend.models import LoginLog
# from backend.utils import appconfig
from settings.settings import (
    SOCIAL_AUTH_GITHUB_ENABLED,
    SOCIAL_AUTH_GOOGLE_OAUTH2_ENABLED,
)


@require_GET
@not_authenticated
def login_initial_page(request: HttpRequest):
    return render(
        request,
        "pages/auth/login_initial.html",
        {
            "github_enabled": SOCIAL_AUTH_GITHUB_ENABLED,
            "google_enabled": SOCIAL_AUTH_GOOGLE_OAUTH2_ENABLED,
        },
    )


# @csrf_exempt
@not_authenticated
@require_POST
@not_authenticated
def login_manual(request: HttpRequest):  # HTMX POST
    if not request.htmx:
        return redirect("auth:login")
    email = request.POST.get("email")

    return render(
        request,
        "pages/auth/login.html",
        context={"email": email},
    )


# @csrf_exempt
@not_authenticated
@require_POST
# @ratelimit(key="post:email", method=django_ratelimit.UNSAFE, rate="5/m")
# @ratelimit(key="post:email", method=django_ratelimit.UNSAFE, rate="10/5m")
# @ratelimit(key="ip", method=django_ratelimit.UNSAFE, rate="5/m")
@not_authenticated
def login_manual_2(request: HttpRequest):  # HTMX POST
    if not request.htmx:
        return redirect("auth:login")
    email = request.POST.get("email")
    password = request.POST.get("password")

    user = authenticate(request, username=email, password=password)

    if not user:
        messages.error(request, "Invalid email or password")
        return render(request, "pages/auth/login.html", {"attempted_email": email})

    if not user.is_active:
        if user.awaiting_email_verification:
            messages.error(request, f"""
                
                Your account is awaiting email verification
                <button hx-post='
                {request.build_absolute_uri(reverse("auth:login create_account verify resend"))}'
                hx-vals='{{"email": "{email}"}}'
                class='link link-success'>
                    click here to send a new verification email
                </a>.
            """)
        else:
            messages.error(request, "Your account is not currently active.")
        return render(request, "pages/auth/login.html", {"attempted_email": email})

    login(request, user)
    LoginLog.objects.create(user=user)
    # AuditLog.objects.create(user=user, action="Login")

    try:
        resolve(request.POST.get("next"))
        if request.POST.get("logout"):
            redirect("dashboard")
        return redirect(request.POST.get("next"))
    except Resolver404:
        return redirect("dashboard")

    print("using correct login")
    return render(
        request,
        "pages/auth/login.html"
    )


def logout_view(request):
    logout(request)

    messages.success(request, "You've now been logged out.")

    return redirect("auth:login")  # + "?next=" + request.POST.get('next'))


@not_authenticated
def forgot_password_page(request: HttpRequest):
    if request.user.is_authenticated:
        return redirect("dashboard")
    return render(request, "pages/auth/forgot_password.html")
