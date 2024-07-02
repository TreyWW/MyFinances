from typing import List, Optional, Dict, Any

from django.http import HttpRequest
from django.urls import reverse

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
    def get_item(name: str, url_name: Optional[str] = None, icon: Optional[str] = None, kwargs: bool = False) -> dict:
        print(kwargs)
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
            "url": reverse(url_name, kwargs=request.resolver_match.kwargs if kwargs else {}) if url_name else "",
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
        return [get_item(*all_items.get(breadcrumb, (None, None, None))) for breadcrumb in breadcrumb_list if breadcrumb in all_items]

    current_url_name: str | Any = request.resolver_match.view_name  # type: ignore[union-attr]

    all_items: dict[str, tuple[str, Optional[str], Optional[str], bool]] = {
        "dashboard": ("Dashboard", "dashboard", "house"),
        "invoices:dashboard": ("Invoices", "invoices:dashboard", "file-invoice"),
        "invoices:create": ("Create", "invoices:create"),
        "invoices:edit": ("Edit", None, "pencil"),
        "receipts dashboard": ("Receipts", "receipts dashboard", "file-invoice"),
        "teams:dashboard": ("Teams", "teams:dashboard", "users"),
        "settings:dashboard": ("Settings", "settings:dashboard", "gear"),
        "clients:dashboard": ("Clients", "clients:dashboard", "users"),
        "clients:create": ("Create", "clients:create"),
        "onboarding:dashboard": ("Onboarding", "onboarding:dashboard", "rocket"),
        "onboarding:settings": ("Settings", "onboarding:settings", "gear"),
        "onboarding:form_builder": ("Form Builder", None, "table"),
        "onboarding:form_builder:edit": ("Edit", "onboarding:form_builder:edit", "pencil", True),
        "onboarding:form_builder:create": ("Create", "onboarding:form_builder:create", "plus"),
    }

    all_breadcrumbs: dict[str, str | tuple[str]] = {
        "dashboard": "dashboard",
        "teams:dashboard": ("dashboard", "teams:dashboard"),
        "receipts dashboard": ("dashboard", "receipts dashboard"),
        "invoices:dashboard": ("dashboard", "invoices:dashboard"),
        "invoices:create": ("dashboard", "invoices:dashboard", "invoices:create"),
        "invoices:edit": ("dashboard", "invoices:dashboard", "invoices:edit"),
        "clients:dashboard": ("dashboard", "clients:dashboard"),
        "clients:create": ("dashboard", "clients:dashboard", "clients:create"),
        "settings:dashboard": ("dashboard", "settings:dashboard"),
        "onboarding:dashboard": "onboarding:dashboard",
        "onboarding:settings": ("onboarding:dashboard", "onboarding:settings"),
        "onboarding:form_builder": ("onboarding:dashboard", "onboarding:form_builder"),
        "onboarding:form_builder:edit": ("onboarding:dashboard", "onboarding:form_builder", "onboarding:form_builder:edit"),
        "onboarding:form_builder:create": ("onboarding:dashboard", "onboarding:form_builder", "onboarding:form_builder:create"),
    }

    return {"breadcrumb": generate_breadcrumbs(*all_breadcrumbs.get(current_url_name, []))}
