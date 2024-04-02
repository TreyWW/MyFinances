from datetime import datetime
from typing import Optional, NoReturn, Union, Literal
from uuid import uuid4

from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.models import UserManager, AbstractUser, AnonymousUser
from django.db import models
from django.db.models import Count, QuerySet
from django.utils import timezone

from backend.models_db.utils import RandomCode, RandomAPICode, add_3hrs_from_now
from settings import settings


class CustomUserManager(UserManager):
    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .select_related("user_profile", "logged_in_as_team")
            .annotate(notification_count=((Count("user_notifications"))))
        )


class User(AbstractUser):
    objects = CustomUserManager()

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

        response = self.get_response(request)
        return response


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

    @property
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


class FeatureFlags(models.Model):
    name = models.CharField(max_length=100)
    value = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Feature Flag"
        verbose_name_plural = "Feature Flags"

    def __str__(self):
        return self.name


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

    def get_quota_limit(self, user: User, quota_limit: Optional["QuotaLimit"] = None):
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

    def strict_goes_above_limit(self, user: User, extra: Optional[str | int] = None) -> bool:
        current = self.strict_get_quotas(user, extra)
        current = current.count() if current != "Not Available" else None
        return current >= self.get_quota_limit(user) if current else False

    def strict_get_quotas(
        self, user: User, extra: Optional[str | int] = None, quota_limit: Optional["QuotaLimit"] = None
    ) -> Union['QuerySet["QuotaUsage"]', Literal["Not Available"]]:
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
    def delete_quota_usage(cls, quota_limit: Union[str, "QuotaLimit"], user: User, extra, timestamp=None) -> NoReturn:
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
        return f"{self.user}"


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
    def create_str(cls, user: User, limit: str | QuotaLimit, extra_data: Optional[str | int] = None):
        try:
            quota_limit = limit if isinstance(limit, QuotaLimit) else QuotaLimit.objects.get(slug=limit)
        except QuotaLimit.DoesNotExist:
            return "Not Found"

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
        PENDING = "pending"
        APPROVED = "approved"
        REJECTED = "rejected"

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quota_limit = models.ForeignKey(QuotaLimit, on_delete=models.CASCADE, related_name="quota_increase_requests")
    new_value = models.IntegerField()
    current_value = models.IntegerField()
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=StatusTypes.choices, default=StatusTypes.PENDING)

    class Meta:
        verbose_name = "Quota Increase Request"
        verbose_name_plural = "Quota Increase Requests"

    def __str__(self):
        return f"{self.user}"
