from __future__ import annotations

from django.contrib import messages
from django.shortcuts import redirect
from django.shortcuts import render
from django.http import HttpResponse
from django.template.loader import get_template

from io import BytesIO
from xhtml2pdf import pisa
from login_required import login_not_required

from backend.models import Invoice, UserSettings
from backend.models import InvoiceURL


def render_to_pdf(template_src, context_dict):
    template = get_template(template_src)
    html = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None


def preview(request, invoice_id):
    invoice = Invoice.objects.filter(id=invoice_id).prefetch_related("items").first()

    context = {
        'invoice': invoice,
    }

    if not invoice:
        messages.error(request, "Invoice not found")
        return redirect("invoices:dashboard")

    if request.user.logged_in_as_team and invoice.organization != request.user.logged_in_as_team:
        messages.error(request, "You don't have access to this invoice")
        return redirect("invoices:dashboard")
    elif invoice.user != request.user:
        messages.error(request, "You don't have access to this invoice")
        return redirect("invoices:dashboard")

    try:
        currency_symbol = invoice.get_currency_symbol()
    except UserSettings.DoesNotExist:
        currency_symbol = "$"

    context.update({"invoice": invoice, "currency_symbol": currency_symbol})

    pdf = render_to_pdf('pages/invoices/view/invoice_page.html', context)

    if pdf:
        response = HttpResponse(pdf, content_type='application/pdf')
        content = f"inline; filename=invoice_{invoice.id}.pdf"
        response['Content-Disposition'] = content
        return response
    return HttpResponse("Error generating PDF", status=400)


@login_not_required
def view(request, uuid):
    context = {"type": "view"}

    try:
        url = InvoiceURL.objects.select_related("invoice").prefetch_related("invoice", "invoice__items").get(uuid=uuid)
        invoice = url.invoice
        if not invoice:
            raise InvoiceURL.DoesNotExist
    except InvoiceURL.DoesNotExist:
        messages.error(request, "Invoice not found")
        return redirect("index")

    currency_symbol = invoice.get_currency_symbol()

    context.update({"invoice": invoice, "currency_symbol": currency_symbol})

    return render(
        request,
        "pages/invoices/view/invoice_page.html",
        context,
    )
