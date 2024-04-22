from typing import Iterable, Any

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from backend.models import (
    Client,
    Invoice,
    InvoiceURL,
    InvoiceItem,
    PasswordSecret,
    AuditLog,
    LoginLog,
    Error,
    TracebackError,
    UserSettings,
    Notification,
    Team,
    TeamInvitation,
    User,
    InvoiceProduct,
    FeatureFlags,
    VerificationCodes,
    APIKey,
    InvoiceOnetimeSchedule,
    QuotaLimit,
    QuotaOverrides,
    QuotaUsage,
    QuotaIncreaseRequest,
    Receipt,
    ReceiptDownloadToken,
    EmailSendStatus,
    InvoiceReminder,
)

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
        Team,
        TeamInvitation,
        InvoiceProduct,
        FeatureFlags,
        VerificationCodes,
        APIKey,
        InvoiceOnetimeSchedule,
        Receipt,
        ReceiptDownloadToken,
        InvoiceReminder,
    ]
)


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
fields[0] = (None, {"fields": ("username", "password", "logged_in_as_team", "awaiting_email_verification")})
UserAdmin.fieldsets = tuple(fields)
admin.site.register(User, UserAdmin)

admin.site.site_header = "MyFinances Admin"
admin.site.index_title = "MyFinances"
admin.site.site_title = "MyFinances | Administration"
