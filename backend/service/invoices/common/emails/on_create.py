from string import Template
from textwrap import dedent

from backend.models import Invoice, InvoiceRecurringProfile, User, EmailSendStatus
from backend.utils.dataclasses import BaseServiceResponse
from backend.utils.service_retry import retry_handler
from settings.helpers import send_email


class OnCreateInvoiceEmailServiceResponse(BaseServiceResponse[str]): ...


def on_create_invoice_service(users_email: str, invoice: Invoice) -> OnCreateInvoiceEmailServiceResponse:
    if not users_email:
        return OnCreateInvoiceEmailServiceResponse(error_message="User email not found")

    if not invoice:
        return OnCreateInvoiceEmailServiceResponse(error_message="Invoice not found")

    email_message = dedent(
        """
        Hi $first_name,

        The invoice #$invoice_id has been created for you to pay, due on the $due_date. Please pay at your earliest convenience.

        Balance Due: $currency_symbol$amount_due $currency

        Many thanks,
        $company_name
    """
    )

    user_data = {
        "first_name": invoice.client_to.name.split(" ")[0] if invoice.client_to else invoice.client_name,
        "invoice_id": invoice.id,
        "invoice_ref": invoice.reference or invoice.invoice_number or invoice.id,
        "due_date": invoice.date_due.strftime("%a %m %Y"),
        "amount_due": invoice.get_total_price(),
        "currency": invoice.currency,
        "currency_symbol": invoice.get_currency_symbol(),
        "product_list": [],  # todo
        "company_name": invoice.self_company or invoice.self_name,
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

    EmailSendStatus.objects.create(
        status="send",
        owner=invoice.owner,
        recipient=users_email,
        aws_message_id=email_svc_response.response.get("MessageId"),
    )

    return OnCreateInvoiceEmailServiceResponse(True, response="Email sent successfully")
