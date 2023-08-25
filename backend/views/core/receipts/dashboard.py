from django.contrib.auth.decorators import login_required
from django.http import HttpRequest
from django.shortcuts import render


@login_required
def receipts_dashboard(request: HttpRequest):
    return render(request, "core/pages/receipts/dashboard.html", {})