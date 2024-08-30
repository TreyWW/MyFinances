import os

import stripe
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import redirect
from django.urls import reverse, resolve, NoReverseMatch

from backend.types.requests import WebRequest

import django


def customer_client_portal_endpoint(request: WebRequest):
    if NEXT := request.GET.get("back"):
        try:
            resolve(NEXT)
        except NoReverseMatch:
            NEXT = None
    stripe_resp = stripe.billing_portal.Session.create(
        customer=request.user.stripe_customer_id, return_url=request.build_absolute_uri(NEXT or reverse("dashboard"))
    )

    if request.htmx:
        response = HttpResponse(status=200)
        response["HX-Redirect"] = stripe_resp.url
        return response

    return HttpResponseRedirect(stripe_resp.url)
