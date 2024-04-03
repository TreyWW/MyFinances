from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from backend.models.client import Client
from backend.models.notification import Notification
from backend.models.receipt import Receipt, ReceiptDownloadToken
from backend.models.invoice import (
    Invoice,
    InvoiceURL,
    InvoiceItem,
    InvoiceProduct,
    InvoiceOnetimeSchedule,
)
from backend.models.logger import AuditLog, LoginLog
from backend.models.error import Error, TracebackError
from backend.models import (
    PasswordSecret,
    UserSettings,
    Team,
    TeamInvitation,
    User,
    FeatureFlags,
    VerificationCodes,
    APIKey,
    QuotaLimit,
    QuotaOverrides,
    QuotaUsage,
    QuotaIncreaseRequest,
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
        QuotaOverrides,
        QuotaUsage,
        QuotaIncreaseRequest,
        Receipt,
        ReceiptDownloadToken,
    ]
)


class QuotaLimitAdmin(admin.ModelAdmin):
    readonly_fields = ["name", "slug"]


admin.site.register(QuotaLimit, QuotaLimitAdmin)

# admin.site.unregister(User)
fields = list(UserAdmin.fieldsets)
fields[0] = (None, {"fields": ("username", "password", "logged_in_as_team", "awaiting_email_verification")})
UserAdmin.fieldsets = tuple(fields)
admin.site.register(User, UserAdmin)

admin.site.site_header = "MyFinances Admin"
admin.site.index_title = "MyFinances"
admin.site.site_title = "MyFinances | Administration"
