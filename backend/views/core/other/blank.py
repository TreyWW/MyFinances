from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpRequest, HttpResponseBadRequest, HttpResponseForbidden, \
    HttpResponseServerError
from django.shortcuts import render, redirect
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
from backend.utils import Notification, Toast
import json
from backend.models import *

from django.contrib.auth import get_user_model, logout

User = get_user_model()