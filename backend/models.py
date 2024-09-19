from __future__ import annotations

import typing
from datetime import datetime, date, timedelta
from decimal import Decimal
from typing import Literal, Union
from uuid import uuid4

from dateutil.relativedelta import relativedelta
from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.models import AbstractUser, UserManager
from django.contrib.contenttypes.models import ContentType
from django.core.files.storage import storages, FileSystemStorage
from django.core.validators import MaxValueValidator
from django.db import models, transaction
from django.db.models import Count, QuerySet
from django.utils import timezone
from django.utils.crypto import get_random_string
from shortuuid.django_fields import ShortUUIDField
from storages.backends.s3 import S3Storage

from backend.managers import InvoiceRecurringProfile_WithItemsManager


def _public_storage():
    return storages["public_media"]


def _private_storage() -> FileSystemStorage | S3Storage:
    return storages["private_media"]


def RandomCode(length=6):
    return get_random_string(length=length).upper()


def RandomAPICode(length=89):
    return get_random_string(length=length).lower()


def upload_to_user_separate_folder(instance, filename, optional_actor=None) -> str:
    instance_name = instance._meta.verbose_name.replace(" ", "-")

    print(instance, filename)

    if optional_actor:
        if isinstance(optional_actor, User):
            return f"{instance_name}/users/{optional_actor.id}/{filename}"
        elif isinstance(optional_actor, Organization):
            return f"{instance_name}/orgs/{optional_actor.id}/{filename}"
        return f"{instance_name}/global/{filename}"

    if hasattr(instance, "user") and hasattr(instance.user, "id"):
        return f"{instance_name}/users/{instance.user.id}/{filename}"
    elif hasattr(instance, "organization") and hasattr(instance.organization, "id"):
        return f"{instance_name}/orgs/{instance.organization.id}/{filename}"
    return f"{instance_name}/global/{filename}"


def USER_OR_ORGANIZATION_CONSTRAINT():
    return models.CheckConstraint(
        name=f"%(app_label)s_%(class)s_check_user_or_organization",
        check=(models.Q(user__isnull=True, organization__isnull=False) | models.Q(user__isnull=False, organization__isnull=True)),
    )


M = typing.TypeVar("M", bound=models.Model)


class CustomUserManager(UserManager):
    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .select_related("user_profile", "logged_in_as_team")
            .annotate(notification_count=(Count("user_notifications")))
        )


class User(AbstractUser):
    objects: CustomUserManager = CustomUserManager()  # type: ignore

    logged_in_as_team = models.ForeignKey("Organization", on_delete=models.SET_NULL, null=True, blank=True)
    stripe_customer_id = models.CharField(max_length=255, null=True, blank=True)
    entitlements = models.JSONField(null=True, blank=True, default=list)  # list of strings e.g. ["invoices"]
    awaiting_email_verification = models.BooleanField(default=True)
    require_change_password = models.BooleanField(default=False)  # does user need to change password upon next login

    class Role(models.TextChoices):
        #        NAME     DJANGO ADMIN NAME
        DEV = "DEV", "Developer"
        STAFF = "STAFF", "Staff"
        USER = "USER", "User"
        TESTER = "TESTER", "Tester"

    role = models.CharField(max_length=10, choices=Role.choices, default=Role.USER)


def add_3hrs_from_now():
    return timezone.now() + timezone.timedelta(hours=3)


class VerificationCodes(models.Model):
    class ServiceTypes(models.TextChoices):
        CREATE_ACCOUNT = "create_account", "Create Account"
        RESET_PASSWORD = "reset_password", "Reset Password"

    uuid = models.UUIDField(default=uuid4, editable=False, unique=True)  # This is the public identifier
    token = models.TextField(default=RandomCode, editable=False)  # This is the private token (should be hashed)

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    expiry = models.DateTimeField(default=add_3hrs_from_now)
    service = models.CharField(max_length=14, choices=ServiceTypes.choices)

    def __str__(self):
        return self.user.username

    def is_expired(self):
        if timezone.now() > self.expiry:
            self.delete()
            return True
        return False

    def hash_token(self):
        self.token = make_password(self.token)
        self.save()
        return True

    class Meta:
        verbose_name = "Verification Code"
        verbose_name_plural = "Verification Codes"


class UserSettings(models.Model):
    class CoreFeatures(models.TextChoices):
        INVOICES = "invoices", "Invoices"
        RECEIPTS = "receipts", "Receipts"
        EMAIL_SENDING = "email_sending", "Email Sending"

    CURRENCIES = {
        "GBP": {"name": "British Pound Sterling", "symbol": "£"},
        "EUR": {"name": "Euro", "symbol": "€"},
        "USD": {"name": "United States Dollar", "symbol": "$"},
        "JPY": {"name": "Japanese Yen", "symbol": "¥"},
        "INR": {"name": "Indian Rupee", "symbol": "₹"},
        "AUD": {"name": "Australian Dollar", "symbol": "$"},
        "CAD": {"name": "Canadian Dollar", "symbol": "$"},
    }
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="user_profile")
    dark_mode = models.BooleanField(default=True)
    currency = models.CharField(
        max_length=3,
        default="GBP",
        choices=[(code, info["name"]) for code, info in CURRENCIES.items()],
    )
    profile_picture = models.ImageField(
        upload_to="profile_pictures/",
        storage=_public_storage,
        blank=True,
        null=True,
    )

    disabled_features = models.JSONField(default=list)

    @property
    def profile_picture_url(self):
        if self.profile_picture and hasattr(self.profile_picture, "url"):
            return self.profile_picture.url
        return ""

    def get_currency_symbol(self):
        return self.CURRENCIES.get(self.currency, {}).get("symbol", "$")

    def has_feature(self, feature: str) -> bool:
        return feature not in self.disabled_features

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name = "User Settings"
        verbose_name_plural = "User Settings"


class Organization(models.Model):
    name = models.CharField(max_length=100, unique=True)
    leader = models.ForeignKey(User, on_delete=models.CASCADE, related_name="teams_leader_of")
    members = models.ManyToManyField(User, related_name="teams_joined")

    stripe_customer_id = models.CharField(max_length=255, null=True, blank=True)
    entitlements = models.JSONField(null=True, blank=True, default=list)  # list of strings e.g. ["invoices"]

    def is_owner(self, user: User) -> bool:
        return self.leader == user

    def is_logged_in_as_team(self, request) -> bool:
        if isinstance(request.auth, User):
            return False

        if request.auth and request.auth.team_id == self.id:
            return True
        return False

    def is_authenticated(self):
        return True


class TeamMemberPermission(models.Model):
    team = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="permissions")
    user = models.OneToOneField("backend.User", on_delete=models.CASCADE, related_name="team_permissions")
    scopes = models.JSONField("Scopes", default=list, help_text="List of permitted scopes")

    class Meta:
        unique_together = ("team", "user")


class TeamInvitation(models.Model):
    code = models.CharField(max_length=10)
    team = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="team_invitations")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="team_invitations")
    invited_by = models.ForeignKey(User, on_delete=models.CASCADE)
    expires = models.DateTimeField(null=True, blank=True)
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
        self.set_expires()
        self.code = RandomCode(10)
        super().save()

    def __str__(self):
        return self.team.name

    class Meta:
        verbose_name = "Team Invitation"
        verbose_name_plural = "Team Invitations"


class OwnerBaseManager(models.Manager):
    def create(self, **kwargs):
        # Handle the 'owner' argument dynamically in `create()`
        owner = kwargs.pop("owner", None)
        if isinstance(owner, User):
            kwargs["user"] = owner
            kwargs["organization"] = None
        elif isinstance(owner, Organization):
            kwargs["organization"] = owner
            kwargs["user"] = None
        return super().create(**kwargs)

    def filter(self, *args, **kwargs):
        # Handle the 'owner' argument dynamically in `filter()`
        owner = kwargs.pop("owner", None)
        if isinstance(owner, User):
            kwargs["user"] = owner
        elif isinstance(owner, Organization):
            kwargs["organization"] = owner
        return super().filter(*args, **kwargs)


class OwnerBase(models.Model):
    user = models.ForeignKey("backend.User", on_delete=models.CASCADE, null=True, blank=True)
    organization = models.ForeignKey("backend.Organization", on_delete=models.CASCADE, null=True, blank=True)

    objects = OwnerBaseManager()

    class Meta:
        abstract = True
        constraints = [
            USER_OR_ORGANIZATION_CONSTRAINT(),
        ]

    @property
    def owner(self) -> User | Organization:
        """
        Property to dynamically get the owner (either User or Team)
        """
        if hasattr(self, "user") and self.user:
            return self.user
        elif hasattr(self, "team") and self.team:
            return self.team
        return self.organization  # type: ignore[return-value]
        # all responses WILL have either a user or org so this will handle all

    @owner.setter
    def owner(self, value: User | Organization) -> None:
        if isinstance(value, User):
            self.user = value
            self.organization = None
        elif isinstance(value, Organization):
            self.user = None
            self.organization = value
        else:
            raise ValueError("Owner must be either a User or a Organization")

    def save(self, *args, **kwargs):
        if hasattr(self, "owner") and not self.user and not self.organization:
            if isinstance(self.owner, User):
                self.user = self.owner
            elif isinstance(self.owner, Organization):
                self.organization = self.owner
        super().save(*args, **kwargs)

    @classmethod
    def filter_by_owner(cls: typing.Type[M], owner: Union[User, Organization]) -> QuerySet[M]:
        """
        Class method to filter objects by owner (either User or Organization)
        """
        if isinstance(owner, User):
            return cls.objects.filter(user=owner)  # type: ignore[attr-defined]
        elif isinstance(owner, Organization):
            return cls.objects.filter(organization=owner)  # type: ignore[attr-defined]
        else:
            raise ValueError("Owner must be either a User or an Organization")


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


class Client(OwnerBase):
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

    def has_access(self, user: User) -> bool:
        if not user.is_authenticated:
            return False

        if user.logged_in_as_team:
            return self.organization == user.logged_in_as_team
        else:
            return self.user == user

class BankDetail(models.Model):
    account_holder_name = models.CharField(max_length=100)
    account_number = models.CharField(max_length=16)
    sort_code = models.CharField(max_length=9)

    def __str__(self):
        return f"{self.account_holder_name} - {self.account_number}"

class DefaultValues(OwnerBase):
    class InvoiceDueDateType(models.TextChoices):
        days_after = "days_after"  # days after issue
        date_following = "date_following"  # date of following month
        date_current = "date_current"  # date of current month

    class InvoiceDateType(models.TextChoices):
        day_of_month = "day_of_month"
        days_after = "days_after"

    client = models.OneToOneField(Client, on_delete=models.CASCADE, related_name="default_values", null=True, blank=True)

    bank_details = models.ManyToManyField(BankDetail, blank=True, related_name='default_values')

    currency = models.CharField(
        max_length=3,
        default="GBP",
        choices=[(code, info["name"]) for code, info in UserSettings.CURRENCIES.items()],
    )

    invoice_due_date_value = models.PositiveSmallIntegerField(default=7, null=False, blank=False)
    invoice_due_date_type = models.CharField(max_length=20, choices=InvoiceDueDateType.choices, default=InvoiceDueDateType.days_after)

    invoice_date_value = models.PositiveSmallIntegerField(default=15, null=False, blank=False)
    invoice_date_type = models.CharField(max_length=20, choices=InvoiceDateType.choices, default=InvoiceDateType.day_of_month)

    invoice_from_name = models.CharField(max_length=100, null=True, blank=True)
    invoice_from_company = models.CharField(max_length=100, null=True, blank=True)
    invoice_from_address = models.CharField(max_length=100, null=True, blank=True)
    invoice_from_city = models.CharField(max_length=100, null=True, blank=True)
    invoice_from_county = models.CharField(max_length=100, null=True, blank=True)
    invoice_from_country = models.CharField(max_length=100, null=True, blank=True)

    invoice_account_number = models.CharField(max_length=100, null=True, blank=True)
    invoice_sort_code = models.CharField(max_length=100, null=True, blank=True)
    invoice_account_holder_name = models.CharField(max_length=100, null=True, blank=True)

    def get_issue_and_due_dates(self, issue_date: date | str | None = None) -> tuple[str, str]:
        due: date
        issue: date

        if isinstance(issue_date, str):
            issue = date.fromisoformat(issue_date) or date.today()
        else:
            issue = issue_date or date.today()

        match self.invoice_due_date_type:
            case self.InvoiceDueDateType.days_after:
                due = issue + timedelta(days=self.invoice_due_date_value)
            case self.InvoiceDueDateType.date_following:
                due = date(issue.year, issue.month + 1, self.invoice_due_date_value)
            case self.InvoiceDueDateType.date_current:
                due = date(issue.year, issue.month, self.invoice_due_date_value)
            case _:
                raise ValueError("Invalid invoice due date type")
        return date.isoformat(issue), date.isoformat(due)

    default_invoice_logo = models.ImageField(
        upload_to="invoice_logos/",
        storage=_private_storage,
        blank=True,
        null=True,
    )


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
    reference = models.CharField(max_length=100, blank=True, null=True)
    invoice_number = models.CharField(max_length=100, blank=True, null=True)
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
        ("pending", "Pending"),
        ("paid", "Paid"),
        ("overdue", "Overdue"),
    )

    invoice_id = models.IntegerField(unique=True, blank=True, null=True)  # todo: add
    date_due = models.DateField()
    payment_status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")
    invoice_recurring_profile = models.ForeignKey(
        "InvoiceRecurringProfile", related_name="generated_invoices", on_delete=models.SET_NULL, blank=True, null=True
    )

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
    def get_to_details(self) -> tuple[str, dict[str, str | None]] | tuple[str, Client]:
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

    def next_invoice_due_date(self, account_defaults: "DefaultValues", from_date: date = datetime.now().date()) -> date:
        match account_defaults.invoice_due_date_type:
            case account_defaults.InvoiceDueDateType.days_after:
                return from_date + timedelta(days=account_defaults.invoice_due_date_value)
            case account_defaults.InvoiceDueDateType.date_following:
                return datetime(from_date.year, from_date.month + 1, account_defaults.invoice_due_date_value)
            case account_defaults.InvoiceDueDateType.date_current:
                return datetime(from_date.year, from_date.month, account_defaults.invoice_due_date_value)
            case _:
                return from_date + timedelta(days=7)


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


class APIKey(models.Model):
    class ServiceTypes(models.TextChoices):
        AWS_API_DESTINATION = "aws_api_destination"

    service = models.CharField(max_length=20, choices=ServiceTypes.choices, null=True)
    key = models.CharField(max_length=100, default=RandomAPICode)
    last_used = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "API Key"
        verbose_name_plural = "API Keys"

    def __str__(self):
        return self.service

    def verify(self, key):
        return check_password(key, self.key)

    def hash(self):
        self.key = make_password(f"{self.id}:{self.key}")
        self.save()


class PasswordSecret(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="password_secrets")
    secret = models.TextField(max_length=300)
    expires = models.DateTimeField(null=True, blank=True)


class Notification(models.Model):
    action_choices = [
        ("normal", "Normal"),
        ("modal", "Modal"),
        ("redirect", "Redirect"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_notifications")
    message = models.CharField(max_length=100)
    action = models.CharField(max_length=10, choices=action_choices, default="normal")
    action_value = models.CharField(max_length=100, null=True, blank=True)
    extra_type = models.CharField(max_length=100, null=True, blank=True)
    extra_value = models.CharField(max_length=100, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)


class AuditLog(OwnerBase):
    action = models.CharField(max_length=100)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints: list = []

    def __str__(self):
        return f"{self.action} - {self.date}"


class LoginLog(models.Model):
    class ServiceTypes(models.TextChoices):
        MANUAL = "manual"
        MAGIC_LINK = "magic_link"

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    service = models.CharField(max_length=14, choices=ServiceTypes.choices, default="manual")
    date = models.DateTimeField(auto_now_add=True)


class Error(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    error = models.CharField(max_length=250, null=True)
    error_code = models.CharField(max_length=100, null=True)
    error_colour = models.CharField(max_length=25, default="danger")
    date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.user_id)


class TracebackError(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    error = models.CharField(max_length=5000, null=True)
    date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.error)


class FeatureFlags(models.Model):
    name = models.CharField(max_length=100, editable=False, unique=True)
    description = models.TextField(max_length=500, null=True, blank=True, editable=False)
    value = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Feature Flag"
        verbose_name_plural = "Feature Flags"

    def __str__(self):
        return self.name

    def enable(self):
        self.value = True
        self.save()

    def disable(self):
        self.value = False
        self.save()


class QuotaLimit(models.Model):
    class LimitTypes(models.TextChoices):
        PER_MONTH = "per_month"
        PER_DAY = "per_day"
        PER_CLIENT = "per_client"
        PER_INVOICE = "per_invoice"
        PER_TEAM = "per_team"
        PER_QUOTA = "per_quota"
        FOREVER = "forever"

    slug = models.CharField(max_length=100, unique=True, editable=False)
    name = models.CharField(max_length=100, editable=False)
    description = models.TextField(max_length=500, null=True, blank=True)
    value = models.IntegerField()
    updated_at = models.DateTimeField(auto_now=True)
    adjustable = models.BooleanField(default=True)
    limit_type = models.CharField(max_length=20, choices=LimitTypes.choices, default=LimitTypes.PER_MONTH)

    class Meta:
        verbose_name = "Quota Limit"
        verbose_name_plural = "Quota Limits"

    def __str__(self):
        return self.name

    def get_quota_limit(self, user: User, quota_limit: QuotaLimit | None = None):
        user_quota_override: QuotaOverrides | QuotaLimit
        try:
            if quota_limit:
                user_quota_override = quota_limit
            else:
                user_quota_override = self.quota_overrides.get(user=user)
            return user_quota_override.value
        except QuotaOverrides.DoesNotExist:
            return self.value

    def get_period_usage(self, user: User):
        if self.limit_type == "forever":
            return self.quota_usage.filter(user=user, quota_limit=self).count()
        elif self.limit_type == "per_month":
            return self.quota_usage.filter(user=user, quota_limit=self, created_at__month=datetime.now().month).count()
        elif self.limit_type == "per_day":
            return self.quota_usage.filter(user=user, quota_limit=self, created_at__day=datetime.now().day).count()
        else:
            return "Not available"

    def strict_goes_above_limit(self, user: User, extra: str | int | None = None, add: int = 0) -> bool:
        current: Union[int, None, QuerySet[QuotaUsage], Literal["Not Available"]]

        current = self.strict_get_quotas(user, extra)
        current = current.count() if current != "Not Available" else None
        return current + add >= self.get_quota_limit(user) if current else False

    def strict_get_quotas(
        self, user: User, extra: str | int | None = None, quota_limit: QuotaLimit | None = None
    ) -> QuerySet[QuotaUsage] | Literal["Not Available"]:
        """
        Gets all usages of a quota
        :return: QuerySet of quota usages OR "Not Available" if utilisation isn't available (e.g. per invoice you can't get in total)
        """
        current = None
        if quota_limit is not None:
            quota_lim = quota_limit.quota_usage
        else:
            quota_lim = QuotaUsage.objects.filter(user=user, quota_limit=self)  # type: ignore[assignment]

        if self.limit_type == "forever":
            current = self.quota_usage.filter(user=user, quota_limit=self)
        elif self.limit_type == "per_month":
            current_month = timezone.now().month
            current_year = timezone.now().year
            current = quota_lim.filter(created_at__year=current_year, created_at__month=current_month)
        elif self.limit_type == "per_day":
            current_day = timezone.now().day
            current_month = timezone.now().month
            current_year = timezone.now().year
            current = quota_lim.filter(created_at__year=current_year, created_at__month=current_month, created_at__day=current_day)
        elif self.limit_type in ["per_client", "per_invoice", "per_team", "per_receipt", "per_quota"] and extra:
            current = quota_lim.filter(extra_data=extra)
        else:
            return "Not Available"
        return current

    @classmethod
    @typing.no_type_check
    def delete_quota_usage(cls, quota_limit: str | QuotaLimit, user: User, extra, timestamp=None):
        quota_limit = cls.objects.get(slug=quota_limit) if isinstance(quota_limit, str) else quota_limit

        all_usages = quota_limit.strict_get_quotas(user, extra)
        closest_obj = None

        if all_usages.count() > 1 and timestamp:
            earliest: QuotaUsage | None = all_usages.filter(created_at__gte=timestamp).order_by("created_at").first()
            latest: QuotaUsage | None = all_usages.filter(created_at__lte=timestamp).order_by("created_at").last()

            if earliest and latest:
                time_until_soonest_obj = abs(earliest.created_at - timestamp)
                time_since_most_recent_obj = abs(latest.created_at - timestamp)
                if time_until_soonest_obj < time_since_most_recent_obj:
                    closest_obj = earliest
                else:
                    closest_obj = latest

            if earliest and latest and closest_obj:
                closest_obj.delete()
        elif all_usages.count() > 1:
            earliest = all_usages.order_by("created_at").first()
            if earliest:
                earliest.delete()
        else:
            first = all_usages.first()
            if first:
                first.delete()


class QuotaOverrides(OwnerBase):
    quota_limit = models.ForeignKey(QuotaLimit, on_delete=models.CASCADE, related_name="quota_overrides")
    value = models.IntegerField()
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Quota Override"
        verbose_name_plural = "Quota Overrides"

    def __str__(self):
        return f"{self.user}"


class QuotaUsage(OwnerBase):
    quota_limit = models.ForeignKey(QuotaLimit, on_delete=models.CASCADE, related_name="quota_usage")
    created_at = models.DateTimeField(auto_now_add=True)
    extra_data = models.IntegerField(null=True, blank=True)  # id of Limit Type

    class Meta:
        verbose_name = "Quota Usage"
        verbose_name_plural = "Quota Usage"

    def __str__(self):
        return f"{self.user} quota usage for {self.quota_limit_id}"

    @classmethod
    def create_str(cls, user: User, limit: str | QuotaLimit, extra_data: str | int | None = None):
        try:
            quota_limit = limit if isinstance(limit, QuotaLimit) else QuotaLimit.objects.get(slug=limit)
        except QuotaLimit.DoesNotExist:
            return "Not Found"

        Notification.objects.create(
            user=user,
            action="redirect",
            action_value=f"/dashboard/quotas/{quota_limit.slug.split('-')[0]}/",
            message=f"You have reached the limit for {quota_limit.name}",
        )

        return cls.objects.create(user=user, quota_limit=quota_limit, extra_data=extra_data)

    @classmethod
    def get_usage(self, user: User, limit: str | QuotaLimit):
        try:
            ql: QuotaLimit = QuotaLimit.objects.get(slug=limit) if isinstance(limit, str) else limit
        except QuotaLimit.DoesNotExist:
            return "Not Found"

        return self.objects.filter(user=user, quota_limit=ql).count()


class QuotaIncreaseRequest(OwnerBase):
    class StatusTypes(models.TextChoices):
        PENDING = "pending"
        APPROVED = "approved"
        REJECTED = "rejected"

    requester = models.ForeignKey(User, on_delete=models.CASCADE, related_name="quota_increase_requests")

    quota_limit = models.ForeignKey(QuotaLimit, on_delete=models.CASCADE, related_name="quota_increase_requests")
    reason = models.CharField(max_length=1000)
    new_value = models.IntegerField()
    current_value = models.IntegerField()
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=StatusTypes.choices, default=StatusTypes.PENDING)

    class Meta:
        verbose_name = "Quota Increase Request"
        verbose_name_plural = "Quota Increase Requests"

    def __str__(self):
        return f"{self.owner}"


class EmailSendStatus(OwnerBase):
    STATUS_CHOICES = [
        (status, status.title())
        for status in [
            "send",
            "reject",
            "bounce",
            "complaint",
            "delivery",
            "open",
            "click",
            "rendering_failure",
            "delivery_delay",
            "subscription",
            "failed_to_send",
            "pending",
        ]
    ]

    sent_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="emails_sent")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_status_at = models.DateTimeField(auto_now_add=True)

    recipient = models.TextField()
    aws_message_id = models.CharField(max_length=100, null=True, blank=True, editable=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)

    class Meta:
        constraints = [USER_OR_ORGANIZATION_CONSTRAINT()]


class FileStorageFile(OwnerBase):
    file = models.FileField(upload_to=upload_to_user_separate_folder, storage=_private_storage)
    file_uri_path = models.CharField(max_length=500)  # relative path not including user folder/media
    last_edited_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, editable=False, related_name="files_edited")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    __original_file = None
    __original_file_uri_path = None

    def __init__(self, *args, **kwargs):
        super(FileStorageFile, self).__init__(*args, **kwargs)
        self.__original_file = self.file
        self.__original_file_uri_path = self.file_uri_path


class MultiFileUpload(OwnerBase):
    files = models.ManyToManyField(FileStorageFile, related_name="multi_file_uploads")
    started_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    finished_at = models.DateTimeField(null=True, blank=True, editable=False)
    uuid = models.UUIDField(default=uuid4, editable=False, unique=True)

    def is_finished(self):
        return self.finished_at is not None
