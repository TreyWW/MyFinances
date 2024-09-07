from django.core.management.base import BaseCommand
from django.core.cache import cache
import stripe


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "action",
            type=str,
            help="help, create_entitlements",
        )

    def handle(self, *args, **kwargs):
        action = kwargs.get("action")

        match action:
            case "create_entitlements":
                for entitlement in [
                    "Receipts",
                    "File Storage",
                    "Organizations",
                    "Invoice Reminders",
                    "API Access",
                    "Emails",
                    "Advanced Onboarding",
                    "Basic Onboarding",
                    "Invoice Schedules",
                    "Invoices",
                    "Customers",
                ]:
                    try:
                        stripe.entitlements.Feature.create(name=entitlement, lookup_key=entitlement.lower().replace(" ", "-"))
                        print(f"Created entitlement: {entitlement}")
                    except stripe.error.InvalidRequestError:
                        print(f"Entitlement already exists: {entitlement}")
            case (_, "help"):
                print(
                    """
                    Available actions:
                    - create_entitlements: This will create all entitlements that you don't have
                """
                )
