from django.contrib import messages
from django.db.models import Q
from django.http import HttpRequest
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.http import require_GET
from django_ratelimit.core import is_ratelimited

from backend.decorators import feature_flag_check
from backend.models import Invoice
from infrastructure.aws.schedules.list_schedules import list_schedules, ScheduleListResponse, ErrorResponse


@require_GET
@feature_flag_check("isInvoiceSchedulingEnabled", True, api=True, htmx=True)
def fetch_onetime_schedules(request: HttpRequest, invoice_id: str):
    # ratelimit = is_ratelimited(request, group="fetch_onetime_schedules", key="user", rate="5/30s", increment=True)
    # if ratelimit:
    #     messages.error(request, "Too many requests")
    #     return render(request, "base/toasts.html")

    try:
        invoice = Invoice.objects.prefetch_related("onetime_invoice_schedules").get(id=invoice_id)
    except Invoice.DoesNotExist:
        messages.error("Invoice not found")
        return render(request, "base/toasts.html")

    if not invoice.user.logged_in_as_team and invoice.user != request.user:
        messages.error("You do not have permission to view this invoice")
        return render(request, "base/toasts.html")

    if invoice.user.logged_in_as_team and invoice.organization != request.user.logged_in_as_team:
        messages.error("You do not have permission to view this invoice")
        return render(request, "base/toasts.html")

    context = {}

    schedules = invoice.onetime_invoice_schedules.order_by("due").only("id", "due", "status")

    action_filter_type = request.GET.get("filter_type")
    action_filter_by = request.GET.get("filter")

    # Define previous filters as a dictionary
    previous_filters = {
        "status": {
            "completed": True if request.GET.get("status_completed") else False,
            "pending": True if request.GET.get("status_pending") else False,
            "deleting": True if request.GET.get("status_deleting") else False,
            "cancelled": True if request.GET.get("status_cancelled") else False,
            "creating": True if request.GET.get("status_creating") else False,
            "failed": True if request.GET.get("status_failed") else False,
        }
    }

    # Initialize context variables
    context["selected_filters"] = []
    context["all_filters"] = {item: [i for i, _ in dictio.items()] for item, dictio in previous_filters.items()}

    # Initialize OR conditions for filters using Q objects
    or_conditions = Q()

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
                filter_condition = {f"{filter_type}": filter_by}
                or_conditions_filter |= Q(**filter_condition)
                context["selected_filters"].append(filter_by)

        # Combine OR conditions for each filter type with AND
        or_conditions &= or_conditions_filter

    # Apply OR conditions to the invoices queryset
    if request.GET.get("refresh-statuses"):
        ratelimited = (
            is_ratelimited(request, group="schedules-refresh-statuses", key="user", rate="2/30s", increment=True)
            or is_ratelimited(request, group="schedules-refresh-statuses", key="user", rate="5/m", increment=True)
            or is_ratelimited(request, group="schedules-refresh-statuses", key="ip", rate="5/m", increment=True)
            or is_ratelimited(request, group="schedules-refresh-statuses", key="ip", rate="10/h", increment=True)
        )

        if ratelimited:
            messages.error(request, "Woah, slow down!")

        aws_schedules: ScheduleListResponse = list_schedules()

        if isinstance(aws_schedules, ErrorResponse):
            messages.error(request, aws_schedules.message)
        else:
            # convert list of dictionaries to dictionary with key of ARN
            aws_schedules = {schedule["Arn"]: schedule for schedule in aws_schedules.schedules}

            for schedule in schedules:
                arn = schedule.stored_schedule_arn

                if not arn:
                    if schedule.status == "deleting":
                        schedule.status = "failed"
                    schedule.save()
                    continue

                if arn in aws_schedules:
                    if schedule.status != "pending" and schedule.status != "cancelled":
                        schedule.status = "pending"
                        schedule.save()
                else:  # Schedule doesn't exist on AWS
                    if schedule.status == "pending":
                        if schedule.due < timezone.now():
                            schedule.status = "failed"
                    elif schedule.status == "deleting":
                        schedule.status = "cancelled"
                    schedule.save()

    context["schedules"] = schedules.filter(or_conditions)

    return render(request, "pages/invoices/schedules/_table_body.html", context)
