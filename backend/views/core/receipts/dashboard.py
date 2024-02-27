from django.contrib.auth.decorators import login_required
from django.http import HttpRequest
from django.shortcuts import render

from backend.decorators import not_customer


@login_required
@not_customer
def receipts_dashboard(request: HttpRequest):
    return render(request, "pages/receipts/dashboard.html")
