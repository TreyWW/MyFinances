from django.http import FileResponse, Http404
from backend.models import Receipt, ReceiptDownloadToken
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.http import HttpResponse, JsonResponse


def download_receipt(request, token):
    """
    Downloads a receipt file based on the provided token.

    Args:
        request (HttpRequest): The HTTP request object.
        token (str): The token used to authenticate the download.

    Returns:
        HttpResponse: The HTTP response containing the downloaded receipt file.
    """
    download_token = get_object_or_404(ReceiptDownloadToken, token=token)

    if download_token.is_used() or download_token.user != request.user:
        raise Http404("Download link is invalid or has been used")

    receipt = get_object_or_404(Receipt, id=download_token.file.id)

    download_token.mark_as_used()

    response = FileResponse(receipt.image)

    response = HttpResponse(response.streaming_content, content_type="image/jpeg")
    return response


def generate_download_link(request, receipt_id):
    """
    Generates a download link for a receipt file.

    Args:
        request (HttpRequest): The HTTP request object.
        receipt_id (int): The ID of the receipt.

    Returns:
        JsonResponse: A JSON response containing the unique,onetime download link and filename.
    """
    receipt = get_object_or_404(Receipt, id=receipt_id, user=request.user)
    token = ReceiptDownloadToken.objects.create(user=request.user, file=receipt)
    download_link = request.build_absolute_uri(
        reverse("api:receipts:download_receipt", args=[token.token])
    )

    response_data = {
        "download_link": download_link,
        "filename": receipt.image.name,
    }

    return JsonResponse(response_data)
