from django.db.models import Q
from django.http import HttpRequest, HttpResponseNotFound
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods

from backend.models import Invoice


@require_http_methods(["GET"])
def fetch_all_invoices(request: HttpRequest):
    if not request.htmx:
        return redirect("invoices dashboard")
    context = {}
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
        if filter_type == "payment_status":
            all_payment_statuses = [
                "overdue",
                "pending",
                "paid",
            ]
            selected_statuses = {
                "paid": True
                if request.GET.get("payment_status_paid") or filter_by == "paid"
                else False,
                "pending": True
                if request.GET.get("payment_status_pending") or filter_by == "pending"
                else False,
                "overdue": True
                if request.GET.get("payment_status_overdue") or filter_by == "overdue"
                else False,
            }
            context["all_filters"] = all_payment_statuses
            context["filtering"] = "payment_status"
            for item, status in selected_statuses.items():
                if status:
                    invoices = invoices.filter(payment_status=item)
                    print(context.get("selected_filters"))
                    context["selected_filters"] = (
                        [item]
                        if not context.get("selected_filters", False)
                        else context["selected_filters"].append(item)
                    )
                    print(context.get("selected_filters"))

    if sort_by:
        invoices = invoices.order_by(sort_by)
        context["sort"] = sort_by

    context["invoices"] = invoices

    return render(request, "pages/invoices/dashboard/_fetch_body.html", context)
