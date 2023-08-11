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

@login_required
def invoices_dashboard(request: HttpRequest):
    # print(Client.objects.all())
    # Invoice.objects.create(user=request.user, client=Client.objects.first(), services="Test", hourly_rate=10, hours_worked=1, total_amount=10, due_date='2024-01-01')
    # print(Invoice.objects.all())
    return render(request, 'core/pages/invoices/dashboard/dashboard.html', {"invoices": Invoice.objects.filter(user=request.user)})

@login_required
def invoices_dashboard_id(request: HttpRequest, id):
    return render(request, 'core/pages/invoices/dashboard/dashboard.html', )