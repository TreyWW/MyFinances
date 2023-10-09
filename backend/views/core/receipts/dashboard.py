from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpRequest
from django.shortcuts import render, redirect
from django.urls import reverse_lazy

from backend.models import Receipt, UserSettings
from backend.utils import Modals

Modals = Modals()


@login_required
def receipts_dashboard(request: HttpRequest):
    context = {}

    if request.htmx:
        search_text = request.POST.get("search")
        if search_text:
            results = (
                Receipt.objects.filter(user=request.user)
                .filter(Q(name__icontains=search_text) | Q(date__icontains=search_text))
                .order_by("-date")
            )
        else:
            results = Receipt.objects.filter(user=request.user).order_by("-date")

        context.update({"receipts": results})
        return render(request, "core/pages/receipts/_search_results.html", context)

    context = {
        "receipts": Receipt.objects.filter(user=request.user).order_by("-date"),
    }

    return render(request, "core/pages/receipts/dashboard.html", context)
