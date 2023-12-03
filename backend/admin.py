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
)
from django.contrib import admin

# admin.register(Invoice)
admin.site.register(UserSettings)
admin.site.register(Client)
admin.site.register(Invoice)
admin.site.register(InvoiceURL)
admin.site.register(InvoiceItem)
admin.site.register(PasswordSecret)
admin.site.register(AuditLog)
admin.site.register(LoginLog)
admin.site.register(Error)
admin.site.register(TracebackError)
admin.site.register(Notification)
admin.site.register(Team)
admin.site.register(TeamInvitation)
admin.site.register(User, UserAdmin)
