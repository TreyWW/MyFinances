from django.http import HttpResponse, HttpRequest, HttpResponseBadRequest, HttpResponseForbidden, \
    HttpResponseServerError, JsonResponse
from django.views.decorators.http import require_POST

from backend.decorators import *
from backend.utils import Notification, Toast
from backend.models import *
from django.contrib.auth import get_user_model
from django.core.mail import EmailMessage
from django.contrib.auth.hashers import make_password, check_password
import re, json
from datetime import date, timedelta
from django.utils import timezone


@not_authenticated
@require_POST
def set_password_set(request: HttpRequest, secret):
    password = request.POST.get('password')
    if len(password) > 7:
        SECRET_RETURNED = PasswordSecrets.objects.all()

        for SECRET in SECRET_RETURNED:
            if SECRET.expires < timezone.now():
                SECRET.delete()
                continue
            elif check_password(secret, SECRET.secret):
                USER = SECRET.user
                USER.set_password(password)
                USER.save()
                SECRET.delete()
                messages.success(request, "Successfully changed your password.")
                return redirect('login')

        messages.error(request, "Invalid password code. The code has either expired or was not entered correctly."
                                "Please contact an administrator for support.")
        return redirect('login')

    else:
        messages.error(request, "No code provided. Please contact an administrator for support.")
        return redirect('login')

    messages.error(request, "Sorry, somethging went wrong!")
    return redirect('login')
