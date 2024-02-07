import os
from typing import List, Optional, Dict, Any

from django.http import HttpRequest
from django.urls import reverse

from .utils import Toast, Modals

Modals = Modals()


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
    data = {}

    data["git_branch"] = os.environ.get("BRANCH")
    data["git_version"] = os.environ.get("VERSION")

    return data


def toasts(request):
    if request.user.is_authenticated:
        toasts = Toast.get_from_request(request)
        return {
            "toasts": toasts,
        }
    return {}


def breadcrumbs(request: HttpRequest):
    def get_item(name: str, url_name: str, icon: Optional[str] = None) -> dict:
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
            "url": reverse(url_name),
            "icon": icon,
        }

    def generate_breadcrumbs(*breadcrumb_list: str) -> List[Dict[str, Any]]:
        """
        Generate a list of breadcrumb items based on the provided list of breadcrumb names.

        Parameters:
        - breadcrumb_list (str): Variable number of strings representing the names of the breadcrumbs.

        Returns:
        List[Dict[str, Any]]: A list of dictionaries representing the breadcrumb items.
        """
        return [all_items.get(breadcrumb) for breadcrumb in breadcrumb_list]

    current_url_name: str = request.resolver_match.url_name

    all_items: Dict[str, dict] = {
        "dashboard": get_item("Dashboard", "dashboard", "house"),
        "invoices dashboard": get_item(
            "Invoices", "invoices dashboard", "file-invoice"
        ),
        "invoices dashboard create": get_item("Create", "invoices dashboard create"),
        "receipts dashboard": get_item(
            "Receipts", "receipts dashboard", "file-invoice"
        ),
        "user settings teams": get_item("Teams", "user settings teams", "users"),
        "user settings": get_item("Settings", "user settings", "gear"),
        "clients dashboard": get_item("Clients", "clients dashboard", "users"),
        "clients create": get_item("Create", "clients create"),
    }

    all_breadcrumbs: Dict[str, list] = {
        "dashboard": generate_breadcrumbs("dashboard"),
        "user settings teams": generate_breadcrumbs("dashboard", "user settings teams"),
        "receipts dashboard": generate_breadcrumbs("dashboard", "receipts dashboard"),
        "invoices dashboard": generate_breadcrumbs("dashboard", "invoices dashboard"),
        "invoices dashboard create": generate_breadcrumbs(
            "dashboard", "invoices dashboard", "invoices dashboard create"
        ),
        "clients dashboard": generate_breadcrumbs("dashboard", "clients dashboard"),
        "clients create": generate_breadcrumbs(
            "dashboard", "clients dashboard", "clients create"
        ),
        "user settings": generate_breadcrumbs("dashboard", "user settings"),
    }

    return {"breadcrumb": all_breadcrumbs.get(current_url_name, [])}
