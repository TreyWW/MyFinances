from uuid import uuid4

import requests
from datetime import datetime
import json

from backend.post_webhooks.helpers import generate_signature
from backend.models import WebhookDeliverySendLog, WebhookEventLog


def send_webhook(subscription, event_type, payload):
    headers = {
        "Content-Type": "application/json",
        "X-Hub-Signature-256": generate_signature(subscription.secret_key, json.dumps(payload)),
        "X-Timestamp": datetime.utcnow().isoformat(),
    }
    response = requests.post(subscription.url, data=json.dumps(payload), headers=headers, timeout=10)

    WebhookDeliverySendLog.objects.create(uuid=uuid4(), response_body=response.text, response_status_code=response.status_code)

    status = "success" if str(response.status_code).startswith("2") else "failed"
    WebhookEventLog.objects.filter(subscription=subscription).update(status=status)
