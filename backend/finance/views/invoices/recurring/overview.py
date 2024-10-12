from backend.decorators import *
from backend.models import *
from backend.core.service.defaults.get import get_account_defaults
from backend.finance.views.invoices.handler import invoices_core_handler


@web_require_scopes("invoices:read", False, False, "dashboard")
def invoices_dashboard(request: WebRequest):
    return render(request, "pages/invoices/recurring/dashboard/dashboard.html")


@web_require_scopes("invoices:read", False, False, "finance:invoices:single:dashboard")
def manage_recurring_invoice_profile_endpoint(request: WebRequest, invoice_profile_id: str):
    context: dict = {}

    if not invoice_profile_id.isnumeric():
        messages.error(request, "Invalid invoice ID")
        return redirect("finance:invoices:single:dashboard")

    invoice_profile = InvoiceRecurringProfile.with_items.get(id=invoice_profile_id, active=True)

    if invoice_profile.client_to:
        context["client_name"] = invoice_profile.client_to.name
        context["client_email"] = invoice_profile.client_to.email
        context["client_is_representative"] = invoice_profile.client_to.is_representative
    else:
        context["client_name"] = invoice_profile.client_name
        context["client_email"] = invoice_profile.client_email
        context["client_is_representative"] = invoice_profile.client_is_representative

    context["total_amt"] = 0
    context["total_count"] = invoice_profile.generated_invoices.count()
    context["total_paid"] = 0

    for invoice in invoice_profile.generated_invoices.all():
        if invoice.status == "paid":
            context["total_paid"] += 1
        context["total_amt"] += invoice.get_total_price()

    ACCOUNT_DEFAULTS = get_account_defaults(request.actor, invoice_profile.client_to)

    context["next_invoice_issue_date"] = invoice_profile.next_invoice_issue_date()
    context["next_invoice_due_date"] = invoice_profile.next_invoice_due_date(
        account_defaults=ACCOUNT_DEFAULTS, from_date=context["next_invoice_issue_date"]
    )

    if not invoice_profile:
        messages.error(request, "Invalid invoice profile")
        return redirect("finance:invoices:recurring:dashboard")

    if not invoice_profile.has_access(request.user):
        messages.error(request, "You do not have access to this invoice profile")
        return redirect("finance:invoices:recurring:dashboard")

    return invoices_core_handler(request, "pages/invoices/recurring/dashboard/manage.html", context | {"invoiceProfile": invoice_profile})
