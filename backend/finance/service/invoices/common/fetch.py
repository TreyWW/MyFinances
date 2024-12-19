from django.db.models import Prefetch, ExpressionWrapper, F, FloatField, Sum, Case, When, Q, Value, CharField, QuerySet
from django.utils import timezone

from backend.finance.models import Invoice, InvoiceItem


def should_add_condition(was_previous_selection, has_just_been_selected):
    return (was_previous_selection and not has_just_been_selected) or (not was_previous_selection and has_just_been_selected)


def get_context(invoices: QuerySet) -> tuple[dict, QuerySet[Invoice]]:
    context: dict = {}

    invoices = (
        invoices.prefetch_related(
            Prefetch(
                "items",
                queryset=InvoiceItem.objects.annotate(
                    subtotal=ExpressionWrapper(
                        F("hours") * F("price_per_hour"),
                        output_field=FloatField(),
                    ),
                ),
            ),
        )
        .select_related("client_to", "client_to__user", "user", "organization")
        # .only("invoice_id", "id", "payment_status", "date_due", "client_to", "client_name", "user", "organization")
        # .only was causing 100x more queries due to re-fetching extra fields
        .annotate(
            subtotal=Sum(F("items__hours") * F("items__price_per_hour")),
            amount=Case(
                When(vat_number=True, then=F("subtotal") * 1.2),
                default=F("subtotal"),
                output_field=FloatField(),
            ),
        )
        .distinct()  # just an extra precaution
    )

    if invoices.model is Invoice:
        invoices = invoices.annotate(
            filterable_dynamic_status=Case(
                When(status="draft", then=Value("draft")),
                When(status="pending", date_due__gt=timezone.now(), then=Value("pending")),
                When(status="pending", date_due__lt=timezone.now(), then=Value("overdue")),
                When(status="paid", then=Value("paid")),
                output_field=CharField(),
            )
        )

    context["invoices"] = invoices

    return context, invoices
