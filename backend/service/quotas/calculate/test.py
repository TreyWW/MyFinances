from decimal import Decimal
from django.db.models import Sum
from django.utils import timezone

from backend.models import Usage, UserPlan, PlanFeature, PlanFeatureVersion
from backend.utils.dataclasses import BaseServiceResponse
from collections import defaultdict
from django.db.models import Sum
from decimal import Decimal, ROUND_HALF_UP, getcontext

getcontext().prec = 18


class GenerateBillingServiceResponse(BaseServiceResponse[int]): ...


def round_currency(value):
    """Round a decimal value to 2 decimal places using ROUND_HALF_UP."""
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def generate_monthly_billing_summary(user, month, year):
    """
    Generate a detailed billing summary for a user in a given month/year.
    Returns a JSON array with details for each service and total amount.
    """
    usage_data = Usage.objects.filter(user=user, timestamp__month=month, timestamp__year=year)

    services = defaultdict(lambda: {"total_cost": Decimal("0.00"), "details": []})
    total_cost = Decimal("0.00")

    for feature_usage in usage_data.values("feature").annotate(total_quantity=Sum("quantity")):
        feature_name = feature_usage["feature"]
        total_quantity = Decimal(feature_usage["total_quantity"])

        try:
            user_plan = UserPlan.objects.get(user=user, plan__feature__slug=feature_name)
            plan = user_plan.plan
        except UserPlan.DoesNotExist:
            print(f"No plan found for feature {feature_name}")
            continue

        # Retrieve the correct PlanFeatureVersion
        try:
            plan_feature_version = PlanFeatureVersion.objects.filter(plan_feature=plan).order_by("version").last()
        except PlanFeatureVersion.DoesNotExist:
            print(f"No version found for plan feature {feature_name}")
            continue

        # Free tier logic (e.g., 1000 emails free every month)
        free_tier_limit = Decimal(plan_feature_version.free_tier_limit if plan_feature_version.free_tier_limit else 0)
        service_cost = Decimal("0.00")
        service_details = []

        if total_quantity <= free_tier_limit:
            # Entire usage is within the free tier
            service_details.append(
                {
                    "description": f"${0.00:.2f} for {free_tier_limit} {plan_feature_version.unit} (Free tier)",
                    "quantity": total_quantity,
                    "cost": 0.00,
                }
            )
        else:
            # Calculate paid usage beyond the free tier
            chargeable_quantity = total_quantity - free_tier_limit

            if free_tier_limit > 0:
                service_details.append(
                    {
                        "description": f"${0.00:.2f} for {free_tier_limit} {plan_feature_version.unit} (Free tier)",
                        "quantity": free_tier_limit,
                        "cost": 0.00,
                    }
                )

            # Calculate cost for the chargeable quantity
            units_to_charge_for = chargeable_quantity / Decimal(plan_feature_version.units_per_cost)
            raw_cost = units_to_charge_for * Decimal(plan_feature_version.cost_per_unit)

            service_details.append(
                {
                    "description": f"${plan_feature_version.cost_per_unit:.2f} per {plan_feature_version.units_per_cost} {plan_feature_version.unit}",
                    "quantity": chargeable_quantity,
                    "cost": raw_cost,
                }
            )

            service_cost += raw_cost

        # Add the service's total cost to the overall total
        total_cost += service_cost
        services[feature_name]["total_cost"] += service_cost
        services[feature_name]["details"].extend(service_details)

    # Final rounding of the total cost (after accumulating precise usage)
    billing_summary = {
        "total_services": len(services),
        "total_cost": round_currency(total_cost),  # Final total rounded to 2 decimals
        "services": [],
    }

    for service_name, data in services.items():
        service_summary = {
            "service_name": service_name,
            "total_cost": round_currency(data["total_cost"]),  # Round each service's total
            "details": data["details"],
        }
        billing_summary["services"].append(service_summary)

    return billing_summary


def log_storage_usage(user, gb_used, duration_in_hours):
    """
    Log the storage usage in GB for a certain duration (in hours).
    Apply minimum billable size if needed.
    """
    # Get the user's plan for storage
    storage_plan = PlanFeature.objects.get(feature="storage")

    # Apply minimum billable size
    if storage_plan.minimum_billable_size and gb_used < storage_plan.minimum_billable_size:
        gb_used = storage_plan.minimum_billable_size

    # Calculate the GB-hours used
    gb_hours = gb_used * duration_in_hours

    Usage.objects.create(user=user, feature="storage", quantity=gb_hours, unit="GB-hour")


def log_transfer_usage(user, gb_transferred):
    """
    Log outbound data transfer in GB for billing.
    """
    storage_plan = PlanFeature.objects.get(feature="storage")

    # Transfer cost is applied per GB transferred
    Usage.objects.create(user=user, feature="storage_transfer", quantity=gb_transferred, unit="GB")
