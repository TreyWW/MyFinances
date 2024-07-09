from __future__ import annotations

import logging
from dataclasses import dataclass
from functools import wraps
from typing import Optional, TypedDict, List

from django.contrib import messages
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.shortcuts import render
from django.urls import reverse

from backend.models import QuotaLimit, TeamMemberPermission
from backend.types.requests import WebRequest
from backend.utils.feature_flags import get_feature_status

logger = logging.getLogger(__name__)


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


def htmx_only(viewname: str = "dashboard"):
    def decorator(view_func):
        def wrapper_func(request, *args, **kwargs):
            if request.htmx:
                return view_func(request, *args, **kwargs)
            else:
                return redirect(viewname)

        return wrapper_func

    return decorator


def hx_boost(view):
    """
    Decorator for HTMX requests.

    used by wrapping FBV in @hx_boost and adding **kwargs to param
    then you can use context = kwargs.get("context", {}) to continue and then it will handle HTMX boosts
    """

    @wraps(view)
    def wrapper(request, *args, **kwargs):
        if request.htmx.boosted:
            kwargs["context"] = kwargs.get("context", {}) | {"base": "base/htmx.html"}
        return view(request, *args, **kwargs)

    return wrapper


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
            try:
                last_visited_url = request.session["last_visited"]
                current_url = request.build_absolute_uri()
                if last_visited_url != current_url:
                    return HttpResponseRedirect(last_visited_url)
            except KeyError:
                pass
            return HttpResponseRedirect(reverse("dashboard"))

        return wrapper

    return decorator


class FlagItem(TypedDict):
    name: str
    desired: bool


def feature_flag_check_multi(flag_list: list[FlagItem], api=False, htmx=False):
    """
    Checks if at least one of the flags in the list is the desired status
    """

    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not any(get_feature_status(flag["name"]) == flag["desired"] for flag in flag_list):
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


def quota_usage_check(limit: str | QuotaLimit, extra_data: str | int | None = None, api=False, htmx=False):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            try:
                quota_limit = QuotaLimit.objects.get(slug=limit) if isinstance(limit, str) else limit
            except QuotaLimit.DoesNotExist:
                return view_func(request, *args, **kwargs)

            if not quota_limit.strict_goes_above_limit(request.user, extra=extra_data):
                return view_func(request, *args, **kwargs)

            if api and htmx:
                messages.error(request, f"You have reached the quota limit for this service '{quota_limit.slug}'")
                return render(request, "partials/messages_list.html", {"autohide": False})
            elif api:
                return HttpResponse(status=403, content=f"You have reached the quota limit for this service '{quota_limit.slug}'")
            messages.error(request, f"You have reached the quota limit for this service '{quota_limit.slug}'")
            try:
                last_visited_url = request.session["last_visited"]
                current_url = request.build_absolute_uri()
                if last_visited_url != current_url:
                    return HttpResponseRedirect(last_visited_url)
            except KeyError:
                pass
            return HttpResponseRedirect(reverse("dashboard"))

        return wrapper

    return decorator


not_logged_in = not_authenticated
logged_out = not_authenticated


def web_require_scopes(scopes: str | list[str], htmx=False, api=False, redirect_url=None):
    """
    Only to be used by WebRequests (htmx or html) NOT PUBLIC API
    """

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request: WebRequest, *args, **kwargs):
            if request.team_id and not request.team:
                return return_error(request, "Team not found")

            if request.team:
                # Check for team permissions based on team_id and scopes
                if not request.team.is_owner(request.user):
                    team_permissions = TeamMemberPermission.objects.filter(team=request.team, user=request.user).first()

                    if not team_permissions:
                        return return_error(request, "You do not have permission to perform this action")

                    # single scope
                    if isinstance(scopes, str) and scopes not in team_permissions.scopes:
                        return return_error(request, "You do not have permission to perform this action")

                    # scope list
                    if isinstance(scopes, list) and not all(scope in team_permissions.scopes for scope in scopes):
                        return return_error(request, "You do not have permission to perform this action")
            return view_func(request, *args, **kwargs)

        _wrapped_view.required_scopes = scopes
        return _wrapped_view

    def return_error(request: WebRequest, msg: str):
        logging.info(f"User does not have permission to perform this action (User ID: {request.user.id}, Scopes: {scopes})")
        if api and htmx:
            messages.error(request, msg)
            return render(request, "base/toast.html", {"autohide": False})
        elif api:
            return HttpResponse(status=403, content=msg)

        messages.error(request, msg)

        try:
            last_visited_url = request.session["last_visited"]
            current_url = request.build_absolute_uri()
            if last_visited_url != current_url:
                return HttpResponseRedirect(last_visited_url)
        except KeyError:
            pass

        if not redirect_url:
            return HttpResponseRedirect(reverse("dashboard"))

        try:
            return HttpResponseRedirect(reverse(redirect_url))
        except KeyError:
            return HttpResponseRedirect(reverse("dashboard"))

    return decorator
