from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, JsonResponse, HttpResponse, HttpResponseRedirect, QueryDict
from django.shortcuts import render, redirect
from django.urls import resolve, Resolver404, reverse
from django.views.decorators.http import require_http_methods

from backend.models import Receipt
from backend.types.htmx import HtmxHttpRequest


@require_http_methods(["DELETE"])
@login_required
def receipt_delete(request: HtmxHttpRequest, id: int):
    try:
        receipt = Receipt.objects.get(id=id)
    except Receipt.DoesNotExist:
        return JsonResponse({"message": "Receipt not found"}, status=404)

    if not receipt:
        return JsonResponse(status=404, data={"message": "Receipt not found"})

    if not receipt.has_access(request.user):
        return JsonResponse({"message": "You do not have permission to delete this invoice"}, status=404)

    receipt.delete()
    messages.success(request, f"Receipt deleted with the name of {receipt.name}")
    if request.user.logged_in_as_team:
        return render(
            request,
            "pages/receipts/_search_results.html",
            {"receipts": Receipt.objects.filter(organization=request.user.logged_in_as_team).order_by("-date")},
        )
    else:
        return render(
            request,
            "pages/receipts/_search_results.html",
            {"receipts": Receipt.objects.filter(user=request.user).order_by("-date")},
        )
