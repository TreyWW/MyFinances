from django.db.models import Prefetch, ExpressionWrapper, F, FloatField, Sum, Case, When, Q, Value, CharField
from django.utils import timezone

from backend.models import Invoice, InvoiceItem


def get_context(invoices, sort_by, sort_direction=True, action_filter_type=None, action_filter_by=None, previous_filters=None):
    context: dict = {}

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
                    filter_condition: dict[str, str | float] = {f"{filter_type}__gte": numeric_part}
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

    # Validate and sanitize the sort_by parameter
    all_sort_options = ["date_due", "id", "payment_status"]
    context["all_sort_options"] = all_sort_options

    # Apply sorting to the invoices queryset
    if sort_by not in all_sort_options:
        context["sort"] = "id"
    elif sort_by in all_sort_options:
        # True is for reverse order
        # first time set direction is none
        if sort_direction is not None and sort_direction.lower() == "true" or sort_direction == "":
            context["sort"] = f"-{sort_by}"
            context["sort_direction"] = False
            invoices = invoices.order_by(f"-{sort_by}")
        else:
            # sort_direction is False
            context["sort"] = sort_by
            context["sort_direction"] = True
            invoices = invoices.order_by(sort_by)

    # Add invoices to the context
    context["invoices"] = invoices

    return context, invoices
