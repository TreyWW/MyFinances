from django.db.models import Prefetch, ExpressionWrapper, F, FloatField, Sum, Case, When, Q, Value, CharField, QuerySet
from django.utils import timezone

from backend.models import Invoice, InvoiceItem


def build_filter_condition(filter_type, filter_by):
    if "+" in filter_by:
        numeric_part = float(filter_by.split("+")[0])
        return {f"{filter_type}__gte": numeric_part}
    else:
        return {f"{filter_type}": filter_by}


def should_add_condition(was_previous_selection, has_just_been_selected):
    return (was_previous_selection and not has_just_been_selected) or (not was_previous_selection and has_just_been_selected)


def filter_conditions(or_conditions, previous_filters, action_filter_by, action_filter_type, context):
    for filter_type, filter_by_list in previous_filters.items():
        or_conditions_filter = Q()  # Initialize OR conditions for each filter type
        for filter_by, status in filter_by_list.items():
            # Determine if the filter was selected in the previous request
            was_previous_selection = bool(status)
            # Determine if the filter is selected in the current request
            has_just_been_selected = action_filter_by == filter_by and action_filter_type == filter_type

            # Check if the filter status has changed
            if should_add_condition(was_previous_selection, has_just_been_selected):
                # Construct filter condition dynamically based on filter_type
                filter_condition = build_filter_condition(filter_type, filter_by)
                or_conditions_filter |= Q(**filter_condition)
                context["selected_filters"].append(filter_by)

        # Combine OR conditions for each filter type with AND
        or_conditions &= or_conditions_filter

    return or_conditions, context


def get_context(
    invoices: QuerySet,
    sort_by: str | None,
    previous_filters: dict,
    sort_direction: str = "True",
    action_filter_type: str | None = None,
    action_filter_by: str | None = None,
) -> tuple[dict, QuerySet[Invoice]]:
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
        .select_related("client_to", "client_to__user", "user", "organization")
        # .only("invoice_id", "id", "payment_status", "date_due", "client_to", "client_name", "user", "organization")
        # .only was causing 100x more queries due to re-fetching extra fields
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

    if action_filter_by or action_filter_type:
        or_conditions, context = filter_conditions(or_conditions, previous_filters, action_filter_by, action_filter_type, context)

    invoices = invoices.filter(or_conditions)

    if action_filter_type == "id":
        invoices = invoices.filter(id=action_filter_by)
    elif action_filter_type == "recurring_profile_id":
        invoices = invoices.filter(invoice_recurring_profile=action_filter_by)

    # Validate and sanitize the sort_by parameter
    all_sort_options = ["end_date", "id", "status"]
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

    context["invoices"] = invoices

    return context, invoices
