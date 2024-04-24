from django.contrib import messages
from django.http import JsonResponse, QueryDict, HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import resolve, reverse
from django.urls.exceptions import Resolver404
from django.views.decorators.http import require_http_methods

from backend.models import Invoice, QuotaLimit
from backend.types.htmx import HtmxHttpRequest


@require_http_methods(["DELETE"])
def delete_invoice(request: HtmxHttpRequest):
    delete_items = QueryDict(request.body)

    redirect = delete_items.get("redirect", None)

    try:
        invoice = Invoice.objects.get(id=delete_items.get("invoice", ""))
    except Invoice.DoesNotExist:
        return JsonResponse({"message": "Invoice not found"}, status=404)

    if not invoice.has_access(request.user):
        return JsonResponse({"message": "You do not have permission to delete this invoice"}, status=404)

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
