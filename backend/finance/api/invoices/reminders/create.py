# from datetime import timedelta
#
# from django.contrib import messages
# from django.core.handlers.wsgi import WSGIRequest
# from django.http import HttpResponse
# from django.shortcuts import render, redirect
# from django.utils import timezone
#
# from backend.decorators import web_require_scopes
# from backend.finance.models import Invoice, InvoiceReminder, QuotaUsage
# from backend.utils.quota_limit_ops import quota_usage_check_under
# from infrastructure.aws.schedules.create_reminder import CreateReminderInputData, create_reminder_schedule
#
# from backend.types.htmx import HtmxHttpRequest
#
#
# def get_datetime_from_reminder(reminder: InvoiceReminder) -> str:
#     if reminder.reminder_type == "on_overdue":
#         return reminder.invoice.date_due.strftime("%Y-%m-%dT%H:%M")
#
#     if reminder.reminder_type == "before_due" and reminder.days:
#         days = 0 - reminder.days
#     else:
#         days = 0
#
#     date = (timezone.now() + timedelta(days=days)).replace(hour=12, minute=0, second=0, microsecond=0).strftime("%Y-%m-%dT%H:%M")
#     return date
#
#
# @web_require_scopes("invoices:write", True, True)
# def create_reminder_view(request: HtmxHttpRequest) -> HttpResponse:
#     if not request.htmx:
#         return redirect("finance:invoices:single:dashboard")
#
#     check_usage = quota_usage_check_under(request, "invoices-schedules", api=True, htmx=True)
#
#     if not isinstance(check_usage, bool):
#         return check_usage
#
#     # Extract POST data
#     invoice_id = request.POST.get("invoice_id", "") or request.POST.get("invoice", "")
#     reminder_type = request.POST.get("reminder_type")
#     days: str | int = request.POST.get("days", "none")
#
#     # Check if invoice exists
#     try:
#         invoice = Invoice.objects.get(id=invoice_id)
#     except Invoice.DoesNotExist:
#         messages.error(request, "Invoice not found")
#         return render(request, "base/toast.html", {"autohide": False})
#
#     # Check user permission
#     if not invoice.has_access(user=request.user):
#         messages.error(request, "You do not have permission to create schedules for this invoice")
#         return render(request, "base/toasts.html")
#
#     # Check reminder type
#     if reminder_type not in InvoiceReminder.ReminderTypes.values:
#         messages.error(request, "Invalid reminder type")
#         return render(request, "base/toasts.html")
#
#     # Ensure days is set for non-overdue reminders
#     if reminder_type == "on_overdue":
#         days = 0
#
#     # Convert days to integer
#     try:
#         days = int(days)
#         if days <= 0 and reminder_type != "on_overdue":
#             raise ValueError
#     except ValueError:
#         messages.error(request, "Invalid days value. Make sure it's an integer from 1-31")
#         return render(request, "base/toasts.html")
#
#     # Create reminder object
#     reminder = InvoiceReminder(invoice=invoice, reminder_type=reminder_type)
#     if reminder_type != "on_overdue":
#         reminder.days = days
#
#     # Prepare data for creating reminder schedule
#     data = CreateReminderInputData(
#         reminder=reminder,
#         invoice=invoice,
#         datetime=get_datetime_from_reminder(reminder),
#         email_type="client_to_email",  # TODO: Change to user inputted
#     )
#
#     # Create reminder schedule
#     REMINDER = create_reminder_schedule(data)
#
#     # Handle result of creating reminder schedule
#     if REMINDER.success:
#         reminder.save()
#         QuotaUsage.create_str(request.user, "invoices-schedules", REMINDER.reminder.id)
#         messages.success(request, "Schedule created!")
#         return render(request, "pages/invoices/single/schedules/reminders/_table_row.html", {"reminder": REMINDER.reminder})
#     else:
#         messages.error(request, REMINDER.message)
#         return render(request, "base/toasts.html")
