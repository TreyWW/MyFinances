from backend.decorators import *
from backend.models import *
from backend.types.htmx import HtmxHttpRequest
from backend.views.core.invoices.handler import invoices_core_handler


@web_require_scopes("invoices:read", False, False, "dashboard")
def invoices_dashboard(request: WebRequest):
    return render(request, "pages/invoices/recurring/dashboard/dashboard.html")


@web_require_scopes("invoices:read", False, False, "invoices:single:dashboard")
def manage_recurring_invoice_set_endpoint(request: WebRequest, invoice_id: str):
    context: dict = {}

    if not invoice_id.isnumeric():
        messages.error(request, "Invalid invoice ID")
        return redirect("invoices:single:dashboard")

    invoice_set = InvoiceRecurringSet.objects.get(id=invoice_id)

    if not invoice_set:
        return redirect("invoices:single:dashboard")

    if not invoice_set.has_access(request.user):
        return redirect("invoices:single:dashboard")

    return invoices_core_handler(request, "pages/invoices/recurring/dashboard/manage.html", context | {"invoiceSet": invoice_set})
