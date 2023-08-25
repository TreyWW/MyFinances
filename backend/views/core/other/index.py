import os

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.http import HttpResponse, HttpRequest, HttpResponseBadRequest, HttpResponseForbidden, \
    HttpResponseServerError
from django.shortcuts import render, redirect

from django.contrib.auth import get_user_model, login
from backend.models import *
from django.contrib.sessions.models import Session


def index(request: HttpRequest):
    return render(request, 'core/pages/index.html')

    # login(request, User.objects.first())

import boto3
from django.conf import settings

@login_required()
def dashboard(request: HttpRequest):
    if request.method == "POST":
        img = request.FILES.get('filename')
        if img:
            receipt = Receipts.objects.create(
                user=request.user,
                name="test",
                image=img
            )
        else:
            print(f"No image found: {request.FILES}")
    return render(request, 'core/pages/dashboard.html', {'receipts': Receipts.objects.all()})