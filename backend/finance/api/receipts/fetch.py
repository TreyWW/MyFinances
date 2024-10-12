from django.db.models import Q, QuerySet
from django.shortcuts import render, redirect

from backend.decorators import web_require_scopes
from backend.models import Receipt
from backend.core.types.htmx import HtmxHttpRequest


@web_require_scopes("receipts:read", True, True)
def fetch_all_receipts(request: HtmxHttpRequest):
    context: dict[str, QuerySet | list[str] | dict[str, list[str]]] = {}
    if not request.htmx:
        return redirect("receipts dashboard")

    search_text = request.GET.get("search")
    selected_filters = request.GET.get("filter")

    # Define previous filters as a dictionary
    previous_filters = {
        "amount": {
            "20": True if request.GET.get("amount_20+") else False,
            "50": True if request.GET.get("amount_50+") else False,
            "100": True if request.GET.get("amount_100+") else False,
        },
    }

    results = Receipt.objects.order_by("-date")
    if request.user.logged_in_as_team:
        results = results.filter(organization=request.user.logged_in_as_team)
    else:
        results = results.filter(user=request.user)

    if search_text:
        results = results.filter(
            Q(name__icontains=search_text)
            | Q(date__icontains=search_text)
            | Q(merchant_store__icontains=search_text)
            | Q(purchase_category__icontains=search_text)
            | Q(id__icontains=search_text)
        ).order_by("-date")
    elif selected_filters:
        context.update({"selected_filters": [selected_filters]})
        results = results.filter(total_price__gte=selected_filters).order_by("-date")

    context.update({"receipts": results})
    context["all_filters"] = {item: [i for i, _ in dictio.items()] for item, dictio in previous_filters.items()}
    return render(request, "pages/receipts/_search_results.html", context)
