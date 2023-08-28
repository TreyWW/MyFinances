import os
from pathlib import Path

import requests
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from backend.models import Receipt
from django.db.models import Q


@require_http_methods(['POST'])
@login_required
def receipt_create(request: HttpRequest):
    print("received")
    file = request.FILES.get('receipt_image')
    date = request.POST.get('receipt_date')
    name = request.POST.get('receipt_name')

    if not file:
        messages.error(request, "No image found")
        return JsonResponse(status=400)

    name = file.name.split('.')[0] if not name else name

    if not name:
        messages.error(request, "No name provided, or image doesn't contain a valid name.")
        return JsonResponse(status=400)

    receipt = Receipt.objects.create(
        user=request.user,
        name=name,
        image=file,
        date=date
    )
    r = requests.post('https://ocr.asprise.com/api/v1/receipt', data={
        'api_key': 'TEST',
        'recognizer': 'auto'},
      files=
      {"file":
           open(os.path.join(Path(__file__).resolve().parent.parent.parent.parent.parent.parent, f"media/receipts/{file}"), "rb")
       }
      )

    receipt_json = r.json()

    if receipt_json.get("total"):
        # Todo: add currency option
        receipt.total_price = receipt_json.get("total")
        receipt.save()

    messages.success(request, f"Receipt added with the name of {receipt.name}")
    return render(request, 'core/pages/receipts/_search_results.html', {'receipts': Receipt.objects.filter(user=request.user)})
