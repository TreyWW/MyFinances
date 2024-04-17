import json

from django.contrib import messages
from django.db.models import Q
from django.http import HttpResponse, HttpResponseForbidden, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods, require_POST, require_GET
from django_ratelimit.core import is_ratelimited
from mypy_boto3_iam.type_defs import GetRoleResponseTypeDef

from backend.decorators import feature_flag_check, quota_usage_check
from backend.models import Invoice, AuditLog, APIKey, InvoiceOnetimeSchedule, InvoiceURL, QuotaUsage
from backend.types.emails import SingleEmailInput
from backend.types.htmx import HtmxHttpRequest
from backend.utils import quota_usage_check_under
from infrastructure.aws.handler import get_iam_client
from infrastructure.aws.schedules.create_schedule import (
    create_onetime_schedule,
    CreateOnetimeScheduleInputData,
    SuccessResponse as CreateOnetimeScheduleSuccessResponse,
)
from infrastructure.aws.schedules.delete_schedule import delete_schedule, DeleteScheduleResponse, ErrorResponse
from infrastructure.aws.schedules.list_schedules import list_schedules, ScheduleListResponse, ErrorResponse as ListSchedulesErrorResponse
from settings.helpers import send_email
from settings.settings import AWS_TAGS_APP_NAME


import logging

logger = logging.getLogger(__name__)


@require_POST
@csrf_exempt
@feature_flag_check("isInvoiceSchedulingEnabled", True, api=True)
def receive_scheduled_invoice(request: HtmxHttpRequest):
    """

    Should return {"success": False, "message": "...", "status": ...} if an error occurred.

    Otherwise, return {
        "success": True
    }

    """
    logger.debug("Received Scheduled Invoice. Now authenticating...")
    valid, reason, status = authenticate_api_key(request)

    if not valid:
        return JsonResponse({"message": reason, "success": False}, status=status)

    invoice_id = request.POST.get("invoice_id") or request.headers.get("invoice_id")
    schedule_id = request.POST.get("schedule_id") or request.headers.get("schedule_id")
    schedule_type = request.POST.get("schedule_type") or request.headers.get("schedule_type")
    email_type = request.POST.get("email_type") or request.headers.get("email_type")

    if not invoice_id or not schedule_id or not schedule_type:
        return JsonResponse({"success": False, "message": "Missing invoice_id or schedule_id or schedule_type"}, status=400)

    try:
        invoice = (
            Invoice.objects.select_related("client_to", "organization", "user")
            .prefetch_related("onetime_invoice_schedules")
            .get(id=invoice_id)
        )
    except Invoice.DoesNotExist:
        return JsonResponse({"success": False, "message": "Invoice not found"}, status=404)

    logger.debug(f"Invoice found: {invoice}")

    try:
        schedule_type = int(schedule_type)
        if schedule_type not in [1, 2]:
            raise ValueError
    except ValueError:
        return JsonResponse({"success": False, "message": "Invalid schedule_type. Must be an integer; 1=one-time, 2=recurring"}, status=400)

    if schedule_type == 1:
        schedule = invoice.onetime_invoice_schedules.get(id=schedule_id)
    else:
        return JsonResponse({"success": False, "message": "Invalid schedule_type. Must be an integer; 1=one-time, 2=recurring"}, status=400)

    if email_type == "client_email":
        email = invoice.client_email
    elif invoice.client_to:
        email = invoice.client_to.email
    else:
        email = None

    if not email:
        return JsonResponse({"success": False, "message": "No client email address stored", "status": 400})

    invoice_url_object = InvoiceURL.objects.create(
        invoice=invoice,
        system_created=True,
        never_expire=True,
    )

    invoice_url = request.build_absolute_uri(reverse("invoices view invoice", kwargs={"uuid": invoice_url_object.uuid}))

    AuditLog.objects.create(action=f"scheduled invoice: {invoice_id} send to {email_type} - {email}")

    client_name = invoice.client_name or invoice.client_to.name or "there"
    # Todo: add better email message
    email_response = send_email(
        SingleEmailInput(
            destination=email,
            subject=f"Invoice #{invoice_id} ready",
            content=f"""
                Hi {client_name},

                This is an automated email to let you know that your invoice #{invoice_id} is now ready. The due date is {invoice.date_due}.

                You can view the invoice here: {invoice_url}

                Best regards

                Note: This is an automated email sent out by MyFinances on behalf of '{invoice.self_company or invoice.self_name}'. If you
                believe this is spam or fraudulent please report it to us and DO NOT pay the invoice. Once a report has been made you will
                have a case opened.
            """,
        )
    )

    if not email_response.success:
        schedule.status = schedule.StatusTypes.FAILED
        schedule.received = False
        schedule.save()
        return JsonResponse({"success": False, "message": f"Failed to send email: {email_response.message}"}, status=500)

    schedule.status = schedule.StatusTypes.COMPLETED
    schedule.received = True
    schedule.save()

    return JsonResponse({"success": True})


@csrf_exempt
@feature_flag_check("isInvoiceSchedulingEnabled", True, api=True)
def create_schedule(request: HtmxHttpRequest):
    option = request.POST.get("option")  # 1=one time 2=recurring

    if option in ["1", "one-time", "onetime", "one"]:
        ratelimited: bool = (
            is_ratelimited(request, group="create_schedule", key="user", rate="2/30s", increment=True)
            or is_ratelimited(request, group="create_schedule", key="user", rate="5/m", increment=True)
            or is_ratelimited(request, group="create_schedule", key="ip", rate="5/m", increment=True)
            or is_ratelimited(request, group="create_schedule", key="ip", rate="10/h", increment=True)
        )

        if ratelimited:
            messages.error(request, "Woah, slow down!")
            return render(request, "base/toasts.html")

        check_usage = quota_usage_check_under(request, "invoices-schedules")
        if not isinstance(check_usage, bool):
            return check_usage

        return create_ots(request)

    messages.error(request, "Invalid option. Something went wrong.")
    return render(request, "base/toasts.html")


def create_ots(request: HtmxHttpRequest) -> HttpResponse:
    invoice_id = request.POST.get("invoice_id") or request.POST.get("invoice")

    try:
        invoice = Invoice.objects.get(id=invoice_id)
    except Invoice.DoesNotExist:
        messages.error(request, "Invoice not found")
        return render(request, "base/toasts.html")

    if (request.user.logged_in_as_team and invoice.organization != request.user.logged_in_as_team) or (
        not request.user.logged_in_as_team and invoice.user != request.user
    ):
        messages.error(request, "You do not have permission to create schedules for this invoice")
        return render(request, "base/toasts.html")

    print("[BACKEND] About to create ots", flush=True)

    schedule = create_onetime_schedule(
        CreateOnetimeScheduleInputData(
            invoice=invoice, option=1, datetime=request.POST.get("date_time"), email_type=request.POST.get("email_type")
        )
    )

    print(schedule, flush=True)

    if isinstance(schedule, CreateOnetimeScheduleSuccessResponse):
        QuotaUsage.create_str(request.user, "invoices-schedules", schedule.schedule.id)
        messages.success(request, "Schedule created!")
        return render(request, "pages/invoices/schedules/schedules/_table_row.html", {"schedule": schedule.schedule})

    messages.error(request, schedule.message)
    return render(request, "base/toasts.html")


def get_execution_role() -> str | None:
    """
    :return: Role ARN if a role exists else None
    """

    iam_client = get_iam_client()
    response = iam_client.list_roles(PathPrefix=f"/{AWS_TAGS_APP_NAME}-scheduled-invoices/", MaxItems=1)

    try:
        response: GetRoleResponseTypeDef = iam_client.get_role(RoleName=f"{AWS_TAGS_APP_NAME}-invoicing-scheduler")
    except (iam_client.exceptions.NoSuchEntityException, iam_client.exceptions.ServiceFailureException):
        return None

    if response.get("Role", {}).get("Arn"):
        return response["Role"]["Arn"]

    return None


def authenticate_api_key(request: HtmxHttpRequest):
    token = request.META.get("HTTP_AUTHORIZATION", "").split()
    print(token)

    if not token or token[0].lower() != "token":
        return False, "Unauthorized", 401

    if len(token) == 1:
        return False, "Token not found", 400

    if len(token) > 2:
        return False, "Invalid token. Token should not contain spaces.", 400

    try:
        key_id = token[1].split(":")[0]
        key_str = token[1].split(":")[1]
        print(key_id)
        apikey = APIKey.objects.get(id=key_id)
        print(apikey)

        correct = apikey.verify(token[1])
        print(correct)
    except APIKey.DoesNotExist:
        return False, "Token not found", 400
    except ValueError:
        return False, "Invalid token", 400

    if not correct:
        return False, "Token not found", 400

    apikey.last_used = timezone.now()
    apikey.save()

    return True, "OK", 200


@require_http_methods(["DELETE", "POST"])
@feature_flag_check("isInvoiceSchedulingEnabled", True, api=True)
def cancel_onetime_schedule(request: HtmxHttpRequest, schedule_id: str):
    if not request.htmx:
        return HttpResponseForbidden()
    try:
        schedule = InvoiceOnetimeSchedule.objects.get(id=schedule_id, invoice__user=request.user)
    except InvoiceOnetimeSchedule.DoesNotExist:
        messages.error(request, "Schedule not found!")
        return render(request, "base/toasts.html")

    original_status = schedule.status
    schedule.status = InvoiceOnetimeSchedule.StatusTypes.DELETING
    schedule.save()

    delete_status: DeleteScheduleResponse = delete_schedule(schedule.invoice.id, schedule.id)

    if isinstance(delete_status, ErrorResponse):
        if delete_status.message == "Schedule not found":
            schedule.status = InvoiceOnetimeSchedule.StatusTypes.CANCELLED
            schedule.save()

            messages.success(request, "Schedule cancelled.")
            return render(request, "pages/invoices/schedules/schedules/_table_row.html", {"schedule": schedule})
        else:
            schedule.status = original_status
            schedule.save()
            messages.error(request, f"Failed to delete schedule: {delete_status.message}")
            return render(request, "base/toasts.html")

    schedule.status = InvoiceOnetimeSchedule.StatusTypes.CANCELLED
    schedule.save()

    messages.success(request, "Schedule cancelled.")
    return render(request, "pages/invoices/schedules/schedules/_table_row.html", {"schedule": schedule})


@require_GET
@feature_flag_check("isInvoiceSchedulingEnabled", True, api=True, htmx=True)
def fetch_onetime_schedules(request: HtmxHttpRequest, invoice_id: str):
    ratelimit = is_ratelimited(request, group="fetch_onetime_schedules", key="user", rate="5/30s", increment=True)
    if ratelimit:
        messages.error(request, "Woah slow down there!")
        return render(request, "base/toasts.html")

    try:
        invoice = Invoice.objects.prefetch_related("onetime_invoice_schedules").get(id=invoice_id)
    except Invoice.DoesNotExist:
        messages.error(request, "Invoice not found")
        return render(request, "base/toasts.html")

    if not invoice.user.logged_in_as_team and invoice.user != request.user:
        messages.error(request, "You do not have permission to view this invoice")
        return render(request, "base/toasts.html")

    if invoice.user.logged_in_as_team and invoice.organization != request.user.logged_in_as_team:
        messages.error(request, "You do not have permission to view this invoice")
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

        if isinstance(aws_schedules, ListSchedulesErrorResponse):
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

    return render(request, "pages/invoices/schedules/schedules/_table_body.html", context)
