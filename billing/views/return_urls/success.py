from django.shortcuts import redirect

from backend.core.types.requests import WebRequest


def stripe_success_return_endpoint(request: WebRequest):
    return redirect("billing:dashboard")
