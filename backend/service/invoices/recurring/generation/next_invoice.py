from datetime import datetime, date, timedelta
from backend.models import Invoice, InvoiceRecurringProfile, DefaultValues, AuditLog
from backend.service.defaults.get import get_account_defaults
from backend.utils.dataclasses import BaseServiceResponse

import logging

logger = logging.getLogger(__name__)


class GenerateNextInvoiceServiceResponse(BaseServiceResponse[Invoice]): ...


def generate_next_invoice_service(
    invoice_recurring_profile: InvoiceRecurringProfile,
    issue_date: date = date.today(),
    account_defaults: DefaultValues | None = None,
) -> GenerateNextInvoiceServiceResponse:
    """
    This will generate the next single invoice based on the invoice recurring profile
    """

    if not invoice_recurring_profile:
        return GenerateNextInvoiceServiceResponse(error_message="Invoice recurring profile not found")

    generated_invoice = Invoice(
        invoice_recurring_profile=invoice_recurring_profile,
    )

    if invoice_recurring_profile.client_to:
        account_defaults = account_defaults or get_account_defaults(invoice_recurring_profile.owner, invoice_recurring_profile.client_to)
        generated_invoice.client_to = invoice_recurring_profile.client_to
    else:
        account_defaults = account_defaults or get_account_defaults(invoice_recurring_profile.owner)
        generated_invoice.client_name = invoice_recurring_profile.client_name
        generated_invoice.client_city = invoice_recurring_profile.client_city
        generated_invoice.client_email = invoice_recurring_profile.client_email
        generated_invoice.client_address = invoice_recurring_profile.client_address
        generated_invoice.client_county = invoice_recurring_profile.client_county
        generated_invoice.client_county = invoice_recurring_profile.client_county
        generated_invoice.client_company = invoice_recurring_profile.client_company

    generated_invoice.self_name = invoice_recurring_profile.self_name
    generated_invoice.self_company = invoice_recurring_profile.self_company
    generated_invoice.self_address = invoice_recurring_profile.self_address
    generated_invoice.self_city = invoice_recurring_profile.self_city
    generated_invoice.self_county = invoice_recurring_profile.self_county
    generated_invoice.self_country = invoice_recurring_profile.self_country

    INVOICE_DUE = invoice_recurring_profile.next_invoice_due_date(account_defaults, from_date=issue_date)

    logger.info(f"Invoice due date calculated: {INVOICE_DUE}")

    generated_invoice.date_due = INVOICE_DUE
    generated_invoice.date_issued = issue_date
    generated_invoice.client_is_representative = invoice_recurring_profile.client_is_representative

    generated_invoice.sort_code = invoice_recurring_profile.sort_code
    generated_invoice.account_holder_name = invoice_recurring_profile.account_holder_name
    generated_invoice.account_number = invoice_recurring_profile.account_number

    generated_invoice.vat_number = invoice_recurring_profile.vat_number
    generated_invoice.logo = invoice_recurring_profile.logo
    generated_invoice.notes = invoice_recurring_profile.notes

    generated_invoice.currency = invoice_recurring_profile.currency
    generated_invoice.discount_amount = invoice_recurring_profile.discount_amount
    generated_invoice.discount_percentage = invoice_recurring_profile.discount_percentage
    generated_invoice.owner = invoice_recurring_profile.owner

    generated_invoice.save()

    generated_invoice.items.set(invoice_recurring_profile.items.all())

    generated_invoice.save(update_fields=["invoice_recurring_profile"])

    logger.info(f"Invoice generated with the ID of {generated_invoice.pk}")

    AuditLog.objects.create(
        action=f"[SYSTEM] Generated invoice #{generated_invoice.pk} from the recurring profile #{invoice_recurring_profile.pk}",
        user=invoice_recurring_profile.user,
        organization=invoice_recurring_profile.organization,
    )

    return GenerateNextInvoiceServiceResponse(True, generated_invoice)
