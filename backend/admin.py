from django.contrib import admin

from backend.finance.models import (
    Invoice,
    InvoiceURL,
    InvoiceItem,
    InvoiceReminder,
    InvoiceRecurringProfile,
    InvoiceProduct,
    Receipt,
    ReceiptDownloadToken,
    FinanceDefaultValues,
)

# from django.contrib.auth.models imp/ort User
# admin.register(Invoice)
admin.site.register(
    [
        Invoice,
        InvoiceURL,
        InvoiceItem,
        InvoiceProduct,
        Receipt,
        ReceiptDownloadToken,
        InvoiceReminder,
        InvoiceRecurringProfile,
        FinanceDefaultValues,
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


class InvoiceURLAdmin(admin.ModelAdmin):
    readonly_fields = ["expires"]


# admin.site.register(QuotaLimit, QuotaLimitAdmin)
# admin.site.register(QuotaUsage, QuotaUsageAdmin)
# admin.site.register(QuotaOverrides, QuotaOverridesAdmin)
# admin.site.register(QuotaIncreaseRequest, QuotaIncreaseRequestAdmin)

admin.site.site_header = "MyFinances Admin"
admin.site.index_title = "MyFinances"
admin.site.site_title = "MyFinances | Administration"
