from django.db import models


class InvoiceRecurringProfile_WithItemsManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().select_related("client_to").prefetch_related("generated_invoices__items", "generated_invoices")
