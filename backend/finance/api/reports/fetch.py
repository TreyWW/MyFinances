from django.db.models import Q
from django.shortcuts import render

from backend.models import MonthlyReport
from backend.core.types.requests import WebRequest


def fetch_reports_endpoint(request: WebRequest):
    search = request.GET.get("search", "")

    reports = MonthlyReport.filter_by_owner(request.actor).all()

    if search:
        reports = reports.filter(
            Q(name__icontains=search)
            | Q(start_date__icontains=search)
            | Q(end_date__icontains=search)
            | Q(payments_in__icontains=search)
            | Q(payments_out__icontains=search)
        )

    return render(request, "pages/reports/_list_rows.html", {"reports": reports})
