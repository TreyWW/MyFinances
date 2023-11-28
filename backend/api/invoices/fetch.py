from django.db.models import Q
from django.http import HttpRequest, HttpResponseNotFound
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from backend.models import Invoice


@require_http_methods(["GET"])
def fetch_all_invoices(request: HttpRequest):
    sort_by = request.GET.get("sort")
    filter_type = request.GET.get("filter_type")
    filter_by = request.GET.get("filter")
    sort_by = (
        sort_by
        if sort_by
        in [
            "-date_due",
            "date_due",
            "id",
            "-id",
            "payment_status",
        ]
        else None
    )

    invoices = (
        Invoice.objects.filter(user=request.user)
        .prefetch_related("items")
        .only("invoice_id", "id", "payment_status", "date_due")
        .filter()
    )

    if filter_type and filter_by:
        if filter_type == "payment_status" and filter_by in [
            "pending",
            "paid",
            "overdue",
        ]:
            invoices = invoices.filter(payment_status=filter_by)

    if sort_by:
        invoices = invoices.order_by(sort_by)

    return render(
        request, "pages/invoices/dashboard/_table_body.html", {"invoices": invoices}
    )
