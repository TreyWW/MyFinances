from django.contrib import messages
from django.http import HttpRequest, JsonResponse, QueryDict, HttpResponse
from django.shortcuts import render
from django.urls import resolve
from django.urls.exceptions import Resolver404
from django.views.decorators.http import require_http_methods

from backend.models import QuotaLimit
from backend.models_db.invoice import Invoice


@require_http_methods(["DELETE"])
def delete_invoice(request: HttpRequest):
    delete_items = QueryDict(request.body)

    invoice = delete_items.get("invoice")
    redirect = delete_items.get("redirect", None)

    try:
        invoice = Invoice.objects.get(id=invoice)
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
            response = HttpResponse(request, status=200)
            response["HX-Location"] = redirect
            return response
        except Resolver404:
            return HttpResponseRedirect(reverse("dashboard"))

    return JsonResponse({"message": "Invoice successfully deleted"}, status=200)
