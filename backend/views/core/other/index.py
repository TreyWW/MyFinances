from django.http import HttpRequest
from django.shortcuts import render
from login_required import login_not_required


def index(request: HttpRequest):
    return render(request, "pages/landing/index.html")


@login_not_required
def pricing(request: HttpRequest):
    return render(request, "pages/landing/pricing.html")


def dashboard(request: HttpRequest):
    return render(request, "pages/dashboard.html")
