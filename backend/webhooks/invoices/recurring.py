from datetime import datetime, timedelta

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from login_required import login_not_required

from backend.decorators import feature_flag_check
from backend.models import InvoiceRecurringSet, Invoice, DefaultValues, AuditLog
from backend.service.defaults.get import get_account_defaults
from backend.service.invoices.recurring.generation.next_invoice import generate_next_invoice_service
from backend.service.invoices.recurring.webhooks.webhook_apikey_auth import authenticate_api_key

import logging

from backend.types.requests import WebRequest
from settings.settings import AWS_TAGS_APP_NAME

logger = logging.getLogger(__name__)


@require_POST
@csrf_exempt
@login_not_required
# @feature_flag_check("isInvoiceSchedulingEnabled", True, api=True)
def handle_recurring_invoice_webhook_endpoint(request: WebRequest):
    """

    requires:
    - invoice_set_id
    """

    invoice_set_id = request.POST.get("invoice_set_id")

    logger.info("Received Scheduled Invoice. Now authenticating...")
    api_auth_response = authenticate_api_key(request)

    if api_auth_response.failed:
        return JsonResponse({"message": api_auth_response.error, "success": False}, status=api_auth_response.status_code or 400)

    invoice_recurring_set: InvoiceRecurringSet = InvoiceRecurringSet.objects.filter(pk=invoice_set_id).first()

    logger.info("Invoice Set found. Now processing...")

    DATE_TODAY = datetime.now().date()

    svc_resp = generate_next_invoice_service(invoice_recurring_set=invoice_recurring_set, issue_date=DATE_TODAY)

    if svc_resp.success:
        return JsonResponse({"message": "Invoice generated", "success": True})
    else:
        logger.info(svc_resp.error)
        return JsonResponse({"message": svc_resp.error, "success": False}, status=400)
