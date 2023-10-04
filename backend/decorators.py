from functools import wraps
from django.shortcuts import redirect

from functools import wraps
from django.shortcuts import redirect
from django.conf import settings

from backend.utils import Toast

from django.shortcuts import redirect


def not_authenticated(view_func):
    def wrapper_func(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("dashboard")
        else:
            return view_func(request, *args, **kwargs)

    return wrapper_func


def staff_only(view_func):
    def wrapper_func(request, *args, **kwargs):
        if request.user.is_staff and request.user.is_authenticated:
            return view_func(request, *args, **kwargs)
        else:
            notification = Notification(
                "warning",
                "You don't have permission to view this page.",
                colour="danger",
            )
            notification.add_to_request(request)
            return redirect("dashboard")

    return wrapper_func


def superuser_only(view_func):
    def wrapper_func(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        else:
            notification = Notification(
                "warning",
                "You don't have permission to view this page.",
                colour="danger",
            )
            notification.add_to_request(request)
            return redirect("dashboard")

    return wrapper_func


not_logged_in = not_authenticated
logged_out = not_authenticated
