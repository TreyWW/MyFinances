from django.db.models import QuerySet

from backend.core.api.public import APIAuthToken
from backend.models import UserSettings
from backend.core.service.defaults.get import get_account_defaults
from backend.core.types.requests import WebRequest


def validate_page(page: str | None) -> bool:
    return not page or page in ["profile", "account", "api_keys", "account_defaults", "account_security", "email_templates"]


def get_user_profile(request: WebRequest) -> UserSettings:
    try:
        usersettings = request.user.user_profile
    except UserSettings.DoesNotExist:
        # Create a new UserSettings object
        usersettings = UserSettings.objects.create(user=request.user)
    return usersettings


def get_api_keys(request: WebRequest) -> QuerySet[APIAuthToken]:
    return APIAuthToken.filter_by_owner(request.actor).filter(active=True).only("created", "name", "last_used", "description", "expires")


def account_page_context(request: WebRequest, context: dict) -> None:
    user_profile = get_user_profile(request)
    context.update({"currency_signs": user_profile.CURRENCIES, "currency": user_profile.currency})


def api_keys_page_context(request: WebRequest, context: dict) -> None:
    api_keys = get_api_keys(request)
    context.update({"api_keys": api_keys})


def account_defaults_context(request: WebRequest, context: dict) -> None:
    context.update({"account_defaults": get_account_defaults(request.actor)})


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
    print(context.get("email_templates"))
