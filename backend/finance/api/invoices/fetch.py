from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from datetime import datetime
from django.db.models import Q

from backend.decorators import web_require_scopes
from backend.finance.models import Invoice
from backend.core.types.htmx import HtmxHttpRequest
from backend.core.service.invoices.common.fetch import get_context


@require_http_methods(["GET"])
@web_require_scopes("invoices:read", True, True)
def fetch_all_invoices(request: HtmxHttpRequest):
    # Redirect if not an HTMX request
    if not request.htmx:
        return redirect("finance:invoices:single:dashboard")

    due_date = request.GET.get("due_date")
    invoice_id = request.GET.get("invoice-id")
    client_name = request.GET.get("client_name")
    amount = request.GET.get("amount")
    status = request.GET.get("status")

    query = Q()
    if invoice_id:
        query &= Q(id=invoice_id)
    if client_name:
        query &= Q(client_name__icontains=client_name)
    if amount:
        query &= Q(discount_amount__icontains=amount)
    if status:
        query &= Q(status=status)
    # If the time range filtering function is enabled, use this function to perform a time range search
    # if due_date:
    #     date_range = due_date.split(',')
    #     date_start = datetime.strptime(date_range[0], "%d/%m/%Y")
    #     date_end = datetime.strptime(date_range[1], "%d/%m/%Y")
    #     query &= Q(date_due__range=[date_start, date_end])

    if request.user.logged_in_as_team:
        invoices = Invoice.objects.filter(organization=request.user.logged_in_as_team).filter(query)
    else:
        invoices = Invoice.objects.filter(user=request.user).filter(query)

    # Get filter and sort parameters from the request
    # sort_by = request.GET.get("sort")
    # sort_direction = request.GET.get("sort_direction", "")
    # action_filter_type = request.GET.get("filter_type")
    # action_filter_by = request.GET.get("filter")

    context, invoices = get_context(invoices)

    # Render the HTMX response
    return render(request, "pages/invoices/dashboard/_fetch_body.html", context)
