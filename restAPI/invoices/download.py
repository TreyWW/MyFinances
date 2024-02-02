from uuid import UUID
from xhtml2pdf import pisa
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from backend.models import InvoiceURL, UserSettings

# search_param = openapi.Parameter(
#     "search",
#     openapi.IN_QUERY,
#     description="A search string for a receipt name or date",
#     type=openapi.TYPE_STRING,
#     required=False,
# )

user_response_download = openapi.Response("Download an invoice")
# user_response_get_token = openapi.Response("Get a download token", ReceiptDownloadTokenReturnedSerializer)


@swagger_auto_schema(
    # manual_parameters=[search_param],
    method="GET",
    responses={200: user_response_download},
)
@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def download_invoice(request, invoice_uuid: InvoiceURL.uuid):
    try:
        if len(invoice_uuid) != 8:
            raise ValueError("Invoice UUID isnt a short uuid")

        url = (
            InvoiceURL.objects.select_related("invoice")
            .prefetch_related("invoice", "invoice__items")
            .get(uuid=invoice_uuid)
        )
        invoice = url.invoice

        if not invoice:
            raise InvoiceURL.DoesNotExist

    except ValueError:
        return Response(
            {"detail": "Invalid invoice uuid"}, status=status.HTTP_400_BAD_REQUEST
        )
    except InvoiceURL.DoesNotExist:
        return Response(
            {"detail": "Invoice not found"}, status=status.HTTP_404_NOT_FOUND
        )

    try:
        if request.user.is_authenticated:
            currency_symbol = request.user.user_profile.get_currency_symbol
        else:
            currency_symbol = "$"
    except UserSettings.DoesNotExist:
        currency_symbol = "$"

    invoice_html = render_to_string(
        "pages/invoices/view/invoice.html",
        {"invoice": invoice, "currency_symbol": currency_symbol},
    )

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = (
        f'attachment; filename="Invoice #{invoice.id}.pdf"'
    )
    # print(invoice_html)

    pisa.CreatePDF(invoice_html, dest=response)

    return response


# @swagger_auto_schema(
#     method="GET",
#     responses={200: user_response_get_token},
# )
# @api_view(["GET"])
# @authentication_classes([TokenAuthentication])
# @permission_classes([IsAuthenticated])
# def get_download_token(request, receipt_id: Receipt.id):
#     try:
#         receipt = Receipt.objects.get(id=receipt_id, user=request.user)
#     except Receipt.DoesNotExist:
#         return Response({"success": False, "message": "Receipt not found"}, status=status.HTTP_404_NOT_FOUND)
#
#     if receipt.user != request.user:
#         return Response({"success": False, "message": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)
#
#     token = ReceiptDownloadToken.objects.create(user=request.user, file=receipt, delete_at=timezone.now() +
#                                                                                            timezone.timedelta(days=1))
#     download_link = request.build_absolute_uri(
#         reverse("restAPI:receipts:download", args=[token.token])
#     )
#
#     response_data = {
#         "success": True,
#         "url": download_link,
#         "token": token.token
#     }
#
#     serializer = ReceiptDownloadTokenReturnedSerializer(response_data)
#
#     # Instead of FileResponse, use Response with appropriate data
#     return Response(serializer.data, content_type="application/json")
