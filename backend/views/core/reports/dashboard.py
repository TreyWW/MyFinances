from datetime import date

from django.contrib import messages

from backend.models import MonthlyReport
from backend.service.reports.generate import generate_report
from backend.types.requests import WebRequest
from django.shortcuts import render, redirect


def view_reports_endpoint(request: WebRequest):
    return render(request, "pages/reports/dashboard.html")
