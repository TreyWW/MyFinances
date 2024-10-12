from datetime import datetime

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from login_required import login_not_required

from backend.finance.models import InvoiceRecurringProfile
from backend.core.service.invoices.recurring.generation.next_invoice import safe_generate_next_invoice_service
from backend.core.service.invoices.recurring.webhooks.webhook_apikey_auth import authenticate_api_key

import logging

from backend.core.types.requests import WebRequest

logger = logging.getLogger(__name__)


@require_POST
@csrf_exempt
@login_not_required
# @feature_flag_check("isInvoiceSchedulingEnabled", True, api=True)
def handle_recurring_invoice_webhook_endpoint(request: WebRequest):
    """

    requires:
    - invoice_profile_id
    """

    invoice_profile_id = request.POST.get("invoice_profile_id", "")

    logger.info("Received Scheduled Invoice. Now authenticating...")
    api_auth_response = authenticate_api_key(request)

    if api_auth_response.failed:
        logger.info(f"Webhook auth failed: {api_auth_response.error}")
        return JsonResponse({"message": api_auth_response.error, "success": False}, status=api_auth_response.status_code or 400)

    try:
        invoice_recurring_profile: InvoiceRecurringProfile = InvoiceRecurringProfile.objects.get(pk=invoice_profile_id, active=True)
    except InvoiceRecurringProfile.DoesNotExist:
        logger.error(f"Invoice recurring profile was not found (#{invoice_profile_id}). ERROR!")
        return JsonResponse({"message": "Invoice recurring profile not found", "success": False}, status=404)

    logger.info("Invoice recurring profile found. Now processing...")

    DATE_TODAY = datetime.now().date()

    svc_resp = safe_generate_next_invoice_service(invoice_recurring_profile=invoice_recurring_profile, issue_date=DATE_TODAY)

    if svc_resp.success:
        logger.info("Successfully generated next invoice")
        return JsonResponse({"message": "Invoice generated", "success": True})
    else:
        logger.info(svc_resp.error)
        return JsonResponse({"message": svc_resp.error, "success": False}, status=400)
