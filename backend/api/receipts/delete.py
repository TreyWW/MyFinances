from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from backend.models import Receipt
from django.db.models import Q


@require_http_methods(["DELETE"])
@login_required
def receipt_delete(request: HttpRequest, id: int):
    receipt = Receipt.objects.filter(id=id).first()
    if not receipt or receipt.user != request.user:
        return JsonResponse(status=404)

    receipt.delete()
    messages.success(request, "Receipt deleted")
    return render(
        request,
        "pages/receipts/_search_results.html",
        {"receipts": Receipt.objects.filter(user=request.user).order_by("-date")},
    )
