from datetime import date
from decimal import Decimal

from django.db import transaction

from backend.models import User, Organization, Invoice, MonthlyReport, MonthlyReportRow
from backend.core.utils.dataclasses import BaseServiceResponse


class GenerateReportServiceResponse(BaseServiceResponse[MonthlyReport]): ...


@transaction.atomic
def generate_report(
    actor: User | Organization, start_date: date | str, end_date: date | str, name: str | None = None
) -> GenerateReportServiceResponse:
    all_invoices = Invoice.filter_by_owner(actor).filter(date_issued__gte=start_date, date_issued__lte=end_date).all()

    created_report = MonthlyReport.objects.create(owner=actor, start_date=start_date, end_date=end_date, name=name)  # type: ignore[misc]

    report_items = []

    for invoice in all_invoices:
        row = MonthlyReportRow(
            date=invoice.date_issued or invoice.date_created,
            reference_number=invoice.reference or invoice.id,
            item_type="invoice",
            paid_in=invoice.get_total_price(),
        )

        if invoice.client_to:
            row.client = invoice.client_to
        else:
            row.client_name = invoice.client_name

        created_report.payments_in += max(row.paid_in, Decimal(0))
        created_report.profit += row.paid_in - row.paid_out
        created_report.invoices_sent += 1

        if invoice.invoice_recurring_profile_id:
            created_report.recurring_customers += 1

        report_items.append(row)

    report_item_objs: list[MonthlyReportRow] = MonthlyReportRow.objects.bulk_create(report_items, batch_size=30)

    created_report.save()
    created_report.items.set(report_item_objs)
    created_report.save()

    return GenerateReportServiceResponse(success=True, response=created_report)
