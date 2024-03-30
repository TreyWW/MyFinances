from django.db.models import Q
from django.http import HttpRequest
from django.shortcuts import render, redirect

from backend.models import QuotaLimit


def fetch_all_quotas(request: HttpRequest, group: str):
    context = {}
    if not request.htmx:
        return redirect("quotas")

    search_text = request.GET.get("search")

    results = QuotaLimit.objects.filter(slug__startswith=group).prefetch_related("quota_overrides").order_by("-slug")

    if search_text:
        results = results.filter(Q(name__icontains=search_text))

    quota_list = zip(results, [q.get_quota_limit(user=request.user) for q in results])
    context.update({"quotas": quota_list})
    return render(request, "pages/quotas/_fetch_body.html", context)
