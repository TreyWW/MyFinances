from textwrap import dedent

from django.contrib import messages
from django.contrib.auth.hashers import check_password
from django.shortcuts import redirect
from django.urls import reverse
from django.views.decorators.http import require_POST
from django_ratelimit.decorators import ratelimit

from backend.models import VerificationCodes, User, TracebackError
from settings import settings
from settings.helpers import send_email, ARE_EMAILS_ENABLED


def create_account_verify(request, uuid, token):
    object = VerificationCodes.objects.filter(uuid=uuid, service="create_account").first()

    if not object:
        messages.error(request, "Invalid URL")  # Todo: add some way a user can resend code?
        return redirect("auth:login create_account")

    if not object.is_active():
        messages.error(request, "This code has already expired")  # Todo: add some way a user can resend code?
        return redirect("auth:login create_account")

    if not object.user.awaiting_email_verification:
        messages.error(request, "Your email has already been verified. You can login.")
        return redirect("auth:login")

    if not check_password(token, object.token):
        messages.error(request, "This verification token is invalid.")
        return redirect("auth:login create_account")

    user = object.user
    user.is_active = True
    user.awaiting_email_verification = False
    user.save()
    object.delete()

    messages.success(request, "Successfully verified your email! You can now login.")
    return redirect("auth:login")


def create_magic_link(user: User, service: str) -> tuple[VerificationCodes, str]:
    magic_link = VerificationCodes.objects.create(user=user, service=service)
    token_plain = magic_link.token
    magic_link.hash_token()
    return magic_link, token_plain


@ratelimit(group="resend_verification_code", key="ip", rate="1/m")
@ratelimit(group="resend_verification_code", key="ip", rate="3/25m")
@ratelimit(group="resend_verification_code", key="ip", rate="10/6h")
@ratelimit(group="resend_verification_code", key="post:email", rate="1/m")
@ratelimit(group="resend_verification_code", key="post:email", rate="3/25m")
@require_POST
def resend_verification_code(request):
    email = request.POST.get("email")
    if not email:
        messages.error(request, "Invalid resend verification request")
        return redirect("auth:login")
    if not ARE_EMAILS_ENABLED:
        messages.error(request, "Emails are currently disabled.")
        TracebackError.objects.create(error="Emails are currently disabled.")
        return redirect("auth:login create_account")
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        messages.error(request, "Invalid resend verification request")
        return redirect("auth:login create_account")
    VerificationCodes.objects.filter(user=user, service="create_account").delete()
    magic_link = create_magic_link(user, "create_account")
    magic_link_url = settings.SITE_URL + reverse("auth:login create_account verify", kwargs={"uuid": magic_link.uuid, "token": token_plain})

    send_email(
        destination=email,
        subject="Verify your email",
        content=dedent(
            f"""
                Hi {user.first_name if user.first_name else "User"},

                Verification for your email has been requested to link this email to your MyFinances account.
                If this wasn't you, you can simply ignore this email.

                If it was you, you can complete the verification by clicking the link below.
                Verify Link: {magic_link_url}
            """
        ),
    )

    messages.success(request, "Verification email sent, check your inbox or spam!")
    return redirect("auth:login")
