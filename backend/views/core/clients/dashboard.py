from django.http import HttpRequest
from django.shortcuts import render


def clients_dashboard(request: HttpRequest):
    return render(request, "pages/clients/dashboard/dashboard.html")
