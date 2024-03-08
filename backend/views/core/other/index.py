from django.core.cache import cache
from django.http import HttpRequest
from django.shortcuts import render

from backend.decorators import not_customer


def index(request: HttpRequest):
    return render(request, "pages/index.html")

    # login(request, User.objects.first())


@not_customer
def dashboard(request: HttpRequest):
    return render(request, "pages/dashboard.html")
