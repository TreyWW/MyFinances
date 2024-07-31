from django.db.models import Subquery

from backend.decorators import *
from backend.models import *
from backend.service.defaults.get import get_account_defaults
from backend.types.htmx import HtmxHttpRequest
from backend.views.core.invoices.handler import invoices_core_handler


@web_require_scopes("invoices:read", False, False, "dashboard")
def invoices_dashboard(request: WebRequest):
    return render(request, "pages/invoices/recurring/dashboard/dashboard.html")


@web_require_scopes("invoices:read", False, False, "invoices:single:dashboard")
def manage_recurring_invoice_set_endpoint(request: WebRequest, invoice_set_id: str):
    context: dict = {}

    if not invoice_set_id.isnumeric():
        messages.error(request, "Invalid invoice ID")
        return redirect("invoices:single:dashboard")

    invoice_set = InvoiceRecurringSet.with_items.get(id=invoice_set_id)

    if invoice_set.client_to:
        context["client_name"] = invoice_set.client_to.name
        context["client_email"] = invoice_set.client_to.email
        context["client_is_representative"] = invoice_set.client_to.is_representative
    else:
        context["client_name"] = invoice_set.client_name
        context["client_email"] = invoice_set.client_email
        context["client_is_representative"] = invoice_set.client_is_representative

    context["total_amt"] = 0
    context["total_count"] = invoice_set.generated_invoices.count()
    context["total_paid"] = 0

    for invoice in invoice_set.generated_invoices.all():
        if invoice.payment_status == "paid":
            context["total_paid"] += 1
        context["total_amt"] += invoice.get_total_price()

    ACCOUNT_DEFAULTS = get_account_defaults(request.actor, invoice_set.client_to)

    context["next_invoice_issue_date"] = invoice_set.next_invoice_issue_date()
    context["next_invoice_due_date"] = invoice_set.next_invoice_due_date(
        account_defaults=ACCOUNT_DEFAULTS, from_date=context["next_invoice_issue_date"]
    )

    if not invoice_set:
        return redirect("invoices:single:dashboard")

    if not invoice_set.has_access(request.user):
        return redirect("invoices:single:dashboard")

    return invoices_core_handler(request, "pages/invoices/recurring/dashboard/manage.html", context | {"invoiceSet": invoice_set})
