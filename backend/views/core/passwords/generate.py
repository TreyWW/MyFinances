from django.core.exceptions import ValidationError
from django.http import HttpRequest
from django.shortcuts import redirect
from django.urls import reverse
from backend.models import *
from django.contrib.auth.hashers import make_password
from django.core.validators import validate_email
from datetime import date, timedelta


def set_password_generate(request: HttpRequest):
    if request.user.is_superuser and request.user.is_staff:
        pass
    else:
        return redirect('dashboard')

    USER = request.GET.get('id')
    NEXT = request.GET.get('next') or 'index'

    if not USER.isnumeric():
        messages.error(request, "User ID must be a valid integer")
        return redirect('dashboard')

    USER = User.objects.filter(id=USER).first()
    if USER:
        CODE = RandomCode(40)
        HASHED_CODE = make_password(CODE, salt=settings.SECRET_KEY)

        PWD_SECRET, created = PasswordSecrets.objects.update_or_create(
            user=USER,
            defaults={"expires": date.today() + timedelta(days=3), "secret" :HASHED_CODE}
        )
        PWD_SECRET.save()
        messages.error(request, f'Successfully created a code. <a href="{reverse("user set password", args=(CODE,))}">{CODE}</a>')
    else:
        messages.error(request, f'User not found')

    return redirect(NEXT)


#@not_logged_in
def password_reset(request: HttpRequest):
    EMAIL = request.GET.get('email')

    try:
        validate_email(EMAIL)
    except ValidationError as e:
        messages.error(request, "Invalid email provided.")
        return redirect('login')

    if EMAIL:
        USER = User.objects.filter(email=EMAIL).first()
        if USER:
            CODE = RandomCode(40)
            HASHED_CODE = make_password(CODE, salt=settings.SECRET_KEY)
            PasswordSecrets.objects.filter(user=USER).all().delete()

            PWD_SECRET = PasswordSecrets(
                user=USER,
                expires=date.today() + timedelta(days=3),
                secret=HASHED_CODE
            ).save()

            # [i.delete() for i in found]

            SEND_SENDGRID_EMAIL(USER.email, "My Finances | Password Reset",
                                f"You've now got a new password reset code. \n\n Reset Here: {request.build_absolute_uri(reverse('user set password', args=(CODE,)))}",
                                request=request)
        messages.success(request,
                         f"<strong>If this is a valid email address</strong> then we have sent you an email.\n Please check spam, if you cannot find the email press forgot password again.")
    return redirect("login")
