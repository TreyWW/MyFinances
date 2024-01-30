import os
import requests
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, JsonResponse, HttpResponseBadRequest
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods

from backend.models import Receipt


@require_http_methods(["POST"])
@login_required
def receipt_create(request: HttpRequest):
    if not request.htmx:
        return redirect("receipts dashboard")
    file = request.FILES.get("receipt_image")  # InMemoryUploadedFile
    date = request.POST.get("receipt_date")
    name = request.POST.get("receipt_name")
    merchant_store = request.POST.get("merchant_store")
    purchase_category = request.POST.get("purchase_category")
    total_price = request.POST.get("total_price")

    if not file:
        messages.error(request, "No image found")
        return HttpResponseBadRequest("No image found", status=400)

    name = file.name.split(".")[0] if not name else name

    if not name:
        messages.error(
            request, "No name provided, or image doesn't contain a valid name."
        )
        return HttpResponseBadRequest(
            "No name provided, or image doesn't contain a valid name.", status=400
        )

    if not date:
        date = None

    receipt = Receipt.objects.create(
        user=request.user,
        name=name,
        image=file,
        date=date,
        merchant_store=merchant_store,
        purchase_category=purchase_category,
        total_price=total_price,
    )
    # r = requests.post(
    #     "https://ocr.asprise.com/api/receipt",
    #     data={
    #         "api_key": "TRUE" if os.environ.get("OCR_API_TEST") else "",
    #         "apikey": os.environ.get("OCR_API_KEY")
    #         if os.environ.get("OCR_API_TEST")
    #         else "",
    #         "recognizer": "auto",
    #     },
    #     files={"file": file.open()},
    # )
    #
    # receipt_json = r.json()
    # receipt.receipt_parsed = receipt_json

    # if receipt_json.get("total"):
    #     # Todo: add currency option
    #     receipt.total_price = receipt_json.get("total")
    receipt.save()

    messages.success(request, f"Receipt added with the name of {receipt.name}")
    return render(
        request,
        "pages/receipts/_search_results.html",
        {"receipts": Receipt.objects.filter(user=request.user).order_by("-date")},
    )
