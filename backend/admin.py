from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from backend.core.api.public import APIAuthToken
from backend.core.models import (
    PasswordSecret,
    AuditLog,
    LoginLog,
    Error,
    TracebackError,
    UserSettings,
    Notification,
    Organization,
    TeamInvitation,
    TeamMemberPermission,
    User,
    FeatureFlags,
    VerificationCodes,
    QuotaLimit,
    QuotaOverrides,
    QuotaUsage,
    QuotaIncreaseRequest,
    EmailSendStatus,
    FileStorageFile,
    MultiFileUpload,
)
from backend.finance.models import (
    Invoice,
    InvoiceURL,
    InvoiceItem,
    InvoiceReminder,
    InvoiceRecurringProfile,
    InvoiceProduct,
    Receipt,
    ReceiptDownloadToken,
)

from backend.clients.models import Client, DefaultValues

from settings.settings import BILLING_ENABLED

# from django.contrib.auth.models imp/ort User
# admin.register(Invoice)
admin.site.register(
    [
        UserSettings,
        Client,
        Invoice,
        InvoiceURL,
        InvoiceItem,
        PasswordSecret,
        AuditLog,
        LoginLog,
        Error,
        TracebackError,
        Notification,
        Organization,
        TeamInvitation,
        TeamMemberPermission,
        InvoiceProduct,
        FeatureFlags,
        VerificationCodes,
        Receipt,
        ReceiptDownloadToken,
        InvoiceReminder,
        APIAuthToken,
        InvoiceRecurringProfile,
        FileStorageFile,
        MultiFileUpload,
        DefaultValues,
    ]
)

if BILLING_ENABLED:
    from billing.models import PlanFeature, PlanFeatureGroup, SubscriptionPlan, UserSubscription

    admin.site.register([PlanFeature, PlanFeatureGroup, SubscriptionPlan, UserSubscription])


class QuotaLimitAdmin(admin.ModelAdmin):
    readonly_fields = ["name", "slug"]


class QuotaOverridesAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        return super().get_queryset(request).select_related("quota_limit", "user")


class QuotaUsageAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        return super().get_queryset(request).select_related("quota_limit", "user")


class QuotaIncreaseRequestAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        return super().get_queryset(request).select_related("quota_limit", "user")


class EmailSendStatusAdmin(admin.ModelAdmin):
    readonly_fields = ["aws_message_id"]


class InvoiceURLAdmin(admin.ModelAdmin):
    readonly_fields = ["expires"]


admin.site.register(QuotaLimit, QuotaLimitAdmin)
admin.site.register(QuotaUsage, QuotaUsageAdmin)
admin.site.register(QuotaOverrides, QuotaOverridesAdmin)
admin.site.register(QuotaIncreaseRequest, QuotaIncreaseRequestAdmin)
admin.site.register(EmailSendStatus, EmailSendStatusAdmin)

# admin.site.unregister(User)
fields = list(UserAdmin.fieldsets)  # type: ignore[arg-type]
fields[0] = (
    None,
    {
        "fields": (
            "username",
            "password",
            "logged_in_as_team",
            "awaiting_email_verification",
            "stripe_customer_id",
            "entitlements",
            "require_change_password",
        )
    },
)
UserAdmin.fieldsets = tuple(fields)
admin.site.register(User, UserAdmin)

admin.site.site_header = "MyFinances Admin"
admin.site.index_title = "MyFinances"
admin.site.site_title = "MyFinances | Administration"
