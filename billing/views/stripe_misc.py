import stripe
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse, resolve, NoReverseMatch

from backend.decorators import web_require_scopes
from backend.core.types.requests import WebRequest

from billing.service.stripe_customer import get_or_create_customer_id


@web_require_scopes("billing:manage", api=True, htmx=True)
def customer_client_portal_endpoint(request: WebRequest):
    if NEXT := request.GET.get("back"):
        try:
            resolve(NEXT)
        except NoReverseMatch:
            NEXT = None

    customer_id = get_or_create_customer_id(request.actor)

    stripe_resp = stripe.billing_portal.Session.create(
        customer=customer_id, return_url=request.build_absolute_uri(NEXT or reverse("dashboard"))
    )

    if request.htmx:
        response = HttpResponse(status=200)
        response["HX-Redirect"] = stripe_resp.url
        return response

    return HttpResponseRedirect(stripe_resp.url)
