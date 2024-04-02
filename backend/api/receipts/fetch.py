from django.db.models import Q
from django.http import HttpRequest
from django.shortcuts import render, redirect

from backend.models_db.receipt import Receipt


def fetch_all_receipts(request: HttpRequest):
    context = {}
    if not request.htmx:
        return redirect("receipts dashboard")

    search_text = request.GET.get("search")

    results = Receipt.objects.order_by("-date")
    if request.user.logged_in_as_team:
        results = results.filter(organization=request.user.logged_in_as_team)
    else:
        results = results.filter(user=request.user)

    if search_text:
        results = results.filter(Q(name__icontains=search_text) | Q(date__icontains=search_text)).order_by("-date")

    context.update({"receipts": results})
    return render(request, "pages/receipts/_search_results.html", context)
