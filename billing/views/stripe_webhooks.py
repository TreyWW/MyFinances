import stripe
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response

from billing.billing_settings import STRIPE_WEBHOOK_ENDPOINT_SECRET
from billing.models import StripeWebhookEvent


@api_view(["POST", "GET"])
@authentication_classes([])
@permission_classes([AllowAny])
# @csrf_exempt
def stripe_listener_webhook_endpoint(request: Request):
    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE", "")

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, STRIPE_WEBHOOK_ENDPOINT_SECRET)
        print(event)
    except ValueError as error:
        print(f"Error parsing payload: {error}")
        return Response(status=400)
    except stripe.error.SignatureVerificationError as error:
        print(f"Error verifying webhook signature: {error}")
        return Response(status=400)

    StripeWebhookEvent.objects.create(event_id=event.id, event_type=event.type, data=event.data, raw_event=event)

    print(event.data)
    print(event.type)

    return Response(status=200)
