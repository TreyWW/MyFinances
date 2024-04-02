from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from backend.models.receipt import Receipt


@require_http_methods(["DELETE"])
@login_required
def receipt_delete(request: HttpRequest, id: int):
    receipt = Receipt.objects.filter(id=id).first()
    if not receipt:
        return JsonResponse(status=404, data={"message": "Receipt not found"})

    if request.user.logged_in_as_team and receipt.organization != request.user.logged_in_as_team:
        return JsonResponse(status=403, data={"message": "Forbidden"})
    elif receipt.user != request.user:
        return JsonResponse(status=403, data={"message": "Forbidden"})

    # QuotaLimit.delete_quota_usage("receipts-count", request.user, receipt.id, receipt.date_uploaded) # Don't want to delete receipts
    # from records because it does cost us PER receipt. So makes sense not to allow Upload, delete, upload .. etc

    receipt.delete()
    messages.success(request, "Receipt deleted")
    return render(
        request,
        "pages/receipts/_search_results.html",
        {"receipts": Receipt.objects.filter(user=request.user).order_by("-date")},
    )
