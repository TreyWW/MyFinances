from dataclasses import dataclass
from typing import Literal

from django.http import HttpRequest, HttpResponse
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from backend.decorators import feature_flag_check
from backend.models import Invoice, AuditLog, APIKey, InvoiceOnetimeSchedule, InvoiceURL, InvoiceReminder
from settings.helpers import send_email, send_templated_email
from settings.settings import SITE_NAME


@require_POST
@csrf_exempt
@feature_flag_check("isInvoiceSchedulingEnabled", True, api=True)
def receive_scheduled_invoice(request: HttpRequest):
    print("Received Scheduled Invoice", flush=True)
    response = authenticate_api_key(request)

    if not response.success:
        print(f"[BACKEND] ERROR receiving scheduled invoice: {response.message}", flush=True)
        return HttpResponse(response.message, status=response.status_code)

    option = request.POST.get("option") or request.headers.get("option")

    if option == "invoice_schedule":
        return receive_scheduled_send(request)
    elif option == "invoice_reminder":
        return receive_reminder(request)
    else:
        return HttpResponse("Invalid option", status=400)


def receive_scheduled_send(request: HttpRequest) -> HttpResponse:
    invoice_id = request.POST.get("invoice_id") or request.headers.get("invoice_id")
    schedule_id = request.POST.get("schedule_id") or request.headers.get("schedule_id")
    schedule_type = request.POST.get("schedule_type") or request.headers.get("schedule_type")
    email_type = request.POST.get("email_type") or request.headers.get("email_type")

    if not invoice_id or not schedule_id or not schedule_type:
        return HttpResponse("Missing invoice_id or schedule_id or schedule_type", status=400)

    try:
        invoice = Invoice.objects.get(id=invoice_id)
    except Invoice.DoesNotExist:
        return HttpResponse("Invoice not found", status=404)

    try:
        schedule_type = int(schedule_type)
    except ValueError:
        return HttpResponse("Invalid schedule_type. Must be an integer; 1=one-time, 2=recurring", status=400)

    if schedule_type == 1:
        schedule = InvoiceOnetimeSchedule.objects.get(id=schedule_id)
    else:
        return HttpResponse("Invalid schedule_type. Must be an integer; 1=one-time, 2=recurring", status=400)

    if email_type == "client_email":
        email = invoice.client_email
    elif invoice.client_to:
        email = invoice.client_to.email
    else:
        email = None

    if not email:
        return HttpResponse("No client email address stored", status=400)

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
        destination=email,
        subject=f"Invoice #{invoice_id} ready",
        message=f"""
                Hi {client_name},

                This is an automated email to let you know that your invoice #{invoice_id} is now ready. The due date is {invoice.date_due}.

                You can view the invoice here: {invoice_url}

                Best regards

                Note: This is an automated email sent out by MyFinances on behalf of '{invoice.self_company or invoice.self_name}'. If you
                believe this is spam or fraudulent please report it to us and DO NOT pay the invoice. Once a report has been made you will
                have a case opened.
            """,
    )

    if not email_response.success:
        schedule.set_status(schedule.StatusTypes.FAILED)
        schedule.set_received(False)
        return HttpResponse(f"Failed to send email: {email_response.message}", status=500)

    schedule.set_status(schedule.StatusTypes.COMPLETED)
    schedule.set_received()

    return HttpResponse("Sent", status=200)


def receive_reminder(request: HttpRequest):
    invoice_id = request.POST.get("invoice_id") or request.headers.get("invoice_id")
    reminder_id = request.POST.get("reminder_id") or request.headers.get("reminder_id")
    email_type = request.POST.get("email_type") or request.headers.get("email_type")

    if not invoice_id or not reminder_id:
        return HttpResponse("Missing invoice_id or reminder_id", status=400)

    try:
        invoice = Invoice.objects.get(id=invoice_id)
    except Invoice.DoesNotExist:
        return HttpResponse("Invoice not found", status=404)

    try:
        reminder = InvoiceReminder.objects.get(id=reminder_id, invoice=invoice)
    except InvoiceReminder.DoesNotExist:
        return HttpResponse("Invalid reminder. Not found.", status=400)

    if email_type == "client_email":
        email = invoice.client_email
    elif invoice.client_to:
        email = invoice.client_to.email
    else:
        email = None

    if not email:
        return HttpResponse("No client email address stored", status=400)

    invoice_url_object = InvoiceURL.objects.create(
        invoice=invoice,
        system_created=True,
        never_expire=True,
    )

    invoice_url = request.build_absolute_uri(reverse("invoices view invoice", kwargs={"uuid": invoice_url_object.uuid}))

    AuditLog.objects.create(action=f"scheduled invoice: {invoice_id} send to {email_type} - {email}")

    data = {
        "client_name": invoice.client_name or invoice.client_to.name or "there",
        "invoice_id": invoice_id,
        "invoice_url": invoice_url,
        "days": reminder.days,
        "company": invoice.self_company or invoice.self_name
    }

    template_name = f"{SITE_NAME}-reminders"

    if reminder.reminder_type == "before_due":
        template_name += "before-due"
    elif reminder.reminder_type == "after_due":
        template_name += "after-due"
    else:
        template_name += "overdue"

    email_response = send_templated_email(destination=email, template_name=template_name, data=data)

    if not email_response.success:
        reminder.set_status(reminder.StatusTypes.FAILED)
        reminder.set_received(False)
        return HttpResponse(f"Failed to send email: {email_response.message}", status=500)

    reminder.set_status(reminder.StatusTypes.COMPLETED)
    reminder.set_received()

    return HttpResponse("Sent", status=200)


@dataclass(frozen=True)
class AuthenticateSuccess:
    success: Literal[True] = True


@dataclass(frozen=True)
class AuthenticateFailure:
    message: str
    status_code: int
    success: Literal[False] = False


def authenticate_api_key(request: HttpRequest) -> AuthenticateSuccess | AuthenticateFailure:
    token = request.META.get("HTTP_AUTHORIZATION", "").split()
    print(token)

    if not token or token[0].lower() != "token":
        return AuthenticateFailure("Unauthorized", 401)

    if len(token) == 1:
        return AuthenticateFailure("Token not found", 400)

    if len(token) > 2:
        return AuthenticateFailure("Invalid token. Token should not contain spaces.", 400)

    try:
        key_id = token[1].split(":")[0]
        key_str = token[1].split(":")[1]
        print(key_id)
        apikey = APIKey.objects.get(id=key_id, service=APIKey.ServiceTypes.AWS_API_DESTINATION)
        print(apikey)

        correct = apikey.verify(token[1])
        print(correct)
    except APIKey.DoesNotExist:
        return AuthenticateFailure("Token not found", 400)
    except ValueError:
        return AuthenticateFailure("Invalid token", 400)

    if not correct:
        return AuthenticateFailure("Token not found", 400)

    apikey.last_used = timezone.now()
    apikey.save()

    return AuthenticateSuccess()
