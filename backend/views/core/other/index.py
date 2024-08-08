from django.http import HttpRequest
from django.shortcuts import render


def index(request: HttpRequest):
    return render(request, "pages/index.html")


def dashboard(request: HttpRequest):
    return render(request, "pages/dashboard.html")
