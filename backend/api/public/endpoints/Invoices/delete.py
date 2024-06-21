from django.http import QueryDict
from django.urls import resolve, Resolver404
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from backend.models import Invoice, QuotaLimit


@api_view(["DELETE"])
def delete_invoice_endpoint(request):
    delete_items = QueryDict(request.body)

    redirect_url = delete_items.get("redirect", None)

    try:
        invoice = Invoice.objects.get(id=delete_items.get("invoice", ""))
    except Invoice.DoesNotExist:
        return Response({"error": "Invoice Not Found"}, status=status.HTTP_404_NOT_FOUND)

    if not invoice.has_access(request.user):
        return Response({"error": "You do not have permission to delete this invoice"}, status=status.HTTP_403_FORBIDDEN)

    QuotaLimit.delete_quota_usage("invoices-count", request.user, invoice.id, invoice.date_created)

    invoice.delete()

    if redirect_url:
        try:
            resolve(redirect_url)
            response = Response({"message": "Invoice deleted"}, status=status.HTTP_200_OK)
            response["HX-Location"] = redirect_url
            return response
        except Resolver404:
            return Response({"error": "Invalid redirect URL"}, status=status.HTTP_400_BAD_REQUEST)

    return Response({"message": "Invoice successfully deleted"}, status=status.HTTP_200_OK)
