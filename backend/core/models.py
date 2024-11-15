from __future__ import annotations

import itertools
import typing
from datetime import datetime, timedelta
from typing import Literal, Union
from uuid import uuid4

from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AbstractUser, UserManager
from django.core.files.storage import storages, FileSystemStorage
from django.db import models
from django.db.models import Count, QuerySet
from django.utils import timezone
from django.utils.crypto import get_random_string
from storages.backends.s3 import S3Storage


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

    @property
    def name(self):
        return self.first_name

    @property
    def teams_apart_of(self):
        return set(itertools.chain(self.teams_joined.all(), self.teams_leader_of.all()))

    @property
    def is_org(self):
        return False


def add_3hrs_from_now():
    return timezone.now() + timezone.timedelta(hours=3)


class ActiveManager(models.Manager):
    """Manager to return only active objects."""

    def get_queryset(self):
        return super().get_queryset().filter(active=True)


class ExpiredManager(models.Manager):
    """Manager to return only expired (inactive) objects."""

    def get_queryset(self):
        now = timezone.now()
        return super().get_queryset().filter(expires__isnull=False, expires__lte=now)


class ExpiresBase(models.Model):
    """Base model for handling expiration logic."""

    expires = models.DateTimeField("Expires", null=True, blank=True, help_text="When the item will expire")
    active = models.BooleanField(default=True)

    # Default manager that returns only active items
    objects = ActiveManager()

    # Custom manager to get expired/inactive objects
    expired_objects = ExpiredManager()

    # Fallback All objects
    all_objects = models.Manager()

    def deactivate(self) -> None:
        """Manually deactivate the object."""
        self.active = False
        self.save()

    def delete_if_expired_for(self, days: int = 14) -> bool:
        """Delete the object if it has been expired for a certain number of days."""
        if self.expires and self.expires <= timezone.now() - timedelta(days=days):
            self.delete()
            return True
        return False

    @property
    def remaining_active_time(self):
        """Return the remaining time until expiration, or None if already expired or no expiration set."""
        if not self.has_expired:
            return self.expires - timezone.now()
        return None

    @property
    def has_expired(self):
        return self.expires and self.expires <= timezone.now()

    def is_active(self):
        return self.active

    class Meta:
        abstract = True


class VerificationCodes(ExpiresBase):
    class ServiceTypes(models.TextChoices):
        CREATE_ACCOUNT = "create_account", "Create Account"
        RESET_PASSWORD = "reset_password", "Reset Password"

    uuid = models.UUIDField(default=uuid4, editable=False, unique=True)  # This is the public identifier
    token = models.TextField(default=RandomCode, editable=False)  # This is the private token (should be hashed)

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    service = models.CharField(max_length=14, choices=ServiceTypes.choices)

    def __str__(self):
        return self.user.username

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
        MONTHLY_REPORTS = "monthly_reports", "Monthly Reports"

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

        if request.auth and request.auth.organization_id == self.id:
            return True
        return False

    @property
    def is_authenticated(self):
        return True

    @property
    def is_org(self):
        return True


class TeamMemberPermission(models.Model):
    team = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="permissions")
    user = models.OneToOneField("backend.User", on_delete=models.CASCADE, related_name="team_permissions")
    scopes = models.JSONField("Scopes", default=list, help_text="List of permitted scopes")

    class Meta:
        unique_together = ("team", "user")


class TeamInvitation(ExpiresBase):
    code = models.CharField(max_length=10)
    team = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="team_invitations")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="team_invitations")
    invited_by = models.ForeignKey(User, on_delete=models.CASCADE)

    def is_active(self):
        return self.active

    def set_expires(self):
        self.expires = timezone.now() + timezone.timedelta(days=14)

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = RandomCode(10)
            self.set_expires()
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

    @property
    def is_team(self):
        return isinstance(self.owner, Organization)


class PasswordSecret(ExpiresBase):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="password_secrets")
    secret = models.TextField(max_length=300)


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
    action = models.CharField(max_length=300)
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
