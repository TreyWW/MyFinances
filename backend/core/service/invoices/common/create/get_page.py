from datetime import date
from typing import NamedTuple
from django.core.exceptions import PermissionDenied, ValidationError

from backend.models import Client, InvoiceProduct, DefaultValues
from backend.core.service.clients.validate import validate_client
from backend.core.service.defaults.get import get_account_defaults
from backend.core.types.requests import WebRequest
from backend.core.utils.dataclasses import BaseServiceResponse


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

    for item in ["name", "company", "address", "city", "county", "country", "email"]:
        context[f"from_{item}"] = request.GET.get(f"from_{item}", "")

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

    if account_holder_name := request.GET.get("account_holder_name"):
        context["account_holder_name"] = account_holder_name

    if account_number := request.GET.get("account_number"):
        context["account_number"] = account_number

    details_from = ["name", "company", "address", "city", "county", "country", "email"]

    for detail in details_from:
        detail_value = request.GET.get(f"from_{detail}", "")

        if not detail_value:
            detail_value = getattr(defaults, f"invoice_from_{detail}")

        context[f"from_{detail}"] = detail_value

    payment_details = ["sort_code", "account_holder_name", "account_number"]

    for detail in payment_details:
        detail_value = request.GET.get(detail, "")

        if not detail_value:
            detail_value = getattr(defaults, f"invoice_{detail}")

        context[detail] = detail_value

    return CreateInvoiceContextServiceResponse(True, CreateInvoiceContextTuple(defaults, context))
