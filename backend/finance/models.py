from __future__ import annotations
from datetime import datetime, date, timedelta
from decimal import Decimal
from typing import Literal
from uuid import uuid4
from django.core.validators import MaxValueValidator
from django.db import models
from django.utils import timezone
from shortuuid.django_fields import ShortUUIDField

from backend.clients.models import Client, DefaultValues
from backend.managers import InvoiceRecurringProfile_WithItemsManager

from backend.core.models import OwnerBase, UserSettings, _private_storage, USER_OR_ORGANIZATION_CONSTRAINT, User, ExpiresBase, Organization


class BotoSchedule(models.Model):
    class BotoStatusTypes(models.TextChoices):
        PENDING = "pending", "Pending"
        CREATING = "creating", "Creating"
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"
        DELETING = "deleting", "Deleting"
        CANCELLED = "cancelled", "Cancelled"

    created_at = models.DateTimeField(auto_now_add=True)

    boto_schedule_arn = models.CharField(max_length=2048, null=True, blank=True)
    boto_schedule_uuid = models.UUIDField(default=None, null=True, blank=True)
    boto_last_updated = models.DateTimeField(auto_now=True)

    received = models.BooleanField(default=False)
    boto_schedule_status = models.CharField(max_length=100, choices=BotoStatusTypes.choices, default=BotoStatusTypes.PENDING)

    class Meta:
        abstract = True

    def set_status(self, status, save=True):
        self.status = status
        if save:
            self.save()
        return self

    def set_received(self, status: bool = True, save=True):
        self.received = status
        if save:
            self.save()
        return self


class InvoiceProduct(OwnerBase):
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=100)
    quantity = models.IntegerField()
    rate = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)


class InvoiceItem(models.Model):
    # objects = InvoiceItemManager()

    name = models.CharField(max_length=50)
    description = models.CharField(max_length=100)
    is_service = models.BooleanField(default=True)
    # from
    # if service
    hours = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    price_per_hour = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    # if product
    price = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)

    def get_total_price(self):
        return self.hours * self.price_per_hour if self.is_service else self.price

    def __str__(self):
        return self.description


class InvoiceBase(OwnerBase):
    client_to = models.ForeignKey(Client, on_delete=models.SET_NULL, blank=True, null=True)

    client_name = models.CharField(max_length=100, blank=True, null=True)
    client_email = models.EmailField(blank=True, null=True)
    client_company = models.CharField(max_length=100, blank=True, null=True)
    client_address = models.CharField(max_length=100, blank=True, null=True)
    client_city = models.CharField(max_length=100, blank=True, null=True)
    client_county = models.CharField(max_length=100, blank=True, null=True)
    client_country = models.CharField(max_length=100, blank=True, null=True)
    client_is_representative = models.BooleanField(default=False)

    self_name = models.CharField(max_length=100, blank=True, null=True)
    self_company = models.CharField(max_length=100, blank=True, null=True)
    self_address = models.CharField(max_length=100, blank=True, null=True)
    self_city = models.CharField(max_length=100, blank=True, null=True)
    self_county = models.CharField(max_length=100, blank=True, null=True)
    self_country = models.CharField(max_length=100, blank=True, null=True)

    sort_code = models.CharField(max_length=8, blank=True, null=True)  # 12-34-56
    account_holder_name = models.CharField(max_length=100, blank=True, null=True)
    account_number = models.CharField(max_length=100, blank=True, null=True)
    vat_number = models.CharField(max_length=100, blank=True, null=True)
    logo = models.ImageField(
        upload_to="invoice_logos",
        storage=_private_storage,
        blank=True,
        null=True,
    )
    notes = models.TextField(blank=True, null=True)

    items = models.ManyToManyField(InvoiceItem, blank=True)
    currency = models.CharField(
        max_length=3,
        default="GBP",
        choices=[(code, info["name"]) for code, info in UserSettings.CURRENCIES.items()],
    )
    date_created = models.DateTimeField(auto_now_add=True)
    date_issued = models.DateField(blank=True, null=True)

    discount_amount = models.DecimalField(max_digits=15, default=0, decimal_places=2)
    discount_percentage = models.DecimalField(default=0, max_digits=5, decimal_places=2, validators=[MaxValueValidator(100)])

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        constraints = [USER_OR_ORGANIZATION_CONSTRAINT()]

    def has_access(self, user: User) -> bool:
        if not user.is_authenticated:
            return False

        if user.logged_in_as_team:
            return self.organization == user.logged_in_as_team
        else:
            return self.user == user

    def get_currency_symbol(self):
        return UserSettings.CURRENCIES.get(self.currency, {}).get("symbol", "$")


class Invoice(InvoiceBase):
    # objects = InvoiceManager()

    STATUS_CHOICES = (
        ("draft", "Draft"),
        # ("ready", "Ready"),
        ("pending", "Pending"),
        ("paid", "Paid"),
    )

    reference = models.CharField(max_length=16, blank=True, null=True)
    date_due = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="draft")
    status_updated_at = models.DateTimeField(auto_now_add=True)
    invoice_recurring_profile = models.ForeignKey(
        "InvoiceRecurringProfile", related_name="generated_invoices", on_delete=models.SET_NULL, blank=True, null=True
    )

    def __str__(self):
        if self.client_name:
            client = self.client_name
        elif self.client_to:
            client = self.client_to.name
        else:
            client = "Unknown Client"

        return f"Invoice #{self.id} for {client}"

    def set_status(self, status: str, save=True):
        if status not in ["draft", "pending", "paid"]:
            return False
        self.status = status
        self.status_updated_at = timezone.now()
        if save:
            self.save()
        return self

    @property
    def dynamic_status(self):
        if self.status == "pending" and self.is_overdue:
            return "overdue"
        else:
            return self.status

    @property
    def is_overdue(self):
        return self.date_due and timezone.now().date() > self.date_due

    @property
    def get_to_details(self) -> tuple[str, dict[str, str | None]] | tuple[str, Client]:
        """
        Returns the client details for the invoice
        "client" and Client object if client_to
        "manual" and dict of details  if client_name
        """
        if self.client_to:
            return "client", self.client_to
        else:
            return "manual", {"name": self.client_name, "company": self.client_company, "email": self.client_email}

    def get_subtotal(self) -> Decimal:
        subtotal = 0
        for item in self.items.all():
            subtotal += item.get_total_price()
        return Decimal(round(subtotal, 2))

    def get_tax(self, amount: Decimal = Decimal(0.00)) -> Decimal:
        amount = amount or self.get_subtotal()
        if self.vat_number:
            return Decimal(round(amount * Decimal(0.2), 2))
        return Decimal(0)

    def get_percentage_amount(self, subtotal: Decimal = Decimal(0.00)) -> Decimal:
        total = subtotal or self.get_subtotal()

        if self.discount_percentage > 0:
            return round(total * (self.discount_percentage / 100), 2)
        return Decimal(0)

    def get_total_price(self) -> Decimal:
        total = self.get_subtotal() or Decimal(0)

        total -= self.get_percentage_amount()

        discount_amount = self.discount_amount

        total -= discount_amount

        if 0 > total:
            total = Decimal(0)
        else:
            total -= self.get_tax(total)

        return Decimal(round(total, 2))


class InvoiceRecurringProfile(InvoiceBase, BotoSchedule):
    with_items = InvoiceRecurringProfile_WithItemsManager()

    class Frequencies(models.TextChoices):
        WEEKLY = "weekly", "Weekly"
        MONTHLY = "monthly", "Monthly"
        YEARLY = "yearly", "Yearly"

    STATUS_CHOICES = (
        ("ongoing", "Ongoing"),
        ("paused", "paused"),
        ("cancelled", "cancelled"),
    )

    active = models.BooleanField(default=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="paused")

    frequency = models.CharField(max_length=20, choices=Frequencies.choices, default=Frequencies.MONTHLY)
    end_date = models.DateField(blank=True, null=True)
    due_after_days = models.PositiveSmallIntegerField(default=7)

    day_of_week = models.PositiveSmallIntegerField(null=True, blank=True)
    day_of_month = models.PositiveSmallIntegerField(null=True, blank=True)
    month_of_year = models.PositiveSmallIntegerField(null=True, blank=True)

    def get_total_price(self) -> Decimal:
        total = Decimal(0)
        for invoice in self.generated_invoices.all():
            total += invoice.get_total_price()
        return Decimal(round(total, 2))

    def get_last_invoice(self) -> Invoice | None:
        return self.generated_invoices.order_by("-id").first()

    def next_invoice_issue_date(self) -> date:
        last_invoice = self.get_last_invoice()

        if not last_invoice:
            if self.date_issued is None:
                return datetime.now().date()
            return max(self.date_issued, datetime.now().date())

        last_invoice_date_issued: date = last_invoice.date_issued or datetime.now().date()

        match self.frequency:
            case "weekly":
                return last_invoice_date_issued + timedelta(days=7)
            case "monthly":
                return date(year=last_invoice_date_issued.year, month=last_invoice_date_issued.month + 1, day=last_invoice_date_issued.day)
            case "yearly":
                return date(year=last_invoice_date_issued.year + 1, month=last_invoice_date_issued.month, day=last_invoice_date_issued.day)
            case _:
                return datetime.now().date()

    def next_invoice_due_date(self, account_defaults: DefaultValues, from_date: date = datetime.now().date()) -> date:
        match account_defaults.invoice_due_date_type:
            case account_defaults.InvoiceDueDateType.days_after:
                return from_date + timedelta(days=account_defaults.invoice_due_date_value)
            case account_defaults.InvoiceDueDateType.date_following:
                return datetime(from_date.year, from_date.month + 1, account_defaults.invoice_due_date_value)
            case account_defaults.InvoiceDueDateType.date_current:
                return datetime(from_date.year, from_date.month, account_defaults.invoice_due_date_value)
            case _:
                return from_date + timedelta(days=7)


class InvoiceURL(ExpiresBase):
    uuid = ShortUUIDField(length=8, primary_key=True)
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name="invoice_urls")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    system_created = models.BooleanField(default=False)
    created_on = models.DateTimeField(auto_now_add=True)

    @property
    def get_created_by(self):
        if self.created_by:
            return self.created_by.first_name or f"USR #{self.created_by.id}"
        else:
            return "SYSTEM"

    def set_expires(self):
        self.expires = timezone.now() + timezone.timedelta(days=7)

    def __str__(self):
        return str(self.invoice.id)

    class Meta:
        verbose_name = "Invoice URL"
        verbose_name_plural = "Invoice URLs"


class InvoiceReminder(BotoSchedule):
    class ReminderTypes(models.TextChoices):
        BEFORE_DUE = "before_due", "Before Due"
        AFTER_DUE = "after_due", "After Due"
        ON_OVERDUE = "on_overdue", "On Overdue"

    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name="invoice_reminders")
    days = models.PositiveIntegerField(blank=True, null=True)
    reminder_type = models.CharField(max_length=100, choices=ReminderTypes.choices, default=ReminderTypes.BEFORE_DUE)

    class Meta:
        verbose_name = "Invoice Reminder"
        verbose_name_plural = "Invoice Reminders"

    def __str__(self):
        days = (str(self.days) + "d" if self.days else " ").center(8, "ㅤ")
        return f"({self.id}) Reminder for (#{self.invoice_id}) {days} {self.reminder_type}"


class MonthlyReportRow(models.Model):
    date = models.DateField()
    reference_number = models.CharField(max_length=100)
    item_type = models.CharField(max_length=100)

    client_name = models.CharField(max_length=64, blank=True, null=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, blank=True, null=True)

    paid_in = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    paid_out = models.DecimalField(max_digits=15, decimal_places=2, default=0)


class MonthlyReport(OwnerBase):
    uuid = models.UUIDField(default=uuid4, editable=False, unique=True)
    name = models.CharField(max_length=100, blank=True, null=True)
    items = models.ManyToManyField(MonthlyReportRow, blank=True)

    profit = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    invoices_sent = models.PositiveIntegerField(default=0)

    start_date = models.DateField()
    end_date = models.DateField()

    recurring_customers = models.PositiveIntegerField(default=0)
    payments_in = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    payments_out = models.DecimalField(max_digits=15, decimal_places=2, default=0)

    currency = models.CharField(
        max_length=3,
        default="GBP",
        choices=[(code, info["name"]) for code, info in UserSettings.CURRENCIES.items()],
    )

    def __str__(self):
        return self.name or str(self.uuid)[:8]

    def get_currency_symbol(self):
        return UserSettings.CURRENCIES.get(self.currency, {}).get("symbol", "$")


class Receipt(OwnerBase):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to="receipts", storage=_private_storage)
    total_price = models.FloatField(null=True, blank=True)
    date = models.DateField(null=True, blank=True)
    date_uploaded = models.DateTimeField(auto_now_add=True)
    receipt_parsed = models.JSONField(null=True, blank=True)
    merchant_store = models.CharField(max_length=255, blank=True, null=True)
    purchase_category = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return f"{self.name} - {self.date} ({self.total_price})"

    def has_access(self, actor: User | Organization) -> bool:
        return self.owner == actor


class ReceiptDownloadToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.ForeignKey(Receipt, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid4, editable=False, unique=True)
