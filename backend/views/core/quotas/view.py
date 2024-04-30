from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.cache import cache_page

from backend.decorators import superuser_only
from backend.models import QuotaIncreaseRequest, QuotaLimit
from backend.types.htmx import HtmxHttpRequest


def quotas_page(request: HtmxHttpRequest) -> HttpResponse:
    groups = sorted({g.split("-")[0] for g in QuotaLimit.objects.order_by("slug").values_list("slug", flat=True).distinct()})

    return render(
        request,
        "pages/quotas/dashboard.html",
        {"quotas": groups},
    )


def quotas_list(request: HtmxHttpRequest, group: str) -> HttpResponse:
    return render(request, "pages/quotas/list.html", {"group": group})


@superuser_only
def view_quota_increase_requests(request: HtmxHttpRequest) -> HttpResponse:
    requests = QuotaIncreaseRequest.objects.filter(status="pending").order_by("-created_at")
    return render(request, "pages/quotas/view_requests.html", {"requests": requests})
