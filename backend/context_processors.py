from typing import List, Optional, Dict, Any

from django.http import HttpRequest
from django.urls import reverse

from settings.helpers import get_var


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

    data["git_branch"] = get_var("BRANCH")
    data["git_version"] = get_var("VERSION")
    data["import_method"] = get_var("IMPORT_METHOD", default="webpack")
    data["analytics"] = get_var("ANALYTICS_STRING")

    if hasattr(request, "htmx") and request.htmx.boosted:
        data["base"] = "base/htmx.html"

    return data


def breadcrumbs(request: HttpRequest):
    def get_item(name: str, url_name: Optional[str] = None, icon: Optional[str] = None) -> dict:
        """
        Create a breadcrumb item dictionary.

        Parameters:
        - name (str): The name of the breadcrumb item.
        - url_name (str): The URL name used for generating the URL using Django's reverse function.
        - icon (Optional[str]): The icon associated with the breadcrumb item (default is None).

        Returns:
        Dict[str, Any]: A dictionary representing the breadcrumb item.
        """
        return {
            "name": name,
            "url": reverse(url_name) if url_name else None,
            "icon": icon,
        }

    def generate_breadcrumbs(*breadcrumb_list: str) -> list[dict[Any, Any] | None]:
        """
        Generate a list of breadcrumb items based on the provided list of breadcrumb names.

        Parameters:
        - breadcrumb_list (str): Variable number of strings representing the names of the breadcrumbs.

        Returns:
        List[Dict[str, Any]]: A list of dictionaries representing the breadcrumb items.
        """
        return [all_items.get(breadcrumb) for breadcrumb in breadcrumb_list]

    current_url_name: str | Any = request.resolver_match.view_name  # type: ignore[union-attr]

    all_items: dict[str, dict] = {
        "dashboard": get_item("Dashboard", "dashboard", "house"),
        "invoices:dashboard": get_item("Invoices", "invoices:dashboard", "file-invoice"),
        "invoices:create": get_item("Create", "invoices:create"),
        "invoices:edit": get_item("Edit", None, "pencil"),
        "receipts dashboard": get_item("Receipts", "receipts dashboard", "file-invoice"),
        "user settings teams": get_item("Teams", "user settings teams", "users"),
        "user settings": get_item("Settings", "user settings", "gear"),
        "clients dashboard": get_item("Clients", "clients dashboard", "users"),
        "clients create": get_item("Create", "clients create"),
    }

    all_breadcrumbs: dict[str | None, list] = {
        "dashboard": generate_breadcrumbs("dashboard"),
        "user settings teams": generate_breadcrumbs("dashboard", "user settings teams"),
        "receipts dashboard": generate_breadcrumbs("dashboard", "receipts dashboard"),
        "invoices:dashboard": generate_breadcrumbs("dashboard", "invoices:dashboard"),
        "invoices:create": generate_breadcrumbs("dashboard", "invoices:dashboard", "invoices:create"),
        "invoices:edit": generate_breadcrumbs("dashboard", "invoices:dashboard", "invoices:edit"),
        "clients dashboard": generate_breadcrumbs("dashboard", "clients dashboard"),
        "clients create": generate_breadcrumbs("dashboard", "clients dashboard", "clients create"),
        "user settings": generate_breadcrumbs("dashboard", "user settings"),
    }

    return {"breadcrumb": all_breadcrumbs.get(current_url_name, [])}
