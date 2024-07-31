from datetime import datetime, timedelta
from backend.models import Invoice, InvoiceRecurringSet, DefaultValues, AuditLog
from backend.service.defaults.get import get_account_defaults
from backend.utils.dataclasses import BaseServiceResponse

import logging

logger = logging.getLogger(__name__)


class GenerateNextInvoiceServiceResponse(BaseServiceResponse[Invoice]): ...


def generate_next_invoice_service(
    invoice_recurring_set: InvoiceRecurringSet,
    issue_date: datetime.date = datetime.now().date(),
    account_defaults: DefaultValues | None = None,
) -> GenerateNextInvoiceServiceResponse:

    if not invoice_recurring_set:
        return GenerateNextInvoiceServiceResponse(error_message="Invoice recurring set not found")

    generated_invoice = Invoice(
        invoice_recurring_set=invoice_recurring_set,
    )

    if invoice_recurring_set.client_to:
        account_defaults = account_defaults or get_account_defaults(invoice_recurring_set.owner, invoice_recurring_set.client_to)
        generated_invoice.client_to = invoice_recurring_set.client_to
    else:
        account_defaults = account_defaults or get_account_defaults(invoice_recurring_set.owner)
        generated_invoice.client_name = invoice_recurring_set.client_name
        generated_invoice.client_city = invoice_recurring_set.client_city
        generated_invoice.client_email = invoice_recurring_set.client_email
        generated_invoice.client_address = invoice_recurring_set.client_address
        generated_invoice.client_county = invoice_recurring_set.client_county
        generated_invoice.client_county = invoice_recurring_set.client_county
        generated_invoice.client_company = invoice_recurring_set.client_company

    generated_invoice.self_name = invoice_recurring_set.self_name
    generated_invoice.self_company = invoice_recurring_set.self_company
    generated_invoice.self_address = invoice_recurring_set.self_address
    generated_invoice.self_city = invoice_recurring_set.self_city
    generated_invoice.self_county = invoice_recurring_set.self_county
    generated_invoice.self_country = invoice_recurring_set.self_country

    INVOICE_DUE = invoice_recurring_set.next_invoice_due_date(account_defaults, from_date=issue_date)

    logger.info(f"Invoice due date calculated: {INVOICE_DUE}")

    generated_invoice.date_due = INVOICE_DUE
    generated_invoice.date_issued = issue_date
    generated_invoice.client_is_representative = invoice_recurring_set.client_is_representative

    generated_invoice.sort_code = invoice_recurring_set.sort_code
    generated_invoice.account_holder_name = invoice_recurring_set.account_holder_name
    generated_invoice.account_number = invoice_recurring_set.account_number

    generated_invoice.vat_number = invoice_recurring_set.vat_number
    generated_invoice.logo = invoice_recurring_set.logo
    generated_invoice.notes = invoice_recurring_set.notes

    generated_invoice.currency = invoice_recurring_set.currency
    generated_invoice.discount_amount = invoice_recurring_set.discount_amount
    generated_invoice.discount_percentage = invoice_recurring_set.discount_percentage
    generated_invoice.owner = invoice_recurring_set.owner

    generated_invoice.save()

    generated_invoice.items.set(invoice_recurring_set.items.all())

    generated_invoice.save(update_fields=["invoice_recurring_set"])

    logger.info(f"Invoice generated with the ID of {generated_invoice.pk}")

    AuditLog.objects.create(
        action=f"[SYSTEM] Generated invoice #{generated_invoice.pk} from Recurring Set #{invoice_recurring_set.pk}",
        owner=invoice_recurring_set.owner,
    )

    return GenerateNextInvoiceServiceResponse(True, generated_invoice)
