from __future__ import annotations

from datetime import date, timedelta
from django.db import models
from backend.data.default_email_templates import (
    recurring_invoices_invoice_created_default_email_template,
    recurring_invoices_invoice_overdue_default_email_template,
    recurring_invoices_invoice_cancelled_default_email_template,
)
from backend.models import _private_storage, DefaultValuesBase

# class FinanceDefaultValues(DefaultValuesBase):
#     class InvoiceDueDateType(models.TextChoices):
#         days_after = "days_after"
#         date_following = "date_following"
#         date_current = "date_current"
#
#     class InvoiceDateType(models.TextChoices):
#         day_of_month = "day_of_month"
#         days_after = "days_after"
#
#     invoice_due_date_value = models.PositiveSmallIntegerField(default=7, null=False, blank=False)
#     invoice_due_date_type = models.CharField(
#         max_length=20,
#         choices=InvoiceDueDateType.choices,
#         default=InvoiceDueDateType.days_after,
#     )
#
#     invoice_date_value = models.PositiveSmallIntegerField(default=15, null=False, blank=False)
#     invoice_date_type = models.CharField(
#         max_length=20,
#         choices=InvoiceDateType.choices,
#         default=InvoiceDateType.day_of_month,
#     )
#
#     invoice_from_name = models.CharField(max_length=100, null=True, blank=True)
#     invoice_from_company = models.CharField(max_length=100, null=True, blank=True)
#     invoice_from_address = models.CharField(max_length=100, null=True, blank=True)
#     invoice_from_city = models.CharField(max_length=100, null=True, blank=True)
#     invoice_from_county = models.CharField(max_length=100, null=True, blank=True)
#     invoice_from_country = models.CharField(max_length=100, null=True, blank=True)
#     invoice_from_email = models.CharField(max_length=100, null=True, blank=True)
#
#     invoice_account_number = models.CharField(max_length=100, null=True, blank=True)
#     invoice_sort_code = models.CharField(max_length=100, null=True, blank=True)
#     invoice_account_holder_name = models.CharField(max_length=100, null=True, blank=True)
#
#     email_template_recurring_invoices_invoice_created = models.TextField(default=recurring_invoices_invoice_created_default_email_template)
#     email_template_recurring_invoices_invoice_overdue = models.TextField(default=recurring_invoices_invoice_overdue_default_email_template)
#     email_template_recurring_invoices_invoice_cancelled = models.TextField(
#         default=recurring_invoices_invoice_cancelled_default_email_template
#     )
#
#     default_invoice_logo = models.ImageField(
#         upload_to="invoice_logos/",
#         storage=_private_storage,
#         blank=True,
#         null=True,
#     )
#
#     def get_issue_and_due_dates(self, issue_date: date | str | None = None) -> tuple[str, str]:
#         due: date
#         issue: date
#
#         if isinstance(issue_date, str):
#             issue = date.fromisoformat(issue_date) or date.today()
#         else:
#             issue = issue_date or date.today()
#
#         match self.invoice_due_date_type:
#             case self.InvoiceDueDateType.days_after:
#                 due = issue + timedelta(days=self.invoice_due_date_value)
#             case self.InvoiceDueDateType.date_following:
#                 due = date(issue.year, issue.month + 1, self.invoice_due_date_value)
#             case self.InvoiceDueDateType.date_current:
#                 due = date(issue.year, issue.month, self.invoice_due_date_value)
#             case _:
#                 raise ValueError("Invalid invoice due date type")
#         return date.isoformat(issue), date.isoformat(due)
