from django.contrib.auth.hashers import check_password
from django.http import HttpRequest
from django.shortcuts import render

from backend.decorators import *
from backend.models import *


@not_authenticated
def set_password(request: HttpRequest, secret):
    SECRET_RETURNED = PasswordSecret.objects.all()
    SECRET_RETURNED.filter(expires__lte=timezone.now()).all().delete()

    for SECRET in SECRET_RETURNED:
        if check_password(secret, SECRET.secret):
            return render(request, "pages/reset_password.html", {"secret": secret})

    messages.error(request, "Invalid or expired password reset code")
    return redirect("dashboard")
