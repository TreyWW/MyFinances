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

    try:
        invoice = Invoice.objects.get(id=invoice_id)
    except Invoice.DoesNotExist:
        messages.error(request, "Invoice not found")
        return redirect("invoices:dashboard")

    print(context | {"invoice": invoice})
    return render(request, "pages/invoices/dashboard/manage.html", context | {"invoice": invoice})
