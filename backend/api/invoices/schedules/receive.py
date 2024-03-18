from django.http import HttpRequest, HttpResponse
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from backend.decorators import feature_flag_check
from backend.models import Invoice, AuditLog, APIKey, InvoiceOnetimeSchedule, InvoiceURL
from settings.helpers import send_email


@require_POST
@csrf_exempt
@feature_flag_check("isInvoiceSchedulingEnabled", True, api=True)
def receive_scheduled_invoice(request: HttpRequest):
    print("Received Scheduled Invoice", flush=True)
    valid, reason, status = authenticate_api_key(request)

    if not valid:
        print(f"[BACKEND] ERROR receiving scheduled invoice: {reason}", flush=True)
        return HttpResponse(reason, status=status)

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
        schedule.status = schedule.StatusTypes.FAILED
        schedule.received = False
        schedule.save()
        return HttpResponse(f"Failed to send email: {email_response.message}", status=500)

    schedule.status = schedule.StatusTypes.COMPLETED
    schedule.received = True
    schedule.save()

    return HttpResponse("Sent", status=200)


def authenticate_api_key(request: HttpRequest):
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
