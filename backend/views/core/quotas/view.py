from django.http import HttpResponse, HttpRequest

from django.shortcuts import render


def quotas_page(request: HttpRequest) -> HttpResponse:
    return render(request, "pages/quotas/dashboard.html")


def quotas_list(request: HttpRequest, group: str) -> HttpResponse:
    return render(request, "pages/quotas/list.html", {"group": group})
