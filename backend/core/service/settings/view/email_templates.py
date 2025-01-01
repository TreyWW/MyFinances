from core.types.requests import WebRequest

from backend.finance.service.defaults.get import get_account_defaults


def email_templates_context(request: WebRequest, context: dict) -> None:
    acc_defaults = get_account_defaults(request.actor)
    context.update(
        {
            "account_defaults": acc_defaults,
            "email_templates": {
                "recurring_invoices": {
                    "invoice_created": acc_defaults.email_template_recurring_invoices_invoice_created,
                    "invoice_overdue": acc_defaults.email_template_recurring_invoices_invoice_overdue,
                    "invoice_cancelled": acc_defaults.email_template_recurring_invoices_invoice_cancelled,
                }
            },
        }
    )
    # print(context.get("email_templates"))
