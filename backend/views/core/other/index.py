from django.http import HttpRequest
from django.shortcuts import render


def index(request: HttpRequest):
    return render(request, 'core/pages/index.html')

    # login(request, User.objects.first())


def dashboard(request: HttpRequest):
    return render(request, 'core/pages/dashboard.html')