from string import Template

from django.urls import reverse

from backend.core.data.default_email_templates import email_footer
from backend.models import Invoice, EmailSendStatus, InvoiceURL
from backend.core.service.defaults.get import get_account_defaults
from backend.core.service.invoices.single.create_url import create_invoice_url
from backend.core.utils.dataclasses import BaseServiceResponse
from backend.core.utils.service_retry import retry_handler
from settings.helpers import send_email, get_var

"""
DOCS: https://docs.myfinances.cloud/user-guide/emails/templates/
(please update if any variables are changed)
"""


class OnCreateInvoiceEmailServiceResponse(BaseServiceResponse[EmailSendStatus]): ...


def on_create_invoice_email_service(users_email: str, invoice: Invoice) -> OnCreateInvoiceEmailServiceResponse:
    if not users_email:
        return OnCreateInvoiceEmailServiceResponse(error_message="User email not found")

    if not invoice:
        return OnCreateInvoiceEmailServiceResponse(error_message="Invoice not found")

    defaults = get_account_defaults(invoice.owner, invoice.client_to)

    email_message: str = defaults.email_template_recurring_invoices_invoice_created + email_footer()

    invoice_url: InvoiceURL = create_invoice_url(invoice).response

    user_data = {
        "first_name": invoice.client_to.name.split(" ")[0] if invoice.client_to else invoice.client_name,
        "invoice_id": invoice.id,
        "invoice_ref": invoice.reference or invoice.id,
        "due_date": invoice.date_due.strftime("%A, %B %d, %Y"),
        "amount_due": invoice.get_total_price(),
        "currency": invoice.currency,
        "currency_symbol": invoice.get_currency_symbol(),
        "product_list": [],  # todo
        "company_name": invoice.self_company or invoice.self_name or "MyFinances Customer",
        "invoice_link": get_var("SITE_URL") + reverse("invoices view invoice", kwargs={"uuid": str(invoice_url.uuid)}),
    }

    output: str = Template(email_message).substitute(user_data)

    email_svc_response = retry_handler(
        send_email,
        destination=invoice.client_to.email or invoice.client_email if invoice.client_to else invoice.client_email,
        subject=f"Invoice #{invoice.id} from {invoice.self_company or invoice.self_name}",
        content=output,
    )

    if email_svc_response.failed:
        return OnCreateInvoiceEmailServiceResponse(False, error_message="Failed to send email")

    email_status_obj = EmailSendStatus.objects.create(
        status="send",
        owner=invoice.owner,
        recipient=users_email,
        aws_message_id=email_svc_response.response.get("MessageId"),
    )

    return OnCreateInvoiceEmailServiceResponse(True, response=email_status_obj)
