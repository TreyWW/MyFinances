from datetime import datetime
from typing import NoReturn
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, JsonResponse, HttpResponse, HttpResponseBadRequest
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods, require_POST
from backend.models import Receipt


@require_http_methods(["POST"])
@login_required
def edit_receipt(request, receipt_id):
    # Fetch the receipt object from the database
    receipt = Receipt.objects.get(pk=receipt_id)
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
        messages.error(request, "No name provided, or image doesn't contain a valid name.")
        return HttpResponseBadRequest("No name provided, or image doesn't contain a valid name.", status=400)

    if not date:
        date = None

    # Compare the values with the existing receipt object
    if (
        name != receipt.name
        or file != receipt.image
        or date != receipt.date
        or merchant_store != receipt.merchant_store
        or purchase_category != receipt.purchase_category
        or total_price != receipt.total_price
    ):

        # Update the receipt object
        receipt.name = name
        receipt.image = file
        receipt.date = date
        receipt.merchant_store = merchant_store
        receipt.purchase_category = purchase_category
        receipt.total_price = total_price

        receipt.save()

        messages.success(request, f"Receipt Name - {receipt.name} updated successfully.")
    else:
        messages.info(request, "No changes were made.")

    if request.user.logged_in_as_team:
        receipt.organization = request.user.logged_in_as_team
        receipts = Receipt.objects.filter(organization=request.user.logged_in_as_team).order_by("-date")
    else:
        receipt.user = request.user
        receipts = Receipt.objects.filter(user=request.user).order_by("-date")

    # Pass the receipt object to the template for rendering
    return render(
        request,
        "pages/receipts/_search_results.html",
        {"receipts": receipts},
    )
