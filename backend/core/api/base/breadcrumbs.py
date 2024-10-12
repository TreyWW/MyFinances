from django.shortcuts import render

from backend.core.types.requests import WebRequest
from backend.core.service.base.breadcrumbs import get_breadcrumbs


def update_breadcrumbs_endpoint(request: WebRequest):
    url = request.GET.get("url")

    breadcrumb_dict: dict = get_breadcrumbs(url=url)
    return render(
        request,
        "base/breadcrumbs.html",
        {
            "breadcrumb": breadcrumb_dict.get("breadcrumb"),
            "swapping": True,
            # "swap": True
        },
    )
