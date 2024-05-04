from backend.decorators import *
from backend.models import *
from backend.types.htmx import HtmxHttpRequest


def invoices_dashboard(request: HtmxHttpRequest):
    return render(request, "pages/invoices/dashboard/dashboard.html")


def manage_invoice(request: HtmxHttpRequest, invoice_id: str):
    context: dict = {}

    if not invoice_id.isnumeric():
        messages.error(request, "Invalid invoice ID")
        return redirect("invoices:dashboard")

    invoice = Invoice.objects.get(id=invoice_id)

    if not invoice:
        return redirect("invoices:dashboard")

    print(context | {"invoice": invoice})
    return render(request, "pages/invoices/dashboard/manage.html", context | {"invoice": invoice})
