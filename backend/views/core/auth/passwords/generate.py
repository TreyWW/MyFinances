from datetime import datetime, timedelta, date

from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.shortcuts import redirect
from django.urls import reverse, resolve, NoReverseMatch
from django.utils import timezone

from backend.models import *
from backend.types.htmx import HtmxHttpRequest


def msg_if_valid_email_then_sent(request):
    return messages.success(
        request,
        f"<strong>If this is a valid email address</strong> then we have sent you an email.\n Please check spam, if you cannot find the email press forgot password again.",
    )


def set_password_generate(request: HtmxHttpRequest):
    if not request.user.is_superuser or not request.user.is_staff:
        return redirect("dashboard")

    USER = request.GET.get("id")
    NEXT = request.GET.get("next") or "index"

    if USER is None or not USER.isnumeric():
        messages.error(request, "User ID must be a valid integer")
        return redirect("dashboard")

    USER_OBJ = User.objects.filter(id=USER).first()

    if not USER_OBJ:
        messages.error(request, f"User not found")
        return redirect("dashboard")
    CODE = RandomCode(40)
    HASHED_CODE = make_password(CODE, salt=settings.SECRET_KEY)

    PWD_SECRET, created = PasswordSecret.objects.update_or_create(
        user=USER_OBJ,
        defaults={"expires": date.today() + timedelta(days=3), "secret": HASHED_CODE},
    )
    PWD_SECRET.save()
    messages.error(
        request,
        f'Successfully created a code. <a href="{reverse("user set password", args=(CODE,))}">{CODE}</a>',
    )

    try:
        resolve(NEXT)
        return redirect(NEXT)
    except NoReverseMatch:
        return redirect("dashboard")


def password_reset(request: HtmxHttpRequest):
    EMAIL = request.POST.get("email")

    # if not EMAIL_SERVER_ENABLED:
    #     messages.error(request, "Unfortunately our email server is not currently available.")

    if not EMAIL:
        msg_if_valid_email_then_sent(request)
        return redirect("login forgot_password")

    try:
        validate_email(EMAIL)
    except ValidationError as e:
        msg_if_valid_email_then_sent(request)
        return redirect("login forgot_password")

    USER = User.objects.filter(email=EMAIL).first()

    if not USER:
        msg_if_valid_email_then_sent(request)
        return redirect("login forgot_password")

    PasswordSecret.objects.filter(user=USER).all().delete()

    CODE = RandomCode(40)
    HASHED_CODE = make_password(CODE)
    expires_date = date.today() + timedelta(days=3)
    expires_datetime = timezone.make_aware(datetime.combine(expires_date, datetime.min.time()))

    PasswordSecret.objects.create(user=USER, expires=expires_datetime, secret=HASHED_CODE)

    # SEND_SENDGRID_EMAIL(USER.email, "Password Reset" ,f"""
    #         My Finances | Password Reset
    #         You've now got a new password reset code.
    #
    #         Reset Here: {request.build_absolute_uri(reverse('user set password', args=(CODE,)))}
    # """, request=request)
    print(f"code is {CODE}")

    msg_if_valid_email_then_sent(request)

    return redirect("login forgot_password")
