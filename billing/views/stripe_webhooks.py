import stripe
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from billing.billing_settings import STRIPE_WEBHOOK_ENDPOINT_SECRET
from billing.models import StripeWebhookEvent
from django.views.decorators.csrf import csrf_exempt


@api_view(["POST"])
@authentication_classes([])  # No auth required for webhooks
@permission_classes([AllowAny])
@csrf_exempt
def stripe_listener_webhook_endpoint(request: Request):
    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE", "")

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, STRIPE_WEBHOOK_ENDPOINT_SECRET)
        print(f"Webhook received: {event['type']}")
    except ValueError as error:
        print(f"Invalid payload: {error}")
        return Response(status=400)
    except stripe.error.SignatureVerificationError as error:
        print(f"Invalid signature: {error}")
        return Response(status=400)

    # Store event in database
    StripeWebhookEvent.objects.create(event_id=event.id, event_type=event["type"], data=event["data"], raw_event=event)

    # Call specific event handler (signal)
    return Response(status=200)
