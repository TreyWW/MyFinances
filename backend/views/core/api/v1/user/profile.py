from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpRequest, HttpResponseBadRequest, HttpResponseForbidden, \
    HttpResponseServerError, JsonResponse
from django.shortcuts import render, redirect
import google_auth_oauthlib.flow
from django.urls import reverse
from django.views.decorators.http import require_POST
from googleapiclient.discovery import build
from django.shortcuts import redirect
from django.contrib.auth import authenticate, login
from django.conf import settings
from django.utils.crypto import get_random_string
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

from backend.decorators import *
from backend.utils import Notification, Toast
import json
from backend.models import *

from django.contrib.auth import get_user_model, logout

User = get_user_model()

@login_required
@require_POST
def toggle_theme(request):
    user_profile = UserProfile.objects.get_or_create(user=request.user).first()

    # Toggle the dark_mode value
    user_profile.dark_mode = not user_profile.dark_mode
    user_profile.save()

    return JsonResponse({'dark_mode': user_profile.dark_mode})