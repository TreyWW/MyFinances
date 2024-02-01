from uuid import UUID

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
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

from backend.models import Receipt, ReceiptDownloadToken
from .serializers import ReceiptDownloadTokenReturnedSerializer

# search_param = openapi.Parameter(
#     "search",
#     openapi.IN_QUERY,
#     description="A search string for a receipt name or date",
#     type=openapi.TYPE_STRING,
#     required=False,
# )

user_response_download = openapi.Response("Download a receipt")
user_response_get_token = openapi.Response("Get a download token", ReceiptDownloadTokenReturnedSerializer)


@swagger_auto_schema(
    # manual_parameters=[search_param],
    method="GET",
    responses={200: user_response_download},
)
@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def download_receipt(request, token: ReceiptDownloadToken.token):
    try:
        UUID(token)
    except ValueError:
        # Token isn't a valid UUID
        return Response({"detail": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        download_token = ReceiptDownloadToken.objects.get(token=token)
    except ReceiptDownloadToken.DoesNotExist:
        return Response({"detail": "Download link is invalid"}, status=status.HTTP_404_NOT_FOUND)

    if download_token.delete_at and download_token.delete_in < timezone.now():
        download_token.delete()
        return Response({"detail": "Download has already been used"}, status=status.HTTP_410_GONE)

    if download_token.expires_at and download_token.expires_at < timezone.now():
        download_token.delete()
        return Response({"detail": "Download link has expired"}, status=status.HTTP_410_GONE)

    if download_token.user != request.user:
        return Response({"detail": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)

    receipt = get_object_or_404(Receipt, id=download_token.file.id)

    download_token.delete_at = timezone.now() + timezone.timedelta(days=6)

    image_data = receipt.image.read()

    response = HttpResponse(image_data, content_type="image/jpeg")
    response['Content-Disposition'] = f'attachment; filename="{receipt.image.name}"'

    return response


@swagger_auto_schema(
    method="GET",
    responses={200: user_response_get_token},
)
@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_download_token(request, receipt_id: Receipt.id):
    try:
        receipt = Receipt.objects.get(id=receipt_id, user=request.user)
    except Receipt.DoesNotExist:
        return Response({"success": False, "message": "Receipt not found"}, status=status.HTTP_404_NOT_FOUND)

    if receipt.user != request.user:
        return Response({"success": False, "message": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)

    token = ReceiptDownloadToken.objects.create(user=request.user, file=receipt, delete_at=timezone.now() +
                                                                                           timezone.timedelta(days=1))
    download_link = request.build_absolute_uri(
        reverse("restAPI:receipts:download", args=[token.token])
    )

    response_data = {
        "success": True,
        "url": download_link,
        "token": token.token
    }

    serializer = ReceiptDownloadTokenReturnedSerializer(response_data)

    # Instead of FileResponse, use Response with appropriate data
    return Response(serializer.data, content_type="application/json")