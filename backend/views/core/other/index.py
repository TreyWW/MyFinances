from django.http import HttpRequest
from django.shortcuts import render
from backend.components.dashboard_chart import generate_chart

def index(request: HttpRequest):
    return render(request, "pages/index.html")

    # login(request, User.objects.first())


def dashboard(request: HttpRequest):
    script, chart = generate_chart()

    return render(request, "pages/dashboard.html", {
        'script': script,
        'chart': chart
    })
