# from django.contrib import messages
# from django.core.handlers.wsgi import WSGIRequest
# from django.http import HttpResponseForbidden
# from django.shortcuts import render
# from django.views.decorators.http import require_http_methods
#
# from backend.decorators import feature_flag_check, web_require_scopes
# from backend.finance.models import InvoiceReminder
#
# from backend.types.htmx import HtmxHttpRequest
#
#
# @require_http_methods(["DELETE", "POST"])
# @feature_flag_check("areInvoiceRemindersEnabled", True, api=True)
# @web_require_scopes("invoices:write", True, True)
# def cancel_reminder_view(request: HtmxHttpRequest, reminder_id: str):
#     if not request.htmx:
#         return HttpResponseForbidden()
#     try:
#         reminder = InvoiceReminder.objects.get(id=reminder_id)
#     except InvoiceReminder.DoesNotExist:
#         messages.error(request, "Schedule not found!")
#         return render(request, "base/toasts.html")
#
#     if not reminder.invoice.has_access(request.user):
#         messages.error(request, "You do not have access to this invoice.")
#         return render(request, "base/toasts.html")
#
#     original_status = reminder.status
#     reminder.set_status("deleting")
#
#     delete_status = delete_reminder(reminder.invoice.id, reminder.id)
#
#     if not delete_status.success:
#         if delete_status.message == "Schedule not found":
#             reminder.set_status("cancelled")
#
#             messages.success(request, "Schedule cancelled.")
#             return render(request, "pages/invoices/single/schedules/reminders/_table_row.html", {"reminder": reminder})
#         else:
#             reminder.set_status(original_status)
#             messages.error(request, f"Failed to delete schedule: {delete_status.message}")
#             return render(request, "base/toasts.html")
#
#     reminder.set_status("cancelled")
#
#     messages.success(request, "Schedule cancelled.")
#     return render(request, "pages/invoices/single/schedules/reminders/_table_row.html", {"reminder": reminder})
