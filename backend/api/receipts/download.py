from django.http import FileResponse, HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404
from django.core.files.storage import default_storage
from backend.models import Receipt, OneTimeURL

def generate_download_url(request, receipt_id):
    # Retrieve the receipt from the database
    receipt = get_object_or_404(Receipt, pk=receipt_id)

    # Check if the receipt belongs to the current user
    if receipt.user != request.user:
        return HttpResponseForbidden()

    # Generate a unique token and create a new one-time URL
    token = receipt.get_signed_id()
    OneTimeURL.objects.create(receipt=receipt, token=token)

    # Return the download URL
    return JsonResponse({'url': receipt.get_receipt_url()})

def receipt_download(request, token):
    # Retrieve the one-time URL from the database
    one_time_url = get_object_or_404(OneTimeURL, token=token)

    # Check if the URL has been used
    if one_time_url.used:
        return HttpResponseForbidden()

    # Mark the URL as used
    one_time_url.used = True
    one_time_url.save()

    # Retrieve the receipt from the database
    receipt = one_time_url.receipt

    # Check if the receipt belongs to the current user
    if receipt.user != request.user:
        return HttpResponseForbidden()

    # Return the receipt image as a file response
    file = default_storage.open(receipt.image.path)
    return FileResponse(file)