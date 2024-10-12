from django.db.models import Q
from django.shortcuts import render, redirect

from backend.models import QuotaLimit
from backend.core.types.htmx import HtmxHttpRequest


def fetch_all_quotas(request: HtmxHttpRequest, group: str):
    context = {}
    if not request.htmx:
        return redirect("quotas")

    search_text = request.GET.get("search")

    results = QuotaLimit.objects.filter(slug__startswith=group).prefetch_related("quota_overrides", "quota_usage").order_by("-slug")

    if search_text:
        results = results.filter(Q(name__icontains=search_text))

    quotas = [
        {
            "quota_limit": ql.get_quota_limit(request.user),
            "period_usage": ql.get_period_usage(request.user),
            "quota_object": ql,
        }
        for ql in results
    ]

    context.update({"quotas": quotas})
    return render(request, "pages/quotas/_fetch_body.html", context)
