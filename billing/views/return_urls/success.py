from django.contrib import messages
from django.shortcuts import redirect

from backend.types.requests import WebRequest


def stripe_success_return_endpoint(request: WebRequest):
    messages.warning(request, "SUCCESS RESPONSE")
    return redirect("billing:dashboard")
