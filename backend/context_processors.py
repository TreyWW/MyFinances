import json
import os
import subprocess
from django.http import HttpRequest
from django.urls import reverse

from .utils import Toast, Modals, load_navbar_items
from .models import *
from django.core.cache import cache

Modals = Modals()


## Context processors need to be put in SETTINGS TEMPLATES to be recognized
def navbar(request):
    cached_navbar_items = cache.get("navbar_items")

    if cached_navbar_items is None:
        navbar_items = load_navbar_items()

        # Cache the sidebar items for a certain time (e.g., 3600 seconds = 1 hr)
        cache.set("navbar_items", navbar_items, 60 * 60 * 3)  # 3 hrs
    else:
        navbar_items = cached_navbar_items
    context = {"navbar_items": navbar_items}
    return context


def extras(request: HttpRequest):
    data = {}

    data["git_branch"] = os.environ.get("BRANCH")
    data["git_version"] = os.environ.get("VERSION")
    data["modals"] = [
        # {
        #     "id": "logout_modal",
        #     "title": "Log out",
        #     "text": "Are you sure you would like to logout?",
        #     "action": {"text": "Log out", "type": "anchor", "href": reverse("logout")},
        # }
    ]

    return data


def toasts(request):
    if request.user.is_authenticated:
        toasts = Toast.get_from_request(request)
        return {
            "toasts": toasts,
        }
    return {}


def breadcrums(request):
    current_url_name = request.resolver_match.url_name
    all_items = {
        "dashboard": {
            "name": "Dashboard",
            "url": reverse("dashboard"),
            "icon": "house",
        },
        "invoices dashboard": {
            "name": "Invoices",
            "url": reverse("invoices dashboard"),
            "icon": "file-invoice",
        },
        "invoices dashboard create": {
            "name": "Create",
            "url": reverse("invoices dashboard create"),
            "icon": None,
        },
        "receipts dashboard": {
            "name": "Receipts",
            "url": reverse("receipts dashboard"),
            "icon": "file-invoice",
        },
        "user settings teams": {
            "name": "Teams",
            "url": reverse("user settings teams"),
            "icon": "users",
        },
        "user settings": {
            "name": "Settings",
            "url": reverse("user settings"),
            "icon": "gear",
        },
    }

    all_breadcrums = {
        "dashboard": [all_items.get("dashboard")],
        "user settings teams": [
            all_items.get("dashboard"),
            all_items.get("user settings teams"),
        ],
        "receipts dashboard": [
            all_items.get("dashboard"),
            all_items.get("receipts dashboard"),
        ],
        "invoices dashboard": [
            all_items.get("dashboard"),
            all_items.get("invoices dashboard"),
        ],
        "invoices dashboard create": [
            all_items.get("dashboard"),
            all_items.get("invoices dashboard"),
            all_items.get("invoices dashboard create"),
        ],
        "user settings": [
            all_items.get("dashboard"),
            all_items.get("user settings"),
        ],
    }

    return {"breadcrumb": all_breadcrums.get(current_url_name)}


def notifications(request):
    context: dict = {}
    if request.user.is_authenticated:
        notifications_qs = Notification.objects.filter(user=request.user)
        # modal_notifications = notifications_qs.filter(action="modal")
        #
        #     for modal_notif in modal_notifications.all():
        #         if not context.get("modal_data_context_processors"):
        #             context["modal_data_context_processors"] = []
        #
        #         try:
        #             modal_function = getattr(Modals, modal_notif.action_value)
        #             context["modal_data_context_processors"].append(modal_function())
        #         except AttributeError:
        #             print("Failed to find modal function")
        #
        context.update({"has_notifications": len(notifications_qs) > 0})
    return context
