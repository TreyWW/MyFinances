from django.contrib.auth.decorators import login_required
from django.http import HttpRequest
from django.shortcuts import render
from backend.utils import Modals

Modals = Modals()


@login_required
def receipts_dashboard(request: HttpRequest):
    return render(request, "pages/receipts/dashboard.html")
