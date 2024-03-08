from django.http import HttpRequest
from django.shortcuts import render

from backend.decorators import not_customer


@not_customer
def clients_dashboard(request: HttpRequest):
    return render(request, "pages/clients/dashboard/dashboard.html")
