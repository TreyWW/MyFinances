from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods

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

    if request.user.logged_in_as_team:
        invoices = Invoice.objects.filter(organization=request.user.logged_in_as_team)
    else:
        invoices = Invoice.objects.filter(user=request.user)

    # Get filter and sort parameters from the request
    # sort_by = request.GET.get("sort")
    # sort_direction = request.GET.get("sort_direction", "")
    # action_filter_type = request.GET.get("filter_type")
    # action_filter_by = request.GET.get("filter")

    context, invoices = get_context(invoices)

    # Render the HTMX response
    return render(request, "pages/invoices/dashboard/_fetch_body.html", context)
