from django.db import models
from backend.models.user import User
from typing import Optional, NoReturn, Union, Literal
from django.utils import timezone


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
