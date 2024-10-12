from django.contrib import messages
from django.shortcuts import redirect

from backend.core.types.requests import WebRequest


def stripe_failed_return_endpoint(request: WebRequest):
    messages.warning(request, "FAILED RESPONSE")
    return redirect("billing:dashboard")
