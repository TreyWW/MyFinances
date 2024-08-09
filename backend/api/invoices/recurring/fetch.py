from django.core.paginator import Paginator, EmptyPage
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods

from backend.decorators import web_require_scopes
from backend.models import InvoiceRecurringSet
from backend.service.invoices.common.fetch import get_context
from backend.types.requests import WebRequest


@require_http_methods(["GET"])
@web_require_scopes("invoices:read", True, True)
def fetch_all_recurring_invoices_endpoint(request: WebRequest):
    # Redirect if not an HTMX request
    if not request.htmx:
        return redirect("invoices:recurring:dashboard")

    invoices = InvoiceRecurringSet.filter_by_owner(owner=request.actor).filter(active=True)

    # Get filter and sort parameters from the request
    sort_by = request.GET.get("sort")
    sort_direction = request.GET.get("sort_direction", "")
    action_filter_type = request.GET.get("filter_type")
    action_filter_by = request.GET.get("filter")

    # Define previous filters as a dictionary
    previous_filters = {
        "status": {
            "ongoing": True if request.GET.get("status_ongoing") else False,
            "paused": True if request.GET.get("status_paused") else False,
            "cancelled": True if request.GET.get("status_cancelled") else False,
        }
    }

    context, _ = get_context(invoices, sort_by, previous_filters, sort_direction, action_filter_type, action_filter_by)

    previous_amount_filter = request.GET.get("amount_filter")

    amount_filter = previous_amount_filter if previous_amount_filter else action_filter_by if action_filter_type == "amount" else None

    if amount_filter:
        context["invoices"] = context["invoices"].filter(amount__gte=amount_filter)
        context["amount_filter"] = amount_filter

    paginator = Paginator(context["invoices"], 8)

    page_obj = paginator.get_page(request.GET.get("page"))

    context["page"] = page_obj
    context["paginator"] = paginator

    # Render the HTMX response
    return render(request, "pages/invoices/recurring/dashboard/_fetch_body.html", context)
