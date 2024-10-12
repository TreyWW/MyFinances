from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods

from backend.decorators import web_require_scopes
from backend.finance.models import InvoiceRecurringProfile
from backend.core.service.invoices.common.fetch import get_context
from backend.core.types.requests import WebRequest


@require_http_methods(["GET"])
@web_require_scopes("invoices:read", True, True)
def fetch_all_recurring_invoices_endpoint(request: WebRequest):
    # Redirect if not an HTMX request
    if not request.htmx:
        return redirect("finance:invoices:recurring:dashboard")

    invoices = InvoiceRecurringProfile.filter_by_owner(owner=request.actor).filter(active=True)

    # Get filter and sort parameters from the request
    # sort_by = request.GET.get("sort")
    # sort_direction = request.GET.get("sort_direction", "")
    # action_filter_type = request.GET.get("filter_type")
    # action_filter_by = request.GET.get("filter")

    context, _ = get_context(invoices)

    paginator = Paginator(context["invoices"], 8)

    page_obj = paginator.get_page(request.GET.get("page"))

    context["page"] = page_obj
    context["paginator"] = paginator

    # Render the HTMX response
    return render(request, "pages/invoices/recurring/dashboard/_fetch_body.html", context)
