from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from backend.decorators import web_require_scopes
from backend.models import Receipt
from backend.core.types.requests import WebRequest


@require_http_methods(["DELETE"])
@login_required
@web_require_scopes("receipts:write", True, True)
def receipt_delete(request: WebRequest, id: int):
    try:
        receipt = Receipt.objects.get(id=id)
    except Receipt.DoesNotExist:
        return JsonResponse({"message": "Receipt not found"}, status=404)

    if not receipt:
        return JsonResponse(status=404, data={"message": "Receipt not found"})

    if not receipt.has_access(request.actor):
        return JsonResponse({"message": "You do not have permission to delete this invoice"}, status=404)

    receipt.delete()
    messages.success(request, f"Receipt deleted with the name of {receipt.name}")
    Receipt.objects.filter()
    return render(
        request, "pages/receipts/_search_results.html", {"receipts": Receipt.filter_by_owner(owner=request.actor).order_by("-date")}
    )
