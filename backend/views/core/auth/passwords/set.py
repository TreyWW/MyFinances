from django.contrib.auth.hashers import check_password
from django.http import (
    HttpRequest,
)
from django.views.decorators.http import require_POST

from backend.decorators import *
from backend.models import *


@not_authenticated
@require_POST
def set_password_set(request: HttpRequest, secret):
    password = request.POST.get("password", "")
    if len(password) > 7:
        SECRET_RETURNED = PasswordSecret.objects.all()

        for SECRET in SECRET_RETURNED:
            if SECRET.expires is not None and SECRET.expires < timezone.now():
                SECRET.delete()
                continue
            elif check_password(secret, SECRET.secret):
                USER = SECRET.user
                USER.set_password(password)
                USER.save()
                SECRET.delete()
                messages.success(request, "Successfully changed your password.")
                return redirect("auth:login")

        messages.error(
            request,
            "Invalid password code. The code has either expired or was not entered correctly."
            "Please contact an administrator for support.",
        )
        return redirect("auth:login")

    else:
        messages.error(request, "No code provided. Please contact an administrator for support.")
        return redirect("auth:login")

    messages.error(request, "Sorry, somethging went wrong!")
    return redirect("auth:login")
