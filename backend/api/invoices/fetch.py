from django.db.models import Q
from django.http import HttpRequest
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods

from backend.models import Invoice


@require_http_methods(["GET"])
def fetch_all_invoices(request: HttpRequest):
    # Redirect if not an HTMX request
    if not request.htmx:
        return redirect("invoices dashboard")

    context = {}

    # Get filter and sort parameters from the request
    sort_by = request.GET.get("sort")
    action_filter_type = request.GET.get("filter_type")
    action_filter_by = request.GET.get("filter")

    # Define previous filters as a dictionary
    previous_filters = {
        "payment_status": {
            "paid": True if request.GET.get("payment_status_paid") else False,
            "pending": True if request.GET.get("payment_status_pending") else False,
            "overdue": True if request.GET.get("payment_status_overdue") else False,
        }
    }

    # Validate and sanitize the sort_by parameter
    sort_by = (
        sort_by
        if sort_by
        in [
            "-date_due",
            "date_due",
            "id",
            "-id",
            "payment_status",
        ]
        else None
    )

    # Fetch invoices for the user, prefetch related items, and select specific fields
    invoices = (
        Invoice.objects.filter(user=request.user)
        .prefetch_related("items")
        .only("invoice_id", "id", "payment_status", "date_due")
        .filter()
    )

    # Initialize context variables
    context["selected_filters"] = []
    context["all_filters"] = {
        item: [i for i, _ in dictio.items()]
        for item, dictio in previous_filters.items()
    }

    # Initialize OR conditions for filters using Q objects
    or_conditions = Q()

    # Iterate through previous filters to build OR conditions
    for filter_type, filter_by_list in previous_filters.items():
        for filter_by, status in filter_by_list.items():
            # Determine if the filter was selected in the previous request
            was_previous_selection = True if status else False
            # Determine if the filter is selected in the current request
            has_just_been_selected = (
                True
                if action_filter_by == filter_by and action_filter_type == filter_type
                else False
            )

            # Check if the filter status has changed
            if (was_previous_selection and not has_just_been_selected) or (
                not was_previous_selection and has_just_been_selected
            ):
                # Construct filter condition dynamically based on filter_type
                filter_condition = {f"{filter_type}": filter_by}
                or_conditions |= Q(**filter_condition)
                context["selected_filters"].append(filter_by)

    # Apply OR conditions to the invoices queryset
    invoices = invoices.filter(or_conditions)

    # Apply sorting to the invoices queryset
    if sort_by:
        invoices = invoices.order_by(sort_by)
        context["sort"] = sort_by

    # Add invoices to the context
    context["invoices"] = invoices

    # Render the HTMX response
    return render(request, "pages/invoices/dashboard/_fetch_body.html", context)
