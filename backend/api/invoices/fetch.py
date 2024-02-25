from django.db.models import (
    Q,
    Case,
    When,
    F,
    FloatField,
    ExpressionWrapper,
    CharField,
    Value,
    Sum,
    Prefetch,
)
from django.http import HttpRequest
from django.shortcuts import render, redirect
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from backend.models import Invoice, InvoiceItem


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
        },
        "amount": {
            "20+": True if request.GET.get("amount_20+") else False,
            "50+": True if request.GET.get("amount_50+") else False,
            "100+": True if request.GET.get("amount_100+") else False,
        },
    }

    # Validate and sanitize the sort_by parameter
    all_sort_options = ["date_due", "id", "payment_status"]
    context["all_sort_options"] = all_sort_options
    sort_by = sort_by if sort_by in all_sort_options else "id"

    # Fetch invoices for the user, prefetch related items, and select specific fields
    if request.user.logged_in_as_team:
        invoices = Invoice.objects.filter(organization=request.user.logged_in_as_team)
    else:
        invoices = Invoice.objects.filter(user=request.user)

    invoices = (
        invoices.prefetch_related(
            Prefetch(
                "items",
                queryset=InvoiceItem.objects.annotate(
                    subtotal=ExpressionWrapper(
                        F("hours") * F("price_per_hour"),
                        output_field=FloatField(),
                    ),
                ),
            ),
        )
        .select_related("client_to", "client_to__user")
        .only("invoice_id", "id", "payment_status", "date_due", "client_to", "client_name")
        .annotate(
            subtotal=Sum(F("items__hours") * F("items__price_per_hour")),
            amount=Case(
                When(vat_number=True, then=F("subtotal") * 1.2),
                default=F("subtotal"),
                output_field=FloatField(),
            ),
        )
        .distinct()  # just an extra precaution
    )

    # Initialize context variables
    context["selected_filters"] = []
    context["all_filters"] = {item: [i for i, _ in dictio.items()] for item, dictio in previous_filters.items()}

    # Initialize OR conditions for filters using Q objects
    or_conditions = Q()

    # Iterate through previous filters to build OR conditions
    for filter_type, filter_by_list in previous_filters.items():
        or_conditions_filter = Q()  # Initialize OR conditions for each filter type
        for filter_by, status in filter_by_list.items():
            # Determine if the filter was selected in the previous request
            was_previous_selection = True if status else False
            # Determine if the filter is selected in the current request
            has_just_been_selected = True if action_filter_by == filter_by and action_filter_type == filter_type else False

            # Check if the filter status has changed
            if (was_previous_selection and not has_just_been_selected) or (not was_previous_selection and has_just_been_selected):
                # Construct filter condition dynamically based on filter_type
                if "+" in filter_by:
                    numeric_part = float(filter_by.split("+")[0])
                    filter_condition = {f"{filter_type}__gte": numeric_part}
                else:
                    filter_condition = {f"{filter_type}": filter_by}
                or_conditions_filter |= Q(**filter_condition)
                context["selected_filters"].append(filter_by)

        # Combine OR conditions for each filter type with AND
        or_conditions &= or_conditions_filter

    # check/update payment status to make sure it is correct before invoices are filtered and displayed
    invoices.update(
        payment_status=Case(
            When(
                date_due__lt=timezone.now().date(),
                payment_status="pending",
                then=Value("overdue"),
            ),
            When(
                date_due__gt=timezone.now().date(),
                payment_status="overdue",
                then=Value("pending"),
            ),
            default=F("payment_status"),
            output_field=CharField(),
        )
    )

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
