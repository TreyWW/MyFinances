from uuid import uuid4
from datetime import date, timedelta
from django.db import models
from backend.core.data.default_email_templates import (
    recurring_invoices_invoice_created_default_email_template,
    recurring_invoices_invoice_overdue_default_email_template,
    recurring_invoices_invoice_cancelled_default_email_template,
)
from backend.core.models import OwnerBase, User, UserSettings, _private_storage


class Client(OwnerBase):
    id = models.BigAutoField(primary_key=True)  # Internal primary key
    public_id = models.CharField(max_length=36, unique=True, editable=False)  # Prefixed public-facing ID

    active = models.BooleanField(default=True)
    name = models.CharField(max_length=64)
    phone_number = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    email_verified = models.BooleanField(default=False)
    company = models.CharField(max_length=100, blank=True, null=True)
    contact_method = models.CharField(max_length=100, blank=True, null=True)
    is_representative = models.BooleanField(default=False)

    address = models.TextField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.public_id:
            self.public_id = f"cl_{uuid4().hex[:8]}"  # Generate public-facing ID with prefix
        super().save(*args, **kwargs)

    def has_access(self, user: User) -> bool:
        if not user.is_authenticated:
            return False
        return self.organization == user.logged_in_as_team if user.logged_in_as_team else self.user == user


class DefaultValues(OwnerBase):
    id = models.BigAutoField(primary_key=True)
    public_id = models.CharField(max_length=36, unique=True, editable=False)  # Prefixed public-facing ID

    class InvoiceDueDateType(models.TextChoices):
        days_after = "days_after"
        date_following = "date_following"
        date_current = "date_current"

    class InvoiceDateType(models.TextChoices):
        day_of_month = "day_of_month"
        days_after = "days_after"

    client = models.OneToOneField(Client, on_delete=models.CASCADE, related_name="default_values", null=True, blank=True)

    currency = models.CharField(
        max_length=3,
        default="GBP",
        choices=[(code, info["name"]) for code, info in UserSettings.CURRENCIES.items()],
    )
    invoice_due_date_value = models.PositiveSmallIntegerField(default=7)
    invoice_due_date_type = models.CharField(max_length=20, choices=InvoiceDueDateType.choices, default=InvoiceDueDateType.days_after)
    invoice_date_value = models.PositiveSmallIntegerField(default=15)
    invoice_date_type = models.CharField(max_length=20, choices=InvoiceDateType.choices, default=InvoiceDateType.day_of_month)

    invoice_from_name = models.CharField(max_length=100, null=True, blank=True)
    invoice_from_company = models.CharField(max_length=100, null=True, blank=True)
    invoice_from_address = models.CharField(max_length=100, null=True, blank=True)
    invoice_from_city = models.CharField(max_length=100, null=True, blank=True)
    invoice_from_county = models.CharField(max_length=100, null=True, blank=True)
    invoice_from_country = models.CharField(max_length=100, null=True, blank=True)
    invoice_from_email = models.CharField(max_length=100, null=True, blank=True)

    invoice_account_number = models.CharField(max_length=100, null=True, blank=True)
    invoice_sort_code = models.CharField(max_length=100, null=True, blank=True)
    invoice_account_holder_name = models.CharField(max_length=100, null=True, blank=True)

    email_template_recurring_invoices_invoice_created = models.TextField(default=recurring_invoices_invoice_created_default_email_template)
    email_template_recurring_invoices_invoice_overdue = models.TextField(default=recurring_invoices_invoice_overdue_default_email_template)
    email_template_recurring_invoices_invoice_cancelled = models.TextField(
        default=recurring_invoices_invoice_cancelled_default_email_template
    )

    def save(self, *args, **kwargs):
        if not self.public_id:
            self.public_id = f"dv_{uuid4().hex[:8]}"  # Generate public-facing ID with prefix
        super().save(*args, **kwargs)

    def get_issue_and_due_dates(self, issue_date: date | str | None = None) -> tuple[str, str]:
        issue = date.fromisoformat(issue_date) if isinstance(issue_date, str) else issue_date or date.today()

        if self.invoice_due_date_type == self.InvoiceDueDateType.days_after:
            due = issue + timedelta(days=self.invoice_due_date_value)
        elif self.invoice_due_date_type == self.InvoiceDueDateType.date_following:
            month = issue.month + 1 if issue.month < 12 else 1
            year = issue.year if issue.month < 12 else issue.year + 1
            due = date(year, month, self.invoice_due_date_value)
        elif self.invoice_due_date_type == self.InvoiceDueDateType.date_current:
            due = date(issue.year, issue.month, self.invoice_due_date_value)
        else:
            raise ValueError("Invalid invoice due date type")

        return date.isoformat(issue), date.isoformat(due)

    default_invoice_logo = models.ImageField(
        upload_to="invoice_logos/",
        storage=_private_storage,
        blank=True,
        null=True,
    )
