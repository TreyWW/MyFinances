from django.contrib.auth.decorators import login_required
from django.contrib.sessions.models import Session
from django.http import HttpResponse, HttpRequest, HttpResponseBadRequest, HttpResponseForbidden, \
    HttpResponseServerError
from django.shortcuts import render, redirect
import google_auth_oauthlib.flow
from django.urls import reverse
from googleapiclient.discovery import build
from django.shortcuts import redirect
from django.contrib.auth import authenticate, login, update_session_auth_hash
from django.conf import settings
from django.utils.crypto import get_random_string
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

from backend.decorators import *
from backend.utils import Notification, Toast
import json
from backend.models import *

from django.contrib.auth import get_user_model, logout


@login_required
def view_profile(request: HttpRequest):
    context = {}
    context['sessions'] = Session.objects.filter()
    return render(request, "core/pages/profile/main.html", context)

@login_required
def change_password(request: HttpRequest):
    if request.method == "POST":
        password = request.POST.get('password')
        if not password or 129 < len(password) > 7:
            messages.error(request, "Something went wrong, no password was provided." if not password else "Password either too short, or too long. Minimum characters is eight, maximum is 128.")
            return redirect("profile change_password")

        request.user.set_password(password)
        request.user.save()
        update_session_auth_hash(request, request.user)
        messages.success(request, "Successfully changed your password.")
        return redirect("profile")

    return render(request, "core/pages/reset_password.html", {"type": "change"})
