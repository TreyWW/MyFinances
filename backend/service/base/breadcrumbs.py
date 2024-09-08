from typing import Optional, Any

from django.http import HttpRequest
from django.urls import resolve, reverse
from django.urls.exceptions import NoReverseMatch

ALL_ITEMS: dict[str, tuple[str, Optional[str], Optional[str]]] = {
    "dashboard": ("Dashboard", "dashboard", "house"),
    "invoices:dashboard": ("Invoices", "invoices:single:dashboard", "file-invoice"),
    "invoices:single:dashboard": ("Single", "invoices:single:dashboard", "file-invoice"),
    "invoices:single:create": ("Create (single)", "invoices:single:create", None),
    "invoices:recurring:create": ("Create (recurring)", "invoices:recurring:create", None),
    "invoices:single:edit": ("Edit", None, "pencil"),
    "receipts dashboard": ("Receipts", "receipts dashboard", "file-invoice"),
    "teams:dashboard": ("Teams", "teams:dashboard", "users"),
    "settings:dashboard": ("Settings", "settings:dashboard", "gear"),
    "clients:dashboard": ("Clients", "clients:dashboard", "users"),
    "clients:create": ("Create", "clients:create", None),
}

ALL_BREADCRUMBS: dict[str, str | tuple] = {
    "dashboard": "dashboard",
    "teams:dashboard": ("dashboard", "teams:dashboard"),
    "receipts dashboard": ("dashboard", "receipts dashboard"),
    "invoices:single:dashboard": ("dashboard", "invoices:dashboard", "invoices:single:dashboard"),
    "invoices:single:create": ("dashboard", "invoices:dashboard", "invoices:single:create"),
    "invoices:recurring:create": ("dashboard", "invoices:dashboard", "invoices:recurring:create"),
    "invoices:single:edit": ("dashboard", "invoices:dashboard", "invoices:single:edit"),
    "clients:dashboard": ("dashboard", "clients:dashboard"),
    "clients:create": ("dashboard", "clients:dashboard", "clients:create"),
    "settings:dashboard": ("dashboard", "settings:dashboard"),
}


def get_item(name: str, url_name: Optional[str] = None, icon: Optional[str] = None, kwargs: dict = {}, *, request=None) -> dict:
    """
    Create a breadcrumb item dictionary.
    Parameters:
    - name (str): The name of the breadcrumb item.
    - url_name (str): The URL name used for generating the URL using Django's reverse function.
    - icon (Optional[str]): The icon associated with the breadcrumb item (default is None).
    Returns:
    Dict[str, Any]: A dictionary representing the breadcrumb item.
    """

    if request:
        rev_kwargs = {kwarg: request.resolver_match.kwargs.get(kwarg) for url, kwarg in kwargs.items() if url == url_name if kwargs}
    else:
        rev_kwargs = {}
    return {
        "name": name,
        "url": reverse(url_name, kwargs=rev_kwargs if rev_kwargs else {}) if url_name else "",
        "icon": icon,
    }


def generate_breadcrumbs(*breadcrumb_list: str, request=None) -> list[dict[Any, Any] | None]:
    """
    Generate a list of breadcrumb items based on the provided list of breadcrumb names.
    Parameters:
    - breadcrumb_list (str): Variable number of strings representing the names of the breadcrumbs.
    Returns:
    List[Dict[str, Any]]: A list of dictionaries representing the breadcrumb items.
    """
    return [
        get_item(*ALL_ITEMS.get(breadcrumb, (None, None, None)), request=request)
        for breadcrumb in breadcrumb_list
        if breadcrumb in ALL_ITEMS
    ]


def get_breadcrumbs(*, request: HttpRequest | None = None, url: str | None = None):
    current_url_name: str | Any = request.resolver_match.view_name if request and request.resolver_match else None  # type: ignore[ union-attr]
    if url:
        try:
            current_url_name = resolve(url).view_name
        except NoReverseMatch:
            return {"breadcrumb": []}
    return {"breadcrumb": generate_breadcrumbs(*ALL_BREADCRUMBS.get(current_url_name, []), request=request)}
