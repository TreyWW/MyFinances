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


@csrf_exempt
@not_authenticated
def login_page(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    #
    # user = User.objects.first()
    # login(request, user)
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        remember_me = request.POST.get('remember_me')

        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)
            LoginLog.objects.create(user=user)
            AuditLog.objects.create(user=user, action="Login")
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid username or password")
            return render(request, 'core/pages/login.html', {'attempted_email': email})
    return render(request, 'core/pages/login.html')


@login_required
def logout_view(request, messages_constants=None):
    logout(request)

    messages.success(request, "You've now been logged out.")

    if request.method == "POST":
        return redirect('dashboard')
    return redirect('dashboard')

def create_account_page(request: HttpRequest):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')
        password_confirm = request.POST.get('confirm_password')

        if password != password_confirm:
            messages.error(request, "Passwords don't match")
            return render(request, 'core/pages/create_account.html', {'attempted_email': email})

        emails_taken = (User.objects.filter(email=email).count() > 0) or (User.objects.filter(username=email).count() > 0)
        if emails_taken:
            messages.error(request, "Email is already taken")
            return render(request, 'core/pages/create_account.html')

        user = User.objects.create_user(email=email, username=email, password=password)
        user = authenticate(request, username=email, password=password)
        login(request, user)

        return redirect('dashboard')
    return render(request, 'core/pages/create_account.html')


@not_authenticated
def forgot_password_page(request: HttpRequest):
    if request.user.is_authenticated:
        return redirect('dashboard')
    code = request.GET.get('secret')

    return render(request, 'core/pages/forgot_password.html')
