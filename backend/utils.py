from __future__ import annotations

from typing import Optional

from django.contrib import messages
from django.core.cache import cache
from django.core.cache.backends.redis import RedisCacheClient
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

cache: RedisCacheClient = cache

from backend.models import FeatureFlags, QuotaLimit


def get_feature_status(feature, should_use_cache=True):
    if should_use_cache:
        key = f"myfinances:feature_flag:{feature}"
        cached_value = cache.get(key)
        if cached_value:
            return cached_value

    value = FeatureFlags.objects.filter(name=feature).first()
    if value:
        if should_use_cache:
            cache.set(key, value.value, timeout=300)
        return value.value
    else:
        return False


def quota_usage_check_under(
    request, limit: str | QuotaLimit, extra_data: str | int | None = None, api=False, htmx=False, add: int = 0
) -> bool | HttpResponse | HttpResponseRedirect:
    try:
        quota_limit = QuotaLimit.objects.get(slug=limit) if isinstance(limit, str) else limit
    except QuotaLimit.DoesNotExist:
        return True

    if not quota_limit.strict_goes_above_limit(request.user, extra=extra_data, add=add):
        return True

    if api and htmx:
        messages.error(request, f"You have reached the quota limit for this service '{quota_limit.name}'")
        return render(request, "base/toast.html", {"autohide": False})
    elif api:
        return HttpResponse(status=403, content=f"You have reached the quota limit for this service '{quota_limit.name}'")
    messages.error(request, f"You have reached the quota limit for this service '{quota_limit.name}'")
    try:
        last_visited_url = request.session["last_visited"]
        current_url = request.build_absolute_uri()
        if last_visited_url != current_url:
            return HttpResponseRedirect(last_visited_url)
    except KeyError:
        pass
    return HttpResponseRedirect(reverse("dashboard"))


def set_cache(key, value, timeout=300):
    cache.set(key, value, timeout=timeout)


def get_cache(key):
    return cache.get(key)


def render_quota_error(request, quota_limit):
    messages.error(request, f"You have reached the quota limit for this service '{quota_limit.slug}'")
    return render(request, "partials/messages_list.html", {"autohide": False})


def render_quota_error_response(quota_limit):
    return HttpResponse(status=403, content=f"You have reached the quota limit for this service '{quota_limit.slug}'")


def redirect_to_last_visited(request, fallback_url="dashboard"):
    """
    Redirects user to the last visited URL stored in session.
    If no previous URL is found, redirects to the fallback URL.
    :param request: HttpRequest object
    :param fallback_url: URL to redirect to if no previous URL found
    :return: HttpResponseRedirect object
    """
    try:
        last_visited_url = request.session.get("last_visited", fallback_url)
        return HttpResponseRedirect(last_visited_url)
    except KeyError:
        return HttpResponseRedirect(fallback_url)
