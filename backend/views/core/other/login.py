from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpRequest, HttpResponseBadRequest, HttpResponseForbidden, \
    HttpResponseServerError
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login
from backend.decorators import *
from backend.utils import Notification, Toast
from backend.models import *

from django.contrib.auth import get_user_model, logout

User = get_user_model()


@csrf_exempt
@not_authenticated
def login_page(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        remember_me = request.POST.get('remember_me')

        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)
            if remember_me:
                request.session.set_expiry()
            LoginLog.objects.create(user=user)
            AuditLog.objects.create(user=user, action="Login")
            return redirect('index')
        else:
            # Add error message to be displayed in the login form
            return render(request, 'core/pages/login.html', {'attempted_email': email, 'error_messages': [{
                "colour": "danger",
                "level": "Error",
                "message": "Invalid username or password."
            }]})
    return render(request, 'core/pages/login.html')


@login_required
def logout_view(request, messages_constants=None):
    logout(request)

    messages.success(request, "You've now been logged out.")

    if request.method == "POST":
        return redirect('index')
    return redirect('index')


def create_account_page(request: HttpRequest):
    return render(request, 'core/pages/create_account.html')


def forgot_password_page(request: HttpRequest):
    return render(request, 'core/pages/forgot_password.html')
