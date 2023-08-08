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

User = get_user_model()
TOASTS = Toasts()

from django.contrib.auth import get_user_model, logout
from django.core.mail import EmailMessage
from django.contrib.auth.hashers import make_password, check_password
from django.utils.safestring import mark_safe


@not_authenticated
def set_password(request: HttpRequest, secret):
    SECRET_RETURNED = PasswordSecrets.objects.filter(secret=make_password(secret, salt="bu11ingd0nS3crEt5")).all()
    for SECRET in SECRET_RETURNED:
        if check_password(secret, SECRET.secret):
            modal_data = [{
                'title': 'Set your password',
                "id": "set_modal",
                "submit_location": 'user set password set',
                "submit_location_secret": secret,
                'inputs': [
                    {'label': 'New Password',
                     'id': 'passwordInput', 'name': 'password',
                     'type': 'password'}
                ],
                'toasts': [
                    TOASTS.refresh()
                ],
                'success_message': 'Successfully set your password.',
                'submit_label': 'Set Password',
                'submit_colour': 'primary',
                'cancel': True
            }]
            return render(request, 'core/pages/login.html', {'modal_data': modal_data, 'set_password': True})

    return render(request, 'core/pages/login.html', {'error_messages': [{
        "colour": "danger",
        "level": "Error",
        "message": "Invalid code."
    }]})
