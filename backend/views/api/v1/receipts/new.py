import os
import requests
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from backend.models import Receipt


@require_http_methods(["POST"])
@login_required
def receipt_create(request: HttpRequest):
    file = request.FILES.get("receipt_image")  # InMemoryUploadedFile
    date = request.POST.get("receipt_date")
    name = request.POST.get("receipt_name")

    if not file:
        messages.error(request, "No image found")
        return JsonResponse(status=400)

    name = file.name.split(".")[0] if not name else name

    if not name:
        messages.error(
            request, "No name provided, or image doesn't contain a valid name."
        )
        return JsonResponse(status=400)

    receipt = Receipt.objects.create(
        user=request.user, name=name, image=file, date=date
    )
    r = requests.post(
        "https://ocr.asprise.com/api/v1/receipt",
        data={
            "api_key": "TRUE" if os.environ.get("OCR_API_TEST") else "",
            "apikey": os.environ.get("OCR_API_KEY")
            if os.environ.get("OCR_API_TEST")
            else "",
            "recognizer": "auto",
        },
        files={"file": file.open()},
    )

    receipt_json = r.json()
    receipt.receipt_parsed = receipt_json

    if receipt_json.get("total"):
        # Todo: add currency option
        receipt.total_price = receipt_json.get("total")
    receipt.save()

    messages.success(request, f"Receipt added with the name of {receipt.name}")
    return render(
        request,
        "core/pages/receipts/_search_results.html",
        {"receipts": Receipt.objects.filter(user=request.user).order_by("-date")},
    )
