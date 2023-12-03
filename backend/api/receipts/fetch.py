from django.db.models import Q
from django.http import HttpRequest, HttpResponseNotFound
from django.shortcuts import render, redirect

from backend.models import Receipt


def fetch_all_receipts(request: HttpRequest):
    context = {}
    if not request.htmx:
        return redirect("receipts dashboard")

    search_text = request.GET.get("search")
    if search_text:
        results = (
            Receipt.objects.filter(user=request.user)
            .filter(Q(name__icontains=search_text) | Q(date__icontains=search_text))
            .order_by("-date")
        )
    else:
        results = Receipt.objects.filter(user=request.user).order_by("-date")

    context.update({"receipts": results})
    return render(request, "pages/receipts/_search_results.html", context)
