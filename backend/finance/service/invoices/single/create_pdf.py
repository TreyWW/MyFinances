from io import BytesIO

from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa

from backend.finance.models import UserSettings, Invoice


def render_to_pdf(template_src: str, context_dict: dict) -> HttpResponse | None:
    template = get_template(template_src)
    html = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type="application/pdf")
    return None


def generate_pdf(invoice: Invoice, content_type: str) -> HttpResponse | None:
    try:
        currency_symbol = invoice.get_currency_symbol()
    except UserSettings.DoesNotExist:
        currency_symbol = "$"

    context = {
        "invoice": invoice,
        "currency_symbol": currency_symbol,
        "img_path": invoice.logo.path.replace("\\", "/") if invoice.logo else None,
    }

    pdf = render_to_pdf("pages/invoices/single/view/invoice_page.html", context)

    if pdf:
        response = HttpResponse(pdf, content_type="application/pdf")
        content = f"{content_type}; filename=invoice_{invoice.id}.pdf"
        response["Content-Disposition"] = content
        return response
    return None
