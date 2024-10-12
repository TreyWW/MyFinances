from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from login_required import login_not_required

from backend.core.service.invoices.recurring.webhooks.webhook_apikey_auth import authenticate_api_key

from backend.core.service.maintenance.expire.run import expire_and_cleanup_objects

import logging

from backend.core.types.requests import WebRequest

logger = logging.getLogger(__name__)


@require_POST
@csrf_exempt
@login_not_required
def handle_maintenance_now_endpoint(request: WebRequest):
    logger.info("Received routine cleanup handler. Now authenticating...")
    api_auth_response = authenticate_api_key(request)

    if api_auth_response.failed:
        logger.info(f"Maintenance auth failed: {api_auth_response.error}")
        return JsonResponse({"message": api_auth_response.error, "success": False}, status=api_auth_response.status_code or 400)

    cleanup_str = expire_and_cleanup_objects()
    logger.info(cleanup_str)
    return JsonResponse({"message": cleanup_str, "success": True}, status=200)
