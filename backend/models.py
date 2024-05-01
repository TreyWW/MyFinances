from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Literal, NoReturn, Optional
from uuid import uuid4

from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.models import AbstractUser, AnonymousUser, UserManager
from django.core.validators import MaxValueValidator
from django.db import models
from django.db.models import Count, QuerySet
from django.utils import timezone
from django.utils.crypto import get_random_string
from shortuuid.django_fields import ShortUUIDField

from settings import settings
from settings.settings import AWS_TAGS_APP_NAME


def generate_random_token(length=6):
    return get_random_string(length=length).upper()


def generate_random_api_key(length=89):
    return get_random_string(length=length).lower()


def user_or_organization_constraint():
    return models.CheckConstraint(
        name=f"%(app_label)s_%(class)s_check_user_or_organization",
        check=(models.Q(user__isnull=True, organization__isnull=False) | models.Q(user__isnull=False, organization__isnull=True)),
    )


class CustomUserManager(UserManager):
    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .select_related("user_profile", "logged_in_as_team")
            .annotate(notification_count=Count("user_notifications"))
        )


class User(AbstractUser):
    objects = CustomUserManager()  # type: ignore

    logged_in_as_team = models.ForeignKey("Team", on_delete=models.SET_NULL, null=True, blank=True)
    awaiting_email_verification = models.BooleanField(default=True)

    class Role(models.TextChoices):
        #        NAME     DJANGO ADMIN NAME
        DEV = "DEV", "Developer"
        STAFF = "STAFF", "Staff"
        USER = "USER", "User"
        TESTER = "TESTER", "Tester"

    role = models.CharField(max_length=10, choices=Role.choices, default=Role.USER)


class CustomUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Replace request.user with CustomUser instance if authenticated
        if request.user.is_authenticated:
            request.user = User.objects.get(pk=request.user.pk)
        else:
            # If user is not authenticated, set request.user to AnonymousUser
            request.user = AnonymousUser()
        return self.get_response(request)


def add_3hrs_from_now():
    return timezone.now() + timezone.timedelta(hours=3)


class VerificationCodes(models.Model):
    class ServiceTypes(models.TextChoices):
        CREATE_ACCOUNT = "create_account", "Create Account"
        RESET_PASSWORD = "reset_password", "Reset Password"

    uuid = models.UUIDField(default=uuid4, editable=False, unique=True)  # This is the public identifier
    token = models.TextField(default=generate_random_token, editable=False)  # This is the private token (should be hashed)
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
        storage=settings.CustomPublicMediaStorage(),
        blank=True,
        null=True,
    )

    def profile_picture_url(self):
        if self.profile_picture and hasattr(self.profile_picture, "url"):
            return self.profile_picture.url
        return ""

    def get_currency_symbol(self):
        return self.CURRENCIES.get(self.currency, {}).get("symbol", "$")

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name = "User Settings"
        verbose_name_plural = "User Settings"


class Team(models.Model):
    name = models.CharField(max_length=100, unique=True)
    leader = models.ForeignKey(User, on_delete=models.CASCADE, related_name="teams_leader_of")
    members = models.ManyToManyField(User, related_name="teams_joined")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Team"
        verbose_name_plural = "Teams"


class TeamInvitation(models.Model):
    code = models.CharField(max_length=10)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="team_invitations")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="team_invitations")
    invited_by = models.ForeignKey(User, on_delete=models.CASCADE)
    expires = models.DateTimeField(null=True, blank=True)
    active = models.BooleanField(default=True)

    def is_active(self):
        if not self.active:
            return False
        if self.expires and timezone.now() > self.expires:
            self.active = False
            self.save()
            return False
        return True

    def set_expires(self):
        self.expires = timezone.now() + timezone.timedelta(days=7)

    def save(self, *args, **kwargs):
        if not self.expires:
            self.set_expires()
        if not self.code:
            self.code = generate_random_token(10)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.team.name

    class Meta:
        verbose_name = "Team Invitation"
        verbose_name_plural = "Team Invitations"


class Receipt(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    organization = models.ForeignKey(Team, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to="receipts", storage=settings.CustomPrivateMediaStorage())
    total_price = models.FloatField(null=True, blank=True)
    date = models.DateField(null=True, blank=True)
    date_uploaded = models.DateTimeField(auto_now_add=True)
    receipt_parsed = models.JSONField(null=True, blank=True)
    merchant_store = models.CharField(max_length=255, blank=True, null=True)
    purchase_category = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        constraints = [user_or_organization_constraint()]

    def __str__(self):
        return f"{self.name} - {self.date} ({self.total_price})"

    def has_access(self, user: User) -> bool:
        if not user.is_authenticated:
            return False
        return self.organization == user.logged_in_as_team if user.logged_in_as_team else self.user == user


class ReceiptDownloadToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.ForeignKey(Receipt, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid4, editable=False, unique=True)

    class Meta:
        verbose_name = "Receipt Download Token"
        verbose_name_plural = "Receipt Download Tokens"


class Client(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    organization = models.ForeignKey(Team, on_delete=models.CASCADE, null=True, blank=True)
    active = models.BooleanField(default=True)

    name = models.CharField(max_length=64)
    phone_number = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    email_verified = models.BooleanField(default=False)
    company = models.CharField(max_length=100, blank=True, null=True)
    is_representative = models.BooleanField(default=False)

    address = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        constraints = [user_or_organization_constraint()]

    def __str__(self):
        return self.name


class InvoiceProduct(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=100)
    quantity = models.IntegerField()
    rate = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)

    def __str__(self):
        return self.name


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
    logo = models.ImageField(upload_to="invoice_logos", storage=settings.CustomPrivateMediaStorage(), blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    payment_status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")
    items = models.ManyToManyField(InvoiceItem, blank=True)
    currency = models.CharField(
        max_length=3, default="GBP", choices=[(code, info["name"]) for code, info in UserSettings.CURRENCIES.items()]
    )

    date_created = models.DateTimeField(auto_now_add=True)
    date_due = models.DateField()
    date_issued = models.DateField(blank=True, null=True)

    discount_amount = models.DecimalField(max_digits=15, default=0, decimal_places=2)
    discount_percentage = models.DecimalField(default=0, max_digits=5, decimal_places=2, validators=[MaxValueValidator(100)])

    class Meta:
        constraints = [user_or_organization_constraint()]

    def __str__(self):
        invoice_id = self.invoice_id or self.id
        client = self.client_name if self.client_name else (self.client_to.name if self.client_to else "Unknown Client")
        return f"Invoice #{invoice_id} for {client}"

    @property
    def dynamic_payment_status(self):
        if self.date_due and timezone.now().date() > self.date_due and self.payment_status == "pending":
            return "overdue"
        return self.payment_status

    @property
    def get_to_details(self):
        if self.client_to:
            return "client", self.client_to
        return "manual", {"name": self.client_name, "company": self.client_company}

    def get_subtotal(self):
        return Decimal(sum(item.get_total_price() for item in self.items.all()))

    def get_tax(self, amount=None):
        if not amount:
            amount = self.get_subtotal()
        return amount * Decimal("0.20") if self.vat_number else Decimal("0")

    def get_percentage_amount(self, subtotal=None):
        if not subtotal:
            subtotal = self.get_subtotal()
        if self.discount_percentage > 0:
            return subtotal * Decimal(self.discount_percentage / 100)
        return Decimal("0")

    def get_total_price(self):
        subtotal = self.get_subtotal()
        total = subtotal - self.get_percentage_amount(subtotal) - self.discount_amount
        total += self.get_tax(total) if total > 0 else Decimal("0")
        return max(total, Decimal("0"))

    def has_access(self, user: User):
        if not user.is_authenticated:
            return False
        return self.organization == user.logged_in_as_team if user.logged_in_as_team else self.user == user

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
        if self.expires and timezone.now() > self.expires:
            self.active = False
            self.save()
            return False
        return True

    def set_expires(self):
        if not self.never_expire:
            self.expires = timezone.now() + timezone.timedelta(days=7)
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


class InvoiceOnetimeSchedule(InvoiceSchedule):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name="onetime_invoice_schedules")
    due = models.DateTimeField()

    class Meta:
        verbose_name = "One-Time Invoice Schedule"
        verbose_name_plural = "One-Time Invoice Schedules"


class InvoiceReminder(InvoiceSchedule):
    class ReminderTypes(models.TextChoices):
        BEFORE_DUE = "before_due", "Before Due"
        AFTER_DUE = "after_due", "After Due"
        ON_OVERDUE = "on_overdue", "On Overdue"

    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name="invoice_reminders")
    days = models.PositiveIntegerField(blank=True, null=True)
    reminder_type = models.CharField(max_length=100, choices=ReminderTypes.choices, default=ReminderTypes.BEFORE_DUE)

    def __str__(self):
        days_str = f"{self.days}d" if self.days else "Unknown days"
        return f"Reminder for Invoice #{self.invoice.id} - {days_str} {self.reminder_type}"

    class Meta:
        verbose_name = "Invoice Reminder"
        verbose_name_plural = "Invoice Reminders"


class APIKey(models.Model):
    class ServiceTypes(models.TextChoices):
        AWS_API_DESTINATION = "aws_api_destination", "AWS API Destination"

    service = models.CharField(max_length=20, choices=ServiceTypes.choices, null=True)
    key = models.CharField(max_length=100, default=generate_random_api_key)
    last_used = models.DateTimeField(auto_now_add=True)

    def verify(self, key):
        return check_password(key, self.key)

    def hash(self):
        self.key = make_password(f"{self.id}:{self.key}")
        self.save()

    def __str__(self):
        return f"{self.service} API Key Last Used: {self.last_used}"

    class Meta:
        verbose_name = "API Key"
        verbose_name_plural = "API Keys"


class PasswordSecret(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="password_secrets")
    secret = models.TextField(max_length=300)
    expires = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Password Secret for {self.user.username}"


class Notification(models.Model):
    ACTION_CHOICES = [
        ("normal", "Normal"),
        ("modal", "Modal"),
        ("redirect", "Redirect"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_notifications")
    message = models.CharField(max_length=100)
    action = models.CharField(max_length=10, choices=ACTION_CHOICES, default="normal")
    action_value = models.CharField(max_length=100, null=True, blank=True)
    extra_type = models.CharField(max_length=100, null=True, blank=True)
    extra_value = models.CharField(max_length=100, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.user.username}: {self.message}"


class AuditLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    organization = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=100)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        user_or_org = self.user.username if self.user else "General"
        return f"Audit Log {user_or_org}: {self.action} on {self.date}"


class LoginLog(models.Model):
    class ServiceTypes(models.TextChoices):
        MANUAL = "manual", "Manual"
        MAGIC_LINK = "magic_link", "Magic Link"

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    service = models.CharField(max_length=14, choices=ServiceTypes.choices, default=ServiceTypes.MANUAL)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} logged in via {self.service} on {self.date}"


class Error(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    error = models.CharField(max_length=250, null=True)
    error_code = models.CharField(max_length=100, null=True)
    error_colour = models.CharField(max_length=25, default="danger")
    date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Error {self.error_code}: {self.error}"


class TracebackError(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    error = models.CharField(max_length=5000, null=True)
    date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Traceback for {self.user.username if self.user else 'Unknown User'}: {self.error}"


class FeatureFlags(models.Model):
    name = models.CharField(max_length=100, editable=False, unique=True)
    description = models.TextField(max_length=500, null=True, blank=True, editable=False)
    value = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

    def enable(self):
        self.value = True
        self.save()

    def disable(self):
        self.value = False
        self.save()

    def __str__(self):
        return f"Feature Flag '{self.name}': {'Enabled' if self.value else 'Disabled'}"

    class Meta:
        verbose_name = "Feature Flag"
        verbose_name_plural = "Feature Flags"


class QuotaLimit(models.Model):
    class LimitTypes(models.TextChoices):
        PER_MONTH = "per_month", "Per Month"
        PER_DAY = "per_day", "Per Day"
        PER_CLIENT = "per_client", "Per Client"
        PER_INVOICE = "per_invoice", "Per Invoice"
        PER_TEAM = "per_team", "Per Team"
        PER_QUOTA = "per_quota", "Per Quota"
        FOREVER = "forever", "Forever"

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
        return f"{self.name} Limit ({self.value})"

    def get_quota_limit(self, user: User, quota_limit: QuotaLimit | None = None):
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
        quota_limit = quota_limit.quota_usage if quota_limit else QuotaUsage.objects.filter(user=user, quota_limit=self)

        if self.limit_type == "forever":
            current = self.quota_usage.filter(user=user, quota_limit=self)
        elif self.limit_type == "per_month":
            current_month = timezone.now().month
            current_year = timezone.now().year
            current = quota_limit.filter(created_at__year=current_year, created_at__month=current_month)
        elif self.limit_type == "per_day":
            current_day = timezone.now().day
            current_month = timezone.now().month
            current_year = timezone.now().year
            current = quota_limit.filter(created_at__year=current_year, created_at__month=current_month, created_at__day=current_day)
        elif self.limit_type in ["per_client", "per_invoice", "per_team", "per_receipt", "per_quota"] and extra:
            current = quota_limit.filter(extra_data=extra)
        else:
            return "Not Available"
        return current

    @classmethod
    def delete_quota_usage(cls, quota_limit: str | QuotaLimit, user: User, extra, timestamp=None) -> NoReturn:
        quota_limit = cls.objects.get(slug=quota_limit) if isinstance(quota_limit, str) else quota_limit

        all_usages = quota_limit.strict_get_quotas(user, extra)
        closest_obj = None

        if all_usages.count() > 1 and timestamp:
            earliest: QuotaUsage = all_usages.filter(created_at__gte=timestamp).order_by("created_at").first()
            latest: QuotaUsage = all_usages.filter(created_at__lte=timestamp).order_by("created_at").last()

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


class QuotaOverrides(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quota_limit = models.ForeignKey(QuotaLimit, on_delete=models.CASCADE, related_name="quota_overrides")
    value = models.IntegerField()
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Quota Override"
        verbose_name_plural = "Quota Overrides"

    def __str__(self):
        return f"{self.user.username}'s Override for {self.quota_limit.name} to {self.value}"


class QuotaUsage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
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


class QuotaIncreaseRequest(models.Model):
    class StatusTypes(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quota_limit = models.ForeignKey(QuotaLimit, on_delete=models.CASCADE, related_name="quota_increase_requests")
    reason = models.CharField(max_length=1000)
    new_value = models.IntegerField()
    current_value = models.IntegerField()
    status = models.CharField(max_length=20, choices=StatusTypes.choices, default=StatusTypes.PENDING)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Quota Increase Request"
        verbose_name_plural = "Quota Increase Requests"

    def __str__(self):
        return f"Request #{self.id} by {self.user.username} for {self.quota_limit.name} increase"


class EmailSendStatus(models.Model):
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

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name="emails_created", blank=True)
    organization = models.ForeignKey(Team, on_delete=models.CASCADE, null=True, related_name="emails_created", blank=True)
    sent_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="emails_sent")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_status_at = models.DateTimeField(auto_now_add=True)
    recipient = models.TextField()
    aws_message_id = models.CharField(max_length=100, null=True, blank=True, editable=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)

    class Meta:
        constraints = [user_or_organization_constraint()]

    def __str__(self):
        return f"Email Status for {self.recipient}: {self.status} sent by {self.sent_by.username if self.sent_by else 'System'}"
