import json
import os
import subprocess
from django.http import HttpRequest
from django.urls import reverse

from .utils import Notification, Toast, Modals, load_navbar_items
from .models import *
from django.core.cache import cache

Modals = Modals()


## Context processors need to be put in SETTINGS TEMPLATES to be recognized
def navbar(request):
    cached_navbar_items = cache.get('navbar_items')

    if cached_navbar_items is None:
        navbar_items = load_navbar_items()

        # Cache the sidebar items for a certain time (e.g., 3600 seconds)
        cache.set('navbar_items', navbar_items, 60 * 60 * 3)
    else:
        navbar_items = cached_navbar_items
    context = {"navbar_items": navbar_items}
    return context


def extras(request: HttpRequest):
    data = {}

    if not request.user.is_authenticated:
        return data

    currency_symbol_cache = cache.get("currency_symbol")
    currency_cache = cache.get("currency")

    if currency_cache is None or currency_symbol_cache is None:
        user_settings, _ = UserSettings.objects.get_or_create(user=request.user)
        currency = user_settings.currency
        currency_symbol = UserSettings.CURRENCIES.get(currency, {}).get('symbol', '£')

        cache.set("currency_symbol", currency_symbol)
        cache.set("currency", currency)
    else:
        currency = currency_cache
        currency_symbol = currency_symbol_cache

    data.update({
        "currency": currency,
        "currency_symbol": currency_symbol
    })

    data['git_branch'] = os.environ.get('BRANCH')
    data['git_version'] = os.environ.get('VERSION')
    data['modals'] = [
        {"id": "logout_modal", "title": "Log out", "text": "Are you sure you would like to logout?", "action": {"text": "Log out", "type": "anchor", "href": reverse("logout")}}
    ]

    return data


def toasts(request):
    if request.user.is_authenticated:
        toasts = Toast.get_from_request(request)
        return {
            'toasts': toasts,
        }
    return {}

# def notifications(request: HttpRequest):
#     if request.user.is_authenticated:
#         notifications = Notification.get_from_request(request)
#         statuses = Errors.objects.filter(user=request.user).order_by('-date')
#
#         if notifications:
#             for notification in notifications:
#                 if request.user.is_authenticated:
#                     if len(notification.get('message')) > 250:
#                         break
#                     error = Errors(user_id=request.user.id, error=notification.get('message'),
#                                    error_colour=notification.get('colour'),
#                                    error_code=notification.get('level'))
#                     error.save()
#
#         return {
#             'notifications': notifications,
#             'status_notifs': statuses,
#             'status_notifs_new': notifications[0].get('colour') if notifications else False
#         }
#     return {}
