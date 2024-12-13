from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from backend.core.api.public import APIAuthToken
from backend.core.service.api_keys.delete import delete_api_key
from backend.core.service.api_keys.generate import generate_public_api_key
from backend.core.service.api_keys.get import get_api_key_by_id
from backend.core.service.permissions.scopes import get_permissions_from_request

from backend.core.types.requests import WebRequest
from backend.decorators import web_require_scopes


@require_http_methods(["POST"])
@web_require_scopes("api_keys:write")
def generate_api_key_endpoint(request: WebRequest) -> HttpResponse:
    name = request.POST.get("name")
    expires = request.POST.get("expires")
    description = request.POST.get("description")
    administrator_toggle = True if request.POST.get("administrator") == "on" else False
    administrator_type = request.POST.get("administrator_type")

    permissions: list = get_permissions_from_request(request)

    key_obj, key_response = generate_public_api_key(
        request,
        request.user.logged_in_as_team or request.user,
        name,
        permissions,
        expires=expires,
        description=description,
        administrator_toggle=administrator_toggle,
        administrator_type=administrator_type,
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


@require_http_methods(["POST"])
@web_require_scopes("api_keys:write")
def regenerate_api_key_endpoint(request: WebRequest, key_id: str) -> HttpResponse:
    key: APIAuthToken | None = get_api_key_by_id(request.user.logged_in_as_team or request.user, key_id)

    if not key:
        messages.error(request, "API key not found")
        return render(request, "base/toast.html")

    delete_api_key(request, request.user.logged_in_as_team or request.user, key=key)

    key_obj, new_key_response = generate_public_api_key(
        request,
        request.user.logged_in_as_team or request.user,
        api_key_name=key.name,
        permissions=key.scopes,
        expires=key.expires,
        description=key.description,
        administrator_toggle=bool(key.administrator_service_type),
        administrator_type=key.administrator_service_type,
    )

    if not key_obj:
        messages.error(request, f"Failed to regenerate the API key: {new_key_response}")
        return render(request, "base/toast.html")

    messages.success(request, "API key regenerated successfully")

    http_response = render(
        request,
        "pages/settings/settings/api_key_generated_response.html",
        {
            "raw_key": new_key_response,
            "name": key.name,
        },
    )

    http_response.headers["HX-Reswap"] = "beforebegin"
    http_response.headers["HX-Retarget"] = 'div[data-hx-container="api_keys"]'

    return http_response


@require_http_methods(["DELETE"])
def revoke_api_key_endpoint(request: WebRequest, key_id: str) -> HttpResponse:
    key: APIAuthToken | None = get_api_key_by_id(request.user.logged_in_as_team or request.user, key_id)

    delete_key_response = delete_api_key(request, request.user.logged_in_as_team or request.user, key=key)

    if isinstance(delete_key_response, str):
        messages.error(request, "This key does not exist")
    else:
        messages.success(request, "Successfully revoked the API Key")
    return render(request, "base/toast.html")
