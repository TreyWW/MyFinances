from django.http import FileResponse, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse

from backend.decorators import web_require_scopes
from backend.models import Receipt, ReceiptDownloadToken


@web_require_scopes("receipts:read", True, True)
def download_receipt(request, token):
    """
    Downloads a receipt file based on the provided token.

    Args:
        request (HttpRequest): The HTTP request object.
        token (str): The token used to authenticate the download.

    Returns:
        HttpResponse: The HTTP response containing the downloaded receipt file.
    """
    try:
        download_token = ReceiptDownloadToken.objects.get(token=token)
    except ReceiptDownloadToken.DoesNotExist:
        return HttpResponse("Download link has been used", status=404)

    # if download_token.is_used():
    #     return HttpResponse("Download link has been used", status=410)  # 410 Gone
    if download_token.user != request.user:
        return HttpResponse("Forbidden", status=403)  # 403 Forbidden

    receipt = get_object_or_404(Receipt, id=download_token.file.id)

    download_token.delete()

    response = FileResponse(receipt.image)

    response = HttpResponse(response.streaming_content, content_type="image/jpeg")
    return response


@web_require_scopes("receipts:read", True, True)
def generate_download_link(request, receipt_id):
    """
    Generates a download link for a receipt file.

    Args:
        request (HttpRequest): The HTTP request object.
        receipt_id (int): The ID of the receipt.

    Returns:
        JsonResponse: A JSON response containing the unique,onetime download link and filename.
    """
    try:
        if request.user.logged_in_as_team:
            receipt = Receipt.objects.get(id=receipt_id, user=request.user)
        else:
            receipt = Receipt.objects.get(id=receipt_id, organization=request.user.logged_in_as_team)
    except Receipt.DoesNotExist:
        return HttpResponse("Receipt not found", status=404)
    token = ReceiptDownloadToken.objects.create(user=request.user, file=receipt)
    download_link = request.build_absolute_uri(reverse("api:finance:receipts:download_receipt", args=[token.token]))

    response_data = {
        "download_link": download_link,
        "filename": receipt.image.name,
    }

    return JsonResponse(response_data)
