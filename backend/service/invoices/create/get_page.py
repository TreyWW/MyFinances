from datetime import date
from typing import NamedTuple
from django.core.exceptions import PermissionDenied, ValidationError

from backend.models import Client, InvoiceProduct, DefaultValues
from backend.service.clients.validate import validate_client
from backend.service.defaults.get import get_account_defaults
from backend.types.requests import WebRequest
from backend.utils.dataclasses import BaseServiceResponse


class CreateInvoiceContextTuple(NamedTuple):
    defaults: DefaultValues
    context: dict


class CreateInvoiceContextServiceResponse(BaseServiceResponse[CreateInvoiceContextTuple]): ...


def global_get_invoice_context(request: WebRequest) -> CreateInvoiceContextServiceResponse:
    context: dict = {
        "clients": Client.objects.filter(user=request.user),
        "existing_products": InvoiceProduct.objects.filter(user=request.user),
    }

    defaults: DefaultValues

    if client_id := request.GET.get("client"):
        try:
            client: Client = validate_client(request, client_id)
            context["existing_client"] = client
            defaults = get_account_defaults(request.actor, client)

        except (Client.DoesNotExist, PermissionDenied, ValidationError):
            defaults = get_account_defaults(request.actor, client=None)
    else:
        defaults = get_account_defaults(request.actor, client=None)

    if issue_date := request.GET.get("issue_date"):
        try:
            date.fromisoformat(issue_date)
            context["issue_date"] = issue_date
        except ValueError:
            context["issue_date"] = date.isoformat(date.today())
    else:
        context["issue_date"] = date.isoformat(date.today())

    if due_date := request.GET.get("due_date"):
        try:
            date.fromisoformat(due_date)
            context["due_date"] = due_date
        except ValueError:
            ...

    if not due_date:
        context["issue_date"], context["due_date"] = defaults.get_issue_and_due_dates(context["issue_date"])

    if sort_code := (request.GET.get("sort_code") or "").replace("-", ""):
        if len(sort_code) == 6:
            if len(sort_code) >= 2:
                sort_code = sort_code[0:2] + "-" + sort_code[2:]
            if len(sort_code) >= 5:
                sort_code = sort_code[0:5] + "-" + sort_code[5:]
            context["sort_code"] = sort_code

    return CreateInvoiceContextServiceResponse(True, CreateInvoiceContextTuple(defaults, context))
