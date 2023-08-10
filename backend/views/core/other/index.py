from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpRequest, HttpResponseBadRequest, HttpResponseForbidden, \
    HttpResponseServerError
from django.shortcuts import render, redirect

from django.contrib.auth import get_user_model, login
from backend.models import *
from django.contrib.sessions.models import Session


def index(request: HttpRequest):
    return render(request, 'core/pages/index.html')

    # login(request, User.objects.first())

@login_required()
def dashboard(request: HttpRequest):
    return render(request, 'core/pages/dashboard.html')