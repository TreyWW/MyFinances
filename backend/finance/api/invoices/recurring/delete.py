from django.contrib import messages
from django.http import JsonResponse, QueryDict, HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import resolve, reverse
from django.urls.exceptions import Resolver404
from django.views.decorators.http import require_http_methods

from backend.decorators import web_require_scopes
from backend.finance.models import InvoiceRecurringProfile
from backend.core.service.asyn_tasks.tasks import Task
from backend.core.service.boto3.scheduler.delete_schedule import delete_boto_schedule
from backend.core.types.requests import WebRequest


@require_http_methods(["DELETE"])
@web_require_scopes("invoices:write", True, True)
def delete_invoice_recurring_profile_endpoint(request: WebRequest):
    delete_items = QueryDict(request.body)

    redirect = delete_items.get("redirect", None)

    try:
        invoice_profile = InvoiceRecurringProfile.objects.get(id=delete_items.get("invoice_profile", ""))
    except InvoiceRecurringProfile.DoesNotExist:
        messages.error(request, "Invoice recurring profile Not Found")
        return render(request, "base/toasts.html")

    if not invoice_profile.has_access(request.user):
        messages.error(request, "You do not have permission to delete this Invoice recurring profile")
        return render(request, "base/toasts.html")

    # QuotaLimit.delete_quota_usage("invoices-count", request.user, invoice.id, invoice.date_created)

    Task().queue_task(delete_boto_schedule, "InvoiceRecurringProfile", invoice_profile.id)

    invoice_profile.active = False
    invoice_profile.save()

    if request.htmx:
        if not redirect:
            messages.success(request, "Invoice profile deleted")
            return render(request, "base/toasts.html")

        try:
            resolve(redirect)
            response = HttpResponse(status=200)
            response["HX-Location"] = redirect
            return response
        except Resolver404:
            return HttpResponseRedirect(reverse("finance:invoices:recurring:dashboard"))

    return JsonResponse({"message": "Invoice successfully deleted"}, status=200)
