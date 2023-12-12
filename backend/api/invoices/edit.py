from django.contrib import messages
from django.http import HttpRequest, JsonResponse, QueryDict
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from backend.models import Invoice


@require_http_methods(["EDIT"])
def edit_invoice(request: HttpRequest):
    edit_items = QueryDict(request.body)
    print("edit items", edit_items)

    invoice = edit_items.get("invoice")

    try:
        invoice = Invoice.objects.get(id=invoice)
    except:
        return JsonResponse({"message": "Invoice not found"}, status=404)

    if not invoice or invoice.user != request.user:
        return JsonResponse({"message": "Invoice not found"}, status=404)

    invoice.edit()

    if request.htmx:
        messages.success(request, "Invoice edited")
        return render(request, "partials/base/toasts.html")

    return JsonResponse({"message": "Invoice successfully edited"}, status=200)
