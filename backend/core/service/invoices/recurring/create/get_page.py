from datetime import date

from backend.core.service.invoices.common.create.get_page import global_get_invoice_context
from backend.core.types.requests import WebRequest


def get_invoice_context(request: WebRequest) -> dict:
    global_context_service_response = global_get_invoice_context(request)

    context = global_context_service_response.response.context
    defaults = global_context_service_response.response.defaults

    if due_date := request.GET.get("end_date"):
        try:
            date.fromisoformat(due_date)
            context["end_date"] = due_date
        except ValueError:
            ...

    if frequency := request.GET.get("frequency", ""):
        if frequency.lower() in ["weekly", "monthly", "yearly"]:
            context["frequency"] = frequency.lower()

            if day_of_week := request.GET.get("day_of_week"):
                context["day_of_week"] = day_of_week

            if day_of_month := request.GET.get("day_of_month"):
                context["day_of_month"] = day_of_month

            if month_of_year := request.GET.get("month_of_year"):
                context["month_of_year"] = month_of_year

    return context
