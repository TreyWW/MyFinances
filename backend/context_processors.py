from typing import List, Optional, Dict, Any

from django.http import HttpRequest
from django.urls import reverse

import calendar

from backend.core.service.base.breadcrumbs import get_breadcrumbs

from settings.helpers import get_var

from backend import __version__
from settings.settings import BASE_DIR, DEBUG


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
    data: Dict[str, Any] = {}

    import pathlib

    def get_git_revision(base_path):
        if not DEBUG:
            return "prod"

        git_dir = pathlib.Path(base_path) / ".git"

        # check file exists

        if not git_dir.exists() or not git_dir.is_dir() or not (git_dir / "HEAD").exists():
            return "commit not found"

        with (git_dir / "HEAD").open("r") as head:
            ref = head.readline().split(" ")[-1].strip()

        if not (git_dir / ref).exists():
            return "commit not found"

        with (git_dir / ref).open("r") as git_hash:
            return git_hash.readline().strip()

    data["version"] = __version__
    data["git_branch"] = get_var("BRANCH")
    data["git_version"] = get_git_revision(BASE_DIR)
    data["import_method"] = get_var("IMPORT_METHOD", default="webpack")
    data["analytics"] = get_var("ANALYTICS_STRING")
    data["calendar_util"] = calendar
    data["day_names_sunday_first"] = [calendar.day_name[(i + 6) % 7] for i in range(7)]
    data["day_names_monday_first"] = [day for day in calendar.day_name]

    if hasattr(request, "htmx") and request.htmx.boosted:
        data["base"] = "base/htmx.html"

    return data


def breadcrumbs(request: HttpRequest):
    return get_breadcrumbs(request=request)
