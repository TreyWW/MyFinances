from django.contrib import messages
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db.models import Q
from django.shortcuts import redirect, render
from django.views import View

from backend.core.models import User
from backend.core.utils.feature_flags import get_feature_status
from settings.settings import (
    SOCIAL_AUTH_GITHUB_ENABLED,
    SOCIAL_AUTH_GOOGLE_OAUTH2_ENABLED,
)


class CreateAccountChooseView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect("dashboard")
        SIGNUPS_ENABLED = get_feature_status("areSignupsEnabled")
        if not SIGNUPS_ENABLED:
            messages.error(request, "New account signups are currently disabled")
            return redirect("auth:login")
        return render(
            request,
            "pages/auth/create_account_choose.html",
            {
                "github_enabled": SOCIAL_AUTH_GITHUB_ENABLED,
                "google_enabled": SOCIAL_AUTH_GOOGLE_OAUTH2_ENABLED,
            },
        )


class CreateAccountManualView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect("dashboard")
        SIGNUPS_ENABLED = get_feature_status("areSignupsEnabled")
        if not SIGNUPS_ENABLED:
            messages.error(request, "New account signups are currently disabled")
            return redirect("auth:login")
        return render(request, "pages/auth/create_account_manual.html")

    def post(self, request):
        if request.user.is_authenticated:
            return redirect("dashboard")
        SIGNUPS_ENABLED = get_feature_status("areSignupsEnabled")
        if not SIGNUPS_ENABLED:
            messages.error(request, "New account signups are currently disabled")
            return redirect("auth:login")

        email = request.POST.get("email")
        password = request.POST.get("password")
        password_confirm = request.POST.get("confirm_password")

        if password != password_confirm:
            messages.error(request, "Passwords don't match")
            return render(
                request,
                "pages/auth/create_account_manual.html",
                {"attempted_email": email},
            )

        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, "Invalid email")
            return render(request, "pages/auth/create_account_manual.html")

        emails_taken = User.objects.filter(Q(username=email) | Q(email=email)).exists()

        if emails_taken:
            messages.error(request, "Email is already taken")
            return render(request, "pages/auth/create_account_manual.html")

        if len(password) < 6:
            messages.error(request, "Password must be at least 6 characters")
            return render(request, "pages/auth/create_account_manual.html")

        created_user = User.objects.create_user(email=email, username=email, password=password)
        created_user.awaiting_email_verification = True
        created_user.save()
        # created_user.is_active = False
        # created_user.save()

        user = authenticate(request, username=email, password=password)
        if not user:
            messages.error(request, "Something went wrong")
            return render(request, "pages/auth/create_account_manual.html")

        # login(request, user)
        messages.success(
            request,
            "Successfully created account. Please verify your account via the email we are " "sending you now!",
        )
        return redirect("auth:login")
