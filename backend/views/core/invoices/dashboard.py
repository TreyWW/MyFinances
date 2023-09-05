from django.contrib.auth.decorators import login_required
from django.db.models import Sum
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
    context = {}
    context["invoices"] = (Invoice.objects
                           .filter(user=request.user)
                           .prefetch_related("items")
                           .only("invoice_id", "id", "payment_status", "date_due"))

    return render(request, 'core/pages/invoices/dashboard/dashboard.html', context)


@login_required
def invoices_dashboard_id(request: HttpRequest, id):
    if id == "create":
        return redirect("invoices dashboard create")
    elif type(id) != "int":
        messages.error(request, "Invalid invoice ID")
        return redirect("invoices dashboard")
    invoices = Invoice.objects.get(id=id)
    if not invoices:
        return redirect('invoices dashboard')
    return render(request, 'core/pages/invoices/dashboard/dashboard.html', )
