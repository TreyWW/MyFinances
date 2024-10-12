from urllib.parse import urlencode

from backend.decorators import *
from backend.models import *
from backend.finance.views.invoices.handler import invoices_core_handler


@web_require_scopes("invoices:read", False, False, "dashboard")
def invoices_dashboard(request: WebRequest):
    return render(request, "pages/invoices/single/dashboard/dashboard.html")


@web_require_scopes("invoices:read", False, False, "finance:invoices:single:dashboard")
def manage_invoice(request: WebRequest, invoice_id: str):
    context: dict = {}

    if not invoice_id.isnumeric():
        messages.error(request, "Invalid invoice ID")
        return redirect("finance:invoices:single:dashboard")

    invoice = Invoice.objects.get(id=invoice_id)

    if not invoice:
        return redirect("finance:invoices:single:dashboard")

    if not invoice.has_access(request.user):
        return redirect("finance:invoices:single:dashboard")

    # "clone to recurring profile" url builder
    base_url = reverse("finance:invoices:recurring:create")
    query_params = {
        "frequency": "monthly",
        "day_of_month": 15,
        "account_holder_name": invoice.account_holder_name,
        "account_number": invoice.account_number,
        "sort_code": invoice.sort_code,
    }

    if invoice.client_to_id:
        query_params |= {
            "client": invoice.client_to_id,
            "from_name": invoice.self_name,
            "from_company": invoice.self_company,
            "from_address": invoice.self_address,
            "from_city": invoice.self_city,
            "from_county": invoice.self_county,
            "from_country": invoice.self_country,
        }
    else:
        query_params |= {
            "to_name": invoice.client_name,
            "to_company": invoice.client_company,
            "to_address": invoice.client_address,
            "to_city": invoice.client_city,
            "to_county": invoice.client_county,
            "to_country": invoice.client_country,
            "to_email": invoice.client_email,
        }

    context["clone_as_recurring_url"] = f"{base_url}?{urlencode(query_params)}"

    return invoices_core_handler(request, "pages/invoices/dashboard/manage.html", context | {"invoice": invoice})
