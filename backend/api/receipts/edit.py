from datetime import datetime
from typing import NoReturn
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods, require_POST
from backend.models import Receipt


@require_http_methods(["POST"])
@login_required
def edit_receipt(request: HttpRequest, receipt_id):
    # Fetch the receipt object from the database
    receipt = Receipt.objects.get(pk=receipt_id)
    # TODO : edit_html page needs work to display the fetched data for editing
    # Pass the receipt object to the template for rendering
    return render(request, "pages/receipts/edit_receipt.html", {"receipt": receipt})
