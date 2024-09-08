from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import render, redirect

from backend.decorators import web_require_scopes
from backend.service.reports.generate import generate_report
from backend.types.requests import WebRequest


@web_require_scopes("invoices:write", True, True)
def generate_report_endpoint(request: WebRequest):
    start_date = request.POST.get("start_date")
    end_date = request.POST.get("end_date")
    name = request.POST.get("name")

    generated_report = generate_report(request.actor, start_date, end_date, name)

    if generated_report.failed:
        messages.error(request, generated_report.error)
        return render(request, "base/toast.html")

    messages.success(request, f"Successfully generated report ({str(generated_report.response.uuid)[:4]})")

    resp = render(request, "base/toast.html")
    resp["HX-Trigger"] = "refresh_reports_table"
    return resp
