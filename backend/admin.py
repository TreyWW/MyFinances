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
    VerificationCodes
)

# admin.register(Invoice)
admin.site.register([UserSettings,
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
                     VerificationCodes
                     ])
admin.site.register(User, UserAdmin)

admin.site.site_header = "MyFinances Admin"
admin.site.index_title = "MyFinances"
admin.site.site_title = "MyFinances | Administration"
