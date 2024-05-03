from django.http import JsonResponse
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from backend.decorators import feature_flag_check, quota_usage_check
from backend.models import Invoice, AuditLog, APIKey, InvoiceURL, InvoiceReminder, InvoiceOnetimeSchedule
from backend.types.emails import SingleEmailInput, SingleTemplatedEmailContent
from backend.types.htmx import HtmxHttpRequest
from settings.helpers import send_email


import logging

from settings.settings import AWS_TAGS_APP_NAME

logger = logging.getLogger(__name__)


@require_POST
@csrf_exempt
@feature_flag_check("isInvoiceSchedulingEnabled", True, api=True)
def receive_scheduled_invoice_schedule(request: HtmxHttpRequest):
    """

    requires:
    - invoice_id
    - schedule_id
    - email_type ("client_email" or none)
    - schedule_occurrence "once" or "recurring"

    :return {"success": False, "message": "...", "status": ...} if an error occurred.
    :return {"success": True} otherwise
    """

    logger.debug("Received Scheduled Invoice. Now authenticating...")
    valid, reason, status = authenticate_api_key(request)

    if not valid:
        return JsonResponse({"message": reason, "success": False}, status=status)

    invoice_id = request.POST.get("invoice_id") or request.headers.get("invoice_id")
    schedule_id = request.POST.get("schedule_id") or request.headers.get("schedule_id")
    schedule_type = request.POST.get("schedule_occurrence") or request.headers.get("schedule_occurrence")
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
        if schedule_type is None or int(schedule_type) not in [1, 2]:
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

    client_name: str = "there"
    if invoice is not None and invoice.client_name:
        client_name = invoice.client_name
    elif invoice is not None and invoice.client_to:
        client_name = invoice.client_to.name

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


@require_POST
@csrf_exempt
@feature_flag_check("isInvoiceSchedulingEnabled", True, api=True)
@feature_flag_check("areInvoiceRemindersEnabled", True, api=True)
def receive_scheduled_invoice_reminder(request: HtmxHttpRequest):
    """
    requires:
    - invoice_id
    - schedule_id
    - email_type ("client_email" or none)
    - schedule_occurrence "once" or "recurring"

    :return {"success": False, "message": "...", "status": ...} if an error occurred.
    :return {"success": True} otherwise
    """

    logger.debug("Received Scheduled Invoice for a Reminder. Now authenticating...")
    valid, reason, status = authenticate_api_key(request)

    if not valid:
        return JsonResponse({"message": reason, "success": False}, status=status)

    invoice_id = request.POST.get("invoice_id") or request.headers.get("invoice_id")
    schedule_id = request.POST.get("schedule_id") or request.headers.get("schedule_id")
    schedule_type = request.POST.get("schedule_occurrence") or request.headers.get("schedule_occurrence")
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

    if schedule_type not in ["once", "recurring"]:
        return JsonResponse({"success": False, "message": "Invalid schedule_type. Must be either 'once' or 'recurring'"}, status=400)

    if schedule_type == "once":
        schedule: InvoiceOnetimeSchedule = invoice.onetime_invoice_schedules.get(id=schedule_id)
    else:
        return JsonResponse({"success": False, "message": "Recurring reminders is not yet implemented"}, status=400)

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

    client_name: str = "there"
    if invoice is not None and invoice.client_name:
        client_name = invoice.client_name
    elif invoice is not None and invoice.client_to:
        client_name = invoice.client_to.name
    # Todo: add better email message

    # if schedule.status

    invoice_status: str = invoice.dynamic_payment_status()

    email_data = {
        "invoice_id": invoice_id,
        "invoice_url": invoice_url,
        "client_name": client_name,
        "company": invoice.self_company or invoice.self_name or invoice.user.get_full_name() if invoice.user else False,
    }

    email_template = AWS_TAGS_APP_NAME + "-reminders-"
    days_until_due: int | bool = get_days_until_invoice_due(invoice)

    if not days_until_due:
        return JsonResponse({"success": False, "message": "Date not found, try again later", "status": 400})

    if invoice_status == "paid":
        return JsonResponse({"success": True})

    if invoice_status == "overdue":
        email_data["days"] = 0
        if days_until_due == 0:  # Today
            email_template += "overdue"
        else:
            email_template += "after_due"
    else:
        email_data["days"] = abs(days_until_due)  # abs makes it always positive

        email_template += "before_due"

    email_response = send_email(
        SingleEmailInput(
            destination=email,
            subject="",  # should be autofilled by template
            content=SingleTemplatedEmailContent(template_name=email_template, template_data=email_data),
        )
    )

    if not email_response.success:
        schedule.set_status("failed", save=False).set_received(False)
        return JsonResponse({"success": False, "message": f"Failed to send email: {email_response.message}"}, status=500)

    schedule.set_status(schedule.StatusTypes.COMPLETED).schedule.set_received()

    return JsonResponse({"success": True})


def get_days_until_invoice_due(invoice: Invoice) -> int:
    if timezone.now() is not None:
        return (invoice.date_due - timezone.now()).days  # type: ignore[attr-defined]
    else:
        return False


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
