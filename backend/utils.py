from typing import Optional

from django.contrib import messages
from django.core.cache import cache
from django.core.cache.backends.redis import RedisCacheClient
from django.http import HttpResponse, HttpResponseRedirect
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
    request, limit: str | QuotaLimit, extra_data: Optional[str | int] = None, api=False, htmx=False
) -> bool | HttpResponse | HttpResponseRedirect:
    try:
        quota_limit = QuotaLimit.objects.get(slug=limit) if isinstance(limit, str) else limit
    except QuotaLimit.DoesNotExist:
        return True

    if not quota_limit.strict_goes_above_limit(request.user, extra=extra_data):
        return True

    if api and htmx:
        messages.error(request, f"You have reached the quota limit for this service '{quota_limit.slug}'")
        return render(request, "base/toast.html")
    elif api:
        return HttpResponse(status=403, content=f"You have reached the quota limit for this service '{quota_limit.slug}'")
    messages.error(request, f"You have reached the quota limit for this service '{quota_limit.slug}'")
    referer = request.META.get("HTTP_REFERER")
    current_url = request.build_absolute_uri()
    if referer != current_url:
        return HttpResponseRedirect(referer)
    return HttpResponseRedirect(reverse("dashboard"))
