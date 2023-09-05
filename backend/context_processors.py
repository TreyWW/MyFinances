import json
import os
import subprocess
from django.http import HttpRequest

from .utils import Notification, Toast, Modals, load_navbar_items
from .models import *
from django.core.cache import cache

Modals = Modals()


## Context processors need to be put in SETTINGS TEMPLATES to be recognized
def navbar(request):
    cached_navbar_items = cache.get('navbar_items')

    if cached_navbar_items is None:
        navbar_items = load_navbar_items()

        # Cache the sidebar items for a certain time (e.g., 3600 seconds = 1 hr)
        cache.set('navbar_items', navbar_items, 60 * 60 * 3)  # 3 hrs
    else:
        navbar_items = cached_navbar_items
    context = {"navbar_items": navbar_items}
    return context


def extras(request: HttpRequest):
    data = {}

    data['git_branch'] = os.environ.get('BRANCH')
    data['git_version'] = os.environ.get('VERSION')

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
