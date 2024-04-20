from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from backend.models import QuotaLimit


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


def render_quota_error(request, quota_limit):
    messages.error(request, f"You have reached the quota limit for this service '{quota_limit.slug}'")
    return render(request, "partials/messages_list.html", {"autohide": False})


def render_quota_error_response(quota_limit):
    return HttpResponse(status=403, content=f"You have reached the quota limit for this service '{quota_limit.slug}'")
