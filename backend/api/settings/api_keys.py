from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from backend.service.api_keys.delete import delete_api_key
from backend.service.api_keys.generate import generate_public_api_key, get_permissions_from_request
from backend.service.api_keys.get import get_api_key_by_id
from backend.types.htmx import HtmxHttpRequest
from backend.api.public.models import APIAuthToken


@require_http_methods(["POST"])
def generate_api_key_endpoint(request: HtmxHttpRequest) -> HttpResponse:
    name = request.POST.get("name")
    expiry = request.POST.get("expiry")
    description = request.POST.get("description")

    permissions: list = get_permissions_from_request(request)

    key_obj, key_response = generate_public_api_key(
        request, request.user.logged_in_as_team or request.user, name, permissions, expires=expiry, description=description
    )

    if not key_obj:
        messages.error(request, key_response)
        return render(request, "base/toast.html")

    messages.success(request, "API key generated successfully")

    http_response = render(
        request,
        "pages/settings/settings/api_key_generated_response.html",
        {
            "raw_key": key_response,
            "name": name,
        },
    )

    http_response.headers["HX-Reswap"] = "beforebegin"
    http_response.headers["HX-Retarget"] = 'div[data-hx-container="api_keys"]'

    return http_response


@require_http_methods(["DELETE"])
def revoke_api_key_endpoint(request: HtmxHttpRequest, key_id: str) -> HttpResponse:
    key: APIAuthToken | None = get_api_key_by_id(request.user.logged_in_as_team or request.user, key_id)

    delete_key_response = delete_api_key(request, request.user.logged_in_as_team or request.user, key=key)

    if isinstance(delete_key_response, str):
        messages.error(request, "This key does not exist")
    else:
        messages.success(request, "Successfully revoked the API Key")
    return render(request, "base/toast.html")
