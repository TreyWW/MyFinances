from django.contrib import messages
from django.db.models import Q
from django.http import HttpRequest
from django.shortcuts import render
from django.views.decorators.http import require_GET
from django_ratelimit.core import is_ratelimited

from backend.decorators import feature_flag_check
from backend.models import Invoice


# @csrf_exempt
# @feature_flag_check("isInvoiceSchedulingEnabled", True, api=True)
# def create_schedule(request: HttpRequest):
#     option = request.POST.get("option")  # 1=one time 2=recurring
#
#     if option in ["1", "one-time", "onetime", "one"]:
#         ratelimited = (
#             is_ratelimited(request, group="create_schedule", key="user", rate="2/30s", increment=True)
#             or is_ratelimited(request, group="create_schedule", key="user", rate="5/m", increment=True)
#             or is_ratelimited(request, group="create_schedule", key="ip", rate="5/m", increment=True)
#             or is_ratelimited(request, group="create_schedule", key="ip", rate="10/h", increment=True)
#         )
#
#         if ratelimited:
#             messages.error(request, "Woah, slow down!")
#             return render(request, "base/toasts.html")
#         return create_ots(request)
#
#     messages.error(request, "Invalid option. Something went wrong.")
#     return render(request, "base/toasts.html")
#
#
# def create_ots(request: HttpRequest) -> HttpResponse:
#     invoice_id = request.POST.get("invoice_id") or request.POST.get("invoice")
#
#     try:
#         invoice = Invoice.objects.get(id=invoice_id)
#     except Invoice.DoesNotExist:
#         messages.error(request, "Invoice not found")
#         return render(request, "base/toasts.html")
#
#     if (request.user.logged_in_as_team and invoice.organization != request.user.logged_in_as_team) or (
#         not request.user.logged_in_as_team and invoice.user != request.user
#     ):
#         messages.error(request, "You do not have permission to create schedules for this invoice")
#         return render(request, "base/toasts.html")
#
#     print("[BACKEND] About to create ots", flush=True)
#     schedule = create_onetime_schedule(
#         CreateOnetimeScheduleInputData(
#             invoice=invoice, option=1, datetime=request.POST.get("date_time"), email_type=request.POST.get("email_type")
#         )
#     )
#
#     print(schedule, flush=True)
#
#     if isinstance(schedule, CreateOnetimeScheduleSuccessResponse):
#         messages.success(request, "Schedule created!")
#         return render(request, "pages/invoices/reminders/_table_row.html", {"schedule": schedule.schedule})
#
#     messages.error(request, schedule.message)
#     return render(request, "base/toasts.html")


@require_GET
@feature_flag_check("areInvoiceRemindersEnabled", True, api=True, htmx=True)
def fetch_reminders(request: HttpRequest, invoice_id: str):
    ratelimit = is_ratelimited(request, group="fetch_reminders", key="user", rate="20/30s", increment=True)
    if ratelimit:
        messages.error(request, "Too many requests")
        return render(request, "base/toasts.html")

    try:
        invoice = Invoice.objects.prefetch_related("invoice_reminders").get(id=invoice_id)
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

    schedules = invoice.invoice_reminders.order_by("reminder_type").only("id", "days", "reminder_type")

    action_filter_type = request.GET.get("filter_type")
    action_filter_by = request.GET.get("filter")

    # Define previous filters as a dictionary
    previous_filters = {
        "reminder_type": {
            "before_due": True if request.GET.get("reminder_type_before_due") else False,
            "after_due": True if request.GET.get("reminder_type_after_due") else False,
            "on_overdue": True if request.GET.get("reminder_type_on_overdue") else False,
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

    context["schedules"] = schedules.filter(or_conditions)

    return render(request, "pages/invoices/schedules/reminders/_table_body.html", context)
