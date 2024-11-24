from datetime import datetime, date

from django.contrib import messages
from django.core.exceptions import PermissionDenied, ValidationError

from backend.finance.models import Invoice, InvoiceItem, Client, InvoiceProduct, DefaultValues
from backend.models import QuotaUsage
from backend.core.service.clients.validate import validate_client
from backend.core.service.defaults.get import get_account_defaults
from backend.core.service.invoices.common.create.create import save_invoice_common
from backend.core.types.requests import WebRequest


def get_invoice_context(request: WebRequest) -> dict:
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

    return context


def create_invoice_items(request: WebRequest):
    return [
        InvoiceItem.objects.create(name=row[0], description=row[1], hours=row[2], price_per_hour=row[3])
        for row in zip(
            request.POST.getlist("service_name[]"),
            request.POST.getlist("service_description[]"),
            request.POST.getlist("hours[]"),
            request.POST.getlist("price_per_hour[]"),
        )
    ]


def save_invoice(request: WebRequest, invoice_items):
    currency = request.user.user_profile.currency

    if not (date_due := request.POST.get("date_due")):
        messages.error(request, "Please enter a valid date")
        return None

    invoice = Invoice(
        date_due=datetime.strptime(date_due, "%Y-%m-%d").date(),
        date_issued=request.POST.get("date_issued"),
        currency=currency,
        reference=request.POST.get("reference"),
    )

    save_invoice_common(request, invoice_items, invoice)

    try:
        invoice.full_clean()
    except ValidationError as validation_errors:
        for field, error in validation_errors.error_dict.items():
            for e in error:
                messages.error(request, f"{field}: {e.messages[0]}")
        return None

    invoice.save()
    invoice.items.set(invoice_items)

    QuotaUsage.create_str(request.user, "invoices-count", invoice.id)

    return invoice
