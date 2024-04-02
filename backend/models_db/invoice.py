from django.db import models
from decimal import Decimal
from django.core.validators import MaxValueValidator
from shortuuid.django_fields import ShortUUIDField

from settings import settings
from backend.models import Team, User, UserSettings
from backend.models_db.client import Client
from backend.models_db.utils import USER_OR_ORGANIZATION_CONSTRAINT
from settings.settings import AWS_TAGS_APP_NAME


class InvoiceProduct(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=100)
    quantity = models.IntegerField()
    rate = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)


class InvoiceItem(models.Model):
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=100)
    is_service = models.BooleanField(default=True)
    # if service
    hours = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    price_per_hour = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    # if product
    price = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)

    def get_total_price(self):
        return self.hours * self.price_per_hour if self.is_service else self.price

    def __str__(self):
        return self.description


class Invoice(models.Model):
    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("paid", "Paid"),
        ("overdue", "Overdue"),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    organization = models.ForeignKey(Team, on_delete=models.CASCADE, null=True, blank=True)
    invoice_id = models.IntegerField(unique=True, blank=True, null=True)  # todo: add

    client_to = models.ForeignKey(Client, on_delete=models.SET_NULL, blank=True, null=True)

    client_name = models.CharField(max_length=100, blank=True, null=True)
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
    reference = models.CharField(max_length=100, blank=True, null=True)
    invoice_number = models.CharField(max_length=100, blank=True, null=True)
    vat_number = models.CharField(max_length=100, blank=True, null=True)
    logo = models.ImageField(
        upload_to="invoice_logos",
        storage=settings.CustomPrivateMediaStorage(),
        blank=True,
        null=True,
    )
    notes = models.TextField(blank=True, null=True)

    payment_status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")
    items = models.ManyToManyField(InvoiceItem)
    currency = models.CharField(
        max_length=3,
        default="GBP",
        choices=[(code, info["name"]) for code, info in UserSettings.CURRENCIES.items()],
    )

    date_created = models.DateTimeField(auto_now_add=True)
    date_due = models.DateField()
    date_issued = models.DateField(blank=True, null=True)

    discount_amount = models.DecimalField(max_digits=15, default=0, decimal_places=2)
    discount_percentage = models.DecimalField(default=0, max_digits=5, decimal_places=2, validators=[MaxValueValidator(100)])

    class Meta:
        constraints = [USER_OR_ORGANIZATION_CONSTRAINT()]

    def __str__(self):
        invoice_id = self.invoice_id or self.id
        if self.client_name:
            client = self.client_name
        elif self.client_to:
            client = self.client_to.name
        else:
            client = "Unknown Client"

        return f"Invoice #{invoice_id} for {client}"

    @property
    def dynamic_payment_status(self):
        if self.date_due and timezone.now().date() > self.date_due and self.payment_status == "pending":
            return "overdue"
        else:
            return self.payment_status

    @property
    def get_to_details(self) -> tuple[str, dict[str, str]]:
        """
        Returns the client details for the invoice
        "client" and Client object if client_to
        "manual" and dict of details  if client_name
        """
        if self.client_to:
            return "client", self.client_to
        else:
            return "manual", {
                "name": self.client_name,
                "company": self.client_company,
            }

    def get_subtotal(self) -> Decimal:
        subtotal = 0
        for item in self.items.all():
            subtotal += item.get_total_price()
        return Decimal(round(subtotal, 2))

    def get_tax(self, amount: float = 0.00) -> float:
        amount = amount or self.get_subtotal()
        if self.vat_number:
            return round(amount * 0.2, 2)
        return 0

    def get_percentage_amount(self, subtotal: float = 0.00) -> Decimal:
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
            total = 0
        else:
            total -= self.get_tax(total)

        return Decimal(round(total, 2))

    def has_access(self, user: User) -> bool:
        if not user.is_authenticated:
            return False

        if user.logged_in_as_team:
            return self.organization == user.logged_in_as_team
        else:
            return self.user == user

    def get_currency_symbol(self):
        return UserSettings.CURRENCIES.get(self.currency, {}).get("symbol", "$")


class InvoiceURL(models.Model):
    uuid = ShortUUIDField(length=8, primary_key=True)
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name="invoice_urls")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    system_created = models.BooleanField(default=False)
    created_on = models.DateTimeField(auto_now_add=True)
    expires = models.DateTimeField(null=True, blank=True)
    never_expire = models.BooleanField(default=False)
    active = models.BooleanField(default=True)

    def is_active(self):
        if not self.active:
            return False
        if timezone.now() > self.expires:
            self.active = False
            self.save()
            return False
        return True

    def set_expires(self):
        self.expires = timezone.now() + timezone.timedelta(days=7)

    def save(self, *args, **kwargs):
        if not self.never_expire:
            self.set_expires()
        super().save()

    def __str__(self):
        return str(self.invoice.id)

    class Meta:
        verbose_name = "Invoice URL"
        verbose_name_plural = "Invoice URLs"


class InvoiceSchedule(models.Model):
    class StatusTypes(models.TextChoices):
        PENDING = "pending", "Pending"
        CREATING = "creating", "Creating"
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"
        DELETING = "deleting", "Deleting"
        CANCELLED = "cancelled", "Cancelled"

    created_at = models.DateTimeField(auto_now_add=True)
    stored_schedule_arn = models.CharField(max_length=500, null=True, blank=True)
    received = models.BooleanField(default=False)
    status = models.CharField(max_length=100, choices=StatusTypes.choices, default=StatusTypes.PENDING)

    def get_tags(self):
        return {"invoice_id": self.invoice.id, "schedule_id": self.id, "app": AWS_TAGS_APP_NAME}

    class Meta:
        abstract = True


class InvoiceOnetimeSchedule(InvoiceSchedule):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name="onetime_invoice_schedules")
    due = models.DateTimeField()

    class Meta:
        verbose_name = "One-Time Invoice Schedule"
        verbose_name_plural = "One-Time Invoice Schedules"
