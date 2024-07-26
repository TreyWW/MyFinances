from typing import List, Optional, Dict, Any

from django.http import HttpRequest
from django.urls import reverse

from backend.service.base.breadcrumbs import get_breadcrumbs

from settings.helpers import get_var

from backend import __version__


## Context processors need to be put in SETTINGS TEMPLATES to be recognized
def navbar(request):
    # cached_navbar_items = cache.get("navbar_items")

    # if cached_navbar_items is None:
    #     navbar_items = load_navbar_items()
    #
    #     # Cache the sidebar items for a certain time (e.g., 3600 seconds = 1 hr)
    #     cache.set("navbar_items", navbar_items, 60 * 60 * 3)  # 3 hrs
    # else:
    #     navbar_items = cached_navbar_items
    # context = {"navbar_items": navbar_items}
    return {}


def extras(request: HttpRequest):
    # import_method can be one of: "webpack", "public_cdn", "custom_cdn"
    data = {}

    data["version"] = __version__
    data["git_branch"] = get_var("BRANCH")
    data["git_version"] = get_var("VERSION")
    data["import_method"] = get_var("IMPORT_METHOD", default="webpack")
    data["analytics"] = get_var("ANALYTICS_STRING")

    if hasattr(request, "htmx") and request.htmx.boosted:
        data["base"] = "base/htmx.html"

    return data


def breadcrumbs(request: HttpRequest):
    return get_breadcrumbs(request=request)
