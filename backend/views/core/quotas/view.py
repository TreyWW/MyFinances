from django.http import HttpResponse, HttpRequest
from django.shortcuts import render

from backend.decorators import superuser_only
from backend.models import QuotaIncreaseRequest


def quotas_page(request: HttpRequest) -> HttpResponse:
    return render(request, "pages/quotas/dashboard.html")


def quotas_list(request: HttpRequest, group: str) -> HttpResponse:
    return render(request, "pages/quotas/list.html", {"group": group})


@superuser_only
def view_quota_increase_requests(request: HttpRequest) -> HttpResponse:
    requests = QuotaIncreaseRequest.objects.filter(status="pending").order_by("-created_at")
    return render(request, "pages/quotas/view_requests.html", {"requests": requests})
