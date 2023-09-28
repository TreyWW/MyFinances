from django.http import HttpRequest
from django.shortcuts import render
from django.utils import timezone
from backend.decorators import *
from backend.utils import Toasts
from backend.models import *

TOASTS = Toasts()

from django.contrib.auth.hashers import make_password, check_password


@not_authenticated
def set_password(request: HttpRequest, secret):
    SECRET_RETURNED = PasswordSecrets.objects.filter(secret=make_password(secret, salt=settings.SECRET_KEY)).all()
    for SECRET in SECRET_RETURNED:
        if SECRET.expires <= timezone.now():
            SECRET.delete()
            continue
        if check_password(secret, SECRET.secret):
            return render(request, 'core/pages/reset_password.html', {"secret": secret})

    messages.error(request, "Invalid or expired password reset code")
    return redirect('dashboard')
