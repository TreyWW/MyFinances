from backend.models import (
    Invoice,
    Client,
    InvoiceItem,
    PasswordSecret,
    AuditLog,
    LoginLog,
    Error,
    TracebackError,
    UserSettings,
)
from django.contrib import admin

# admin.register(Invoice)
admin.site.register(UserSettings)
admin.site.register(Invoice)
admin.site.register(Client)
admin.site.register(InvoiceItem)
admin.site.register(PasswordSecret)
admin.site.register(AuditLog)
admin.site.register(LoginLog)
admin.site.register(Error)
admin.site.register(TracebackError)
