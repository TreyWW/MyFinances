from datetime import date

from backend.core.service.invoices.common.create.get_page import global_get_invoice_context
from backend.core.types.requests import WebRequest


def get_invoice_context(request: WebRequest) -> dict:
    global_context_service_response = global_get_invoice_context(request)

    context = global_context_service_response.response.context
    defaults = global_context_service_response.response.defaults

    if due_date := request.GET.get("due_date"):
        try:
            date.fromisoformat(due_date)
            context["due_date"] = due_date
        except ValueError:
            ...

    if not due_date:
        context["issue_date"], context["due_date"] = defaults.get_issue_and_due_dates(context["issue_date"])
    return context
