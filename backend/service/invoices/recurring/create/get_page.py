from datetime import date

from backend.service.invoices.common.create.get_page import global_get_invoice_context
from backend.types.requests import WebRequest


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

    if sort_code := (request.GET.get("sort_code") or "").replace("-", ""):
        if len(sort_code) == 6:
            if len(sort_code) >= 2:
                sort_code = sort_code[0:2] + "-" + sort_code[2:]
            if len(sort_code) >= 5:
                sort_code = sort_code[0:5] + "-" + sort_code[5:]
            context["sort_code"] = sort_code

    return context
