from dataclasses import dataclass
from functools import wraps
from typing import List

from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render

from backend.utils import get_feature_status


@dataclass
class FlagItem:
    name: str
    desired: bool


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
            messages.error(request, "You don't have permission to view this page.")
            return redirect("dashboard")

    return wrapper_func


def superuser_only(view_func):
    def wrapper_func(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        else:
            messages.error(request, "You don't have permission to view this page.")
            return redirect("dashboard")

    return wrapper_func


def feature_flag_check(flag, status=True, api=False, htmx=False):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            feat_status = get_feature_status(flag)

            if feat_status == status:
                return view_func(request, *args, **kwargs)

            if api and htmx:
                messages.error(request, "This feature is currently disabled.")
                return render(request, "base/toasts.html")
            elif api:
                return HttpResponse(status=403, content="This feature is currently disabled.")
            messages.error(request, "This feature is currently disabled.")
            return HttpResponseRedirect(request.META.get("HTTP_REFERER"))

        return wrapper

    return decorator


def feature_flag_check_multi(flag_list: List[FlagItem], api=False, htmx=False):
    """
    Checks if at least one of the flags in the list is the desired status
    """

    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not any(get_feature_status(flag.name) == flag.desired for flag in flag_list):
                if api and htmx:
                    messages.error(request, "This feature is currently disabled.")
                    return render(request, "base/toasts.html")
                elif api:
                    return HttpResponse(status=403, content="This feature is currently disabled.")
                messages.error(request, "This feature is currently disabled.")
                return HttpResponseRedirect(request.META.get("HTTP_REFERER"))

            return view_func(request, *args, **kwargs)

        return wrapper

    return decorator


not_logged_in = not_authenticated
logged_out = not_authenticated
