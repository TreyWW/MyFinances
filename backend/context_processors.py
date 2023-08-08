import os
import subprocess
from django.http import HttpRequest

from .utils import Notification, Toast, Modals
from .models import *

Modals = Modals()


## Context processors need to be put in SETTINGS TEMPLATES to be recognized
def navbar(request: HttpRequest):
    # if request.user.is_authenticated:

    navbarItems = [
        {"tab_name": "Main", "tab_items": {

        }}
    ]
    context = {
        "navbar_items": navbarItems
    }

    context["modal_data_extra"] = [Modals.logout_confirm()]

    return context


def extras(request: HttpRequest):
    data = {
        "modal_data_extra": [Modals.create_customer(id="create_customer_nav", success_message="Customer created with the name of ${$('#nameInput').val()}.", toasts=[])]}

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


def notifications(request: HttpRequest):
    if request.user.is_authenticated:
        notifications = Notification.get_from_request(request)
        statuses = Errors.objects.filter(user=request.user).order_by('-date')

        if notifications:
            for notification in notifications:
                if request.user.is_authenticated:
                    if len(notification.get('message')) > 250:
                        break
                    error = Errors(user_id=request.user.id, error=notification.get('message'),
                                   error_colour=notification.get('colour'),
                                   error_code=notification.get('level'))
                    error.save()

        return {
            'notifications': notifications,
            'status_notifs': statuses,
            'status_notifs_new': notifications[0].get('colour') if notifications else False
        }
    return {}
