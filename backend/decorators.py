from functools import wraps
from typing import Optional

from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render

from backend.models import QuotaLimit
from backend.utils import get_feature_status


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


def quota_usage_check(limit: str | QuotaLimit, extra_data: Optional[str | int] = None, api=False, htmx=False):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            try:
                quota_limit = QuotaLimit.objects.get(slug=limit) if isinstance(limit, str) else limit
            except QuotaLimit.DoesNotExist:
                return view_func(request, *args, **kwargs)

            print(quota_limit.strict_goes_above_limit(request.user, extra=extra_data))

            if not quota_limit.strict_goes_above_limit(request.user, extra=extra_data):
                return view_func(request, *args, **kwargs)

            if api and htmx:
                messages.error(request, f"You have reached the quota limit for this service '{quota_limit.slug}'")
                return render(request, "base/toasts.html")
            elif api:
                return HttpResponse(status=403, content="fYou have reached the quota limit for this service '{quota_limit.slug}'")
            messages.error(request, f"You have reached the quota limit for this service '{quota_limit.slug}'")
            return HttpResponseRedirect(request.META.get("HTTP_REFERER"))

        return wrapper

    return decorator


not_logged_in = not_authenticated
logged_out = not_authenticated
