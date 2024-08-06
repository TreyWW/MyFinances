from django.contrib import messages
from django.http import JsonResponse, QueryDict, HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import resolve, reverse
from django.urls.exceptions import Resolver404
from django.views.decorators.http import require_http_methods

from backend.decorators import web_require_scopes
from backend.models import QuotaLimit, InvoiceRecurringSet
from backend.types.requests import WebRequest


@require_http_methods(["DELETE"])
@web_require_scopes("invoices:write", True, True)
def delete_invoice_recurring_set_endpoint(request: WebRequest):
    delete_items = QueryDict(request.body)

    redirect = delete_items.get("redirect", None)

    try:
        invoice_set = InvoiceRecurringSet.objects.get(id=delete_items.get("invoice", ""))
    except InvoiceRecurringSet.DoesNotExist:
        messages.error(request, "Invoice Set Not Found")
        return render(request, "base/toasts.html")

    if not invoice_set.has_access(request.user):
        messages.error(request, "You do not have permission to delete this invoice set")
        return render(request, "base/toasts.html")

    # QuotaLimit.delete_quota_usage("invoices-count", request.user, invoice.id, invoice.date_created)

    invoice_set.delete()

    if request.htmx:
        if not redirect:
            messages.success(request, "Invoice deleted")
            return render(request, "base/toasts.html")

        try:
            resolve(redirect)
            response = HttpResponse(status=200)
            response["HX-Location"] = redirect
            return response
        except Resolver404:
            return HttpResponseRedirect(reverse("invoices:recurring:dashboard"))

    return JsonResponse({"message": "Invoice successfully deleted"}, status=200)
