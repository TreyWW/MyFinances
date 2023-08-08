from django.http import HttpResponse, HttpRequest, HttpResponseBadRequest, HttpResponseForbidden, \
    HttpResponseServerError, JsonResponse

from backend.decorators import *
from backend.utils import Notification, Toast
from backend.models import *
from django.contrib.auth import get_user_model
from django.core.mail import EmailMessage
from django.contrib.auth.hashers import make_password, check_password
import re, json
from datetime import date, timedelta
from django.utils import timezone


User = get_user_model()


@not_authenticated
def set_password_set(request: HttpRequest, secret):
    password = request.POST.get('password')
    if password:
        SECRET_RETURNED = PasswordSecrets.objects.all()

        for SECRET in SECRET_RETURNED:
            if SECRET.expires < timezone.now():
                SECRET.delete()
            elif check_password(secret, SECRET.secret):
                USER = SECRET.user
                USER.set_password(password)
                USER.save()
                SECRET.delete()
                return JsonResponse({
                    'success': "Successfully set your password! Please login with the password you just set "
                               "and the email."})

        return JsonResponse({
            'error': "Invalid password code. The code has either expired or was not entered correctly."
                     "Please contact an administrator for support."},
            status=500)

    else:
        return JsonResponse({'error': "No code provided. Please contact an administrator for support."}, status=400)

    return redirect('login')
