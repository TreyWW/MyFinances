from django.contrib import messages
from django.shortcuts import render

from backend.decorators import web_require_scopes
from backend.core.service.reports.generate import generate_report
from backend.core.types.requests import WebRequest


@web_require_scopes("invoices:write", True, True)
def generate_report_endpoint(request: WebRequest):
    start_date: str = request.POST.get("start_date", "")
    end_date: str = request.POST.get("end_date", "")
    name: str = request.POST.get("name", "")

    generated_report = generate_report(request.actor, start_date, end_date, name)

    if generated_report.failed:
        messages.error(request, generated_report.error)
        return render(request, "base/toast.html")

    messages.success(request, f"Successfully generated report ({str(generated_report.response.uuid)[:4]})")

    resp = render(request, "base/toast.html")
    resp["HX-Trigger"] = "refresh_reports_table"
    return resp
