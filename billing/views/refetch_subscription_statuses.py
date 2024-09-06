import stripe
from django.http import HttpResponse
from django.shortcuts import redirect

from backend.decorators import web_require_scopes
from backend.types.requests import WebRequest
from billing.service.refresh_subscriptions import refresh_actor_subscriptions


@web_require_scopes("billing:manage", api=True, htmx=True)
def refetch_subscriptions_endpoint(request: WebRequest):
    refresh_actor_subscriptions(request.actor)

    if request.htmx:
        response = HttpResponse()
        response["HX-Refresh"] = "true"
        return response
    return redirect("billing:dashboard")
