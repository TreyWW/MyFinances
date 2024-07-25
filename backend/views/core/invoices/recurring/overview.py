from backend.decorators import *
from backend.models import *
from backend.types.htmx import HtmxHttpRequest
from backend.views.core.invoices.handler import invoices_core_handler


@web_require_scopes("invoices:read", False, False, "dashboard")
def invoices_dashboard(request: WebRequest):
    return render(request, "pages/invoices/dashboard/../../../../../frontend/templates/pages/invoices/single/dashboard/dashboard.html")


@web_require_scopes("invoices:read", False, False, "invoices:single:dashboard")
def manage_invoice(request: WebRequest, invoice_id: str):
    context: dict = {}

    if not invoice_id.isnumeric():
        messages.error(request, "Invalid invoice ID")
        return redirect("invoices:single:dashboard")

    invoice = Invoice.objects.get(id=invoice_id)

    if not invoice:
        return redirect("invoices:single:dashboard")

    if not invoice.has_access(request.user):
        return redirect("invoices:single:dashboard")

    return invoices_core_handler(request, "pages/invoices/dashboard/manage.html", context | {"invoice": invoice})
