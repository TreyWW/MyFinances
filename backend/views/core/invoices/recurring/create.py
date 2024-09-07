from django.contrib import messages
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from backend.models import InvoiceRecurringProfile
from backend.decorators import web_require_scopes
from backend.service import BOTO3_HANDLER
from backend.service.asyn_tasks.tasks import Task
from backend.service.boto3.scheduler.create_schedule import create_boto_schedule
from backend.service.invoices.common.create.create import create_invoice_items
from backend.service.invoices.recurring.create.get_page import get_invoice_context
from backend.service.invoices.recurring.create.save import save_invoice
from backend.types.requests import WebRequest
from backend.views.core.invoices.handler import invoices_core_handler


@require_http_methods(["GET", "POST"])
def create_recurring_invoice_endpoint_handler(request: WebRequest):
    if request.method == "POST":
        return create_invoice_post_endpoint(request)
    return create_invoice_page_endpoint(request)


@require_http_methods(["GET"])
@web_require_scopes("invoices:read", False, False, "invoices:recurring:dashboard")
def create_invoice_page_endpoint(request: WebRequest):
    if not BOTO3_HANDLER.initiated:
        messages.error(request, "Something went wrong with the recurring service, please try again later or contact an administrator.")
        response = redirect("invoices:recurring:dashboard")
        return response
    context = get_invoice_context(request) | {"InvoiceRecurringProfile": InvoiceRecurringProfile}
    return invoices_core_handler(request, "pages/invoices/create/create_recurring.html", context)


@require_http_methods(["POST"])
@web_require_scopes("invoices:write", False, False, "invoices:recurring:dashboard")
def create_invoice_post_endpoint(request: WebRequest):
    invoice_items = create_invoice_items(request)
    invoice_response = save_invoice(request, invoice_items)
    if invoice_response.failed:
        messages.error(request, invoice_response.error_message)
        return invoices_core_handler(request, "pages/invoices/create/create_recurring.html", {"autohide": False})
    Task().queue_task(create_boto_schedule, invoice_response.response.pk)
    return redirect("invoices:recurring:dashboard")
