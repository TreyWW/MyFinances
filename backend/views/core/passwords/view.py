import datetime
import math
import traceback

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpRequest, HttpResponseBadRequest, HttpResponseForbidden, \
    HttpResponseServerError
from django.shortcuts import render, redirect
import google_auth_oauthlib.flow
import google_auth_oauthlib.flow
import google_auth_oauthlib.flow
from django.urls import reverse
from django.utils import timezone
from googleapiclient.discovery import build
from django.shortcuts import redirect
from django.contrib.auth import authenticate, login
from django.conf import settings
from django.utils.crypto import get_random_string
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

from backend.decorators import *
from backend.utils import Notification, Toast, Toasts
import json
from backend.models import *

from django.contrib.auth import get_user_model, logout
TOASTS = Toasts()

from django.contrib.auth import get_user_model, logout
from django.core.mail import EmailMessage
from django.contrib.auth.hashers import make_password, check_password
from django.utils.safestring import mark_safe


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
    return redirect('index')
