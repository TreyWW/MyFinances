from django.contrib import messages
from django.http import JsonResponse, QueryDict, HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import resolve, reverse
from django.urls.exceptions import Resolver404
from django.views.decorators.http import require_http_methods

from backend.decorators import web_require_scopes
from backend.models import Invoice, QuotaLimit
from backend.core.types.htmx import HtmxHttpRequest


@require_http_methods(["DELETE"])
@web_require_scopes("invoices:write", True, True)
def delete_invoice(request: HtmxHttpRequest):
    delete_items = QueryDict(request.body)

    redirect = delete_items.get("redirect", None)

    try:
        invoice = Invoice.objects.get(id=delete_items.get("invoice", ""))
    except Invoice.DoesNotExist:
        messages.error(request, "Invoice Not Found")
        return render(request, "base/toasts.html")

    if not invoice.has_access(request.user):
        messages.error(request, "You do not have permission to delete this invoice")
        return render(request, "base/toasts.html")

    QuotaLimit.delete_quota_usage("invoices-count", request.user, invoice.id, invoice.date_created)

    invoice.delete()

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
            return HttpResponseRedirect(reverse("dashboard"))

    return JsonResponse({"message": "Invoice successfully deleted"}, status=200)
