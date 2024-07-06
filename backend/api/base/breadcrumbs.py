from django.shortcuts import render

from backend.types.requests import WebRequest
from backend.service.base.breadcrumbs import get_breadcrumbs


def update_breadcrumbs_endpoint(request: WebRequest):
    breadcrumb_dict: dict = get_breadcrumbs(url=request.GET.get("url"))
    return render(
        request,
        "base/breadcrumbs.html",
        {
            "breadcrumb": breadcrumb_dict.get("breadcrumb"),
            # "swap": True
        },
    )
