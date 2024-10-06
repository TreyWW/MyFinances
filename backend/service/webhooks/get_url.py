import os

from django.urls import reverse


def get_global_webhook_response_url():
    return os.environ.get("SITE_URL", default="http://127.0.0.1:8000") + reverse("api:public:webhooks:receive_global")
