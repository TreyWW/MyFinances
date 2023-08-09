from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpRequest, HttpResponseBadRequest, HttpResponseForbidden, \
    HttpResponseServerError
from django.shortcuts import render, redirect

from django.contrib.auth import get_user_model


def index(request: HttpRequest):
    messages.warning(request, f"logged in {request.user.username}" if request.user.is_authenticated else "not logged in")
    return render(request, 'core/pages/index.html')

@login_required
def dashboard(request: HttpRequest):
    return render(request, 'core/pages/dashboard.html')