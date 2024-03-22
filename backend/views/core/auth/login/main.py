from typing import NoReturn

import django_ratelimit
from django.contrib.auth import login, logout
from django.contrib.auth.hashers import check_password
from django.http import HttpRequest
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import View
from django_ratelimit.decorators import ratelimit

from backend.decorators import *
from backend.models import LoginLog, User, VerificationCodes, AuditLog
from backend.views.core.auth.verify import create_magic_link
from settings.helpers import send_email
from .login.helpers import render_toast_message, ToastMessage


# from backend.utils import appconfig


class MagicLinkRequestView(View):
    @method_decorator(ratelimit(key="post:email", method=django_ratelimit.UNSAFE, rate="5/m"))
    @method_decorator(ratelimit(key="post:email", method=django_ratelimit.UNSAFE, rate="10/5m"))
    @method_decorator(ratelimit(key="ip", method=django_ratelimit.UNSAFE, rate="2/m"))
    @method_decorator(ratelimit(key="ip", method=django_ratelimit.UNSAFE, rate="3/10m"))
    @method_decorator(ratelimit(key="ip", method=django_ratelimit.UNSAFE, rate="6/1h"))
    def post(self, request: HttpRequest) -> HttpResponse:
        if request.user.is_authenticated:
            return redirect("dashboard")
        if not request.htmx:
            return redirect("auth:login")

        email = request.POST.get("email")
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return self.send_message(request)

        if not user.is_active:
            return self.send_message(request, "This account is not currently active.", False)

        magic_link, plain_token = create_magic_link(user, service="login")
        self.send_magic_link_email(request, user, magic_link.uuid, plain_token)
        self.send_message(request, should_redirect=False)
        return render(request, "pages/auth/magic_link_waiting.html", {"email": request.POST.get("email")})

    def send_message(
        self, request: HttpRequest, message: str = "", success: bool = True, should_redirect: bool = True
    ) -> HttpResponse | bool:
        message = message or "If this is a valid email address, we have sent you an email! Keep this tab open!"
        if success:
            messages.success(request, message)
        else:
            messages.error(request, message)

        if should_redirect:
            return render_toast_message(request)
        else:
            return True

    def send_magic_link_email(self, request: HttpRequest, user: User, uuid: str, plain_token: str) -> NoReturn:
        magic_link_url = request.build_absolute_uri(reverse("auth:login magic_link verify", kwargs={"uuid": uuid, "token": plain_token}))
        send_email(
            destination=user.email,
            subject="Login Request",
            message=f"""
            Hi {user.first_name if user.first_name else "User"},

            A login request was made on your MyFinances account. If this was not you, please ignore 
            this email.

            If you would like to login, please use the following link: \n {magic_link_url}
        """,
        )


def get_magic_link(uuid: str) -> VerificationCodes | None:
    try:
        return VerificationCodes.objects.get(uuid=uuid, service="login")
    except VerificationCodes.DoesNotExist:
        return None


class MagicLinkWaitingView(View):
    def post(self, request: HttpRequest) -> HttpResponse:
        if request.user.is_authenticated:
            return redirect("dashboard")
        if not request.htmx:
            return redirect("auth:login")
        return render(request, "pages/auth/magic_link_waiting.html", {"email": request.POST.get("email")})


class MagicLinkVerifyView(View):
    def get(self, request: HttpRequest, uuid: str, token: str) -> HttpResponse:
        if request.user.is_authenticated:
            return redirect("dashboard")

        magic_link = get_magic_link(uuid)

        magic_link_valid, magic_link_msg = is_magiclink_valid(magic_link, token)
        if not magic_link_valid:
            messages.error(request, magic_link_msg)
            return redirect("auth:login")

        return render(request, "pages/auth/magic_link_verify.html", {"uuid": uuid, "token": token})


class MagicLinkVerifyDecline(View):
    def post(self, request: HttpRequest, uuid: str, token: str) -> HttpResponse:
        if request.user.is_authenticated or not request.htmx:
            return redirect("dashboard")

        magic_link = get_magic_link(uuid)
        magic_link_valid, magic_link_msg = is_magiclink_valid(magic_link, token)

        if not magic_link_valid:
            return render_toast_message(request, ToastMessage(magic_link_msg))

        user = magic_link.user
        magic_link.delete()
        AuditLog.objects.create(user=user, action="magic link declined")
        messages.success(request, "Successfully declined the magic link verification request.")
        return render(request, "pages/auth/_magic_link_partial.html", {"declined": True})


class MagicLinkVerifyAccept(View):
    def post(self, request: HttpRequest, uuid: str, token: str) -> HttpResponse:
        if request.user.is_authenticated or not request.htmx:
            return redirect("dashboard")

        magic_link = get_magic_link(uuid)
        magic_link_valid, magic_link_msg = is_magiclink_valid(magic_link, token)

        if not magic_link_valid:
            messages.error(request, magic_link_msg)
            return render_toast_message(request)

        user = magic_link.user
        magic_link.delete()

        user.backend = "backend.auth_backends.EmailInsteadOfUsernameBackend"
        LoginLog.objects.create(user=user, service=LoginLog.ServiceTypes.MAGIC_LINK)
        AuditLog.objects.create(user=user, action="magic link accepted")
        login(request, magic_link.user)

        messages.success(request, "Successfully accepted the magic link verification request.")
        return render(request, "pages/auth/_magic_link_partial.html", {"accepted": True})


def is_magiclink_valid(magic_link: VerificationCodes, token: str) -> tuple[bool, str]:
    if not magic_link:
        return False, "Invalid magic link"

    if magic_link.is_expired():
        return False, "This link has expired"

    if not check_password(token, magic_link.token):
        return False, "Invalid magic link"

    return True, ""


def logout_view(request):
    logout(request)

    messages.success(request, "You've now been logged out.")

    return redirect("auth:login")  # + "?next=" + request.POST.get('next'))


@not_authenticated
def forgot_password_page(request: HttpRequest):
    if request.user.is_authenticated:
        return redirect("dashboard")
    return render(request, "pages/auth/forgot_password.html")
