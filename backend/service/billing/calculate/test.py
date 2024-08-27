from backend.models import Usage, PlanFeature, PlanFeatureVersion, User, UserSubscription, SubscriptionPlan, PlanFeatureGroup
from backend.utils.calendar import timezone_now
from backend.utils.dataclasses import BaseServiceResponse
from collections import defaultdict
from django.db.models import Sum, Q
from decimal import Decimal, ROUND_HALF_UP, getcontext

getcontext().prec = 18


class GenerateBillingServiceResponse(BaseServiceResponse[int]): ...


def round_currency(value):
    """Round a decimal value to 2 decimal places using ROUND_HALF_UP."""
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def generate_monthly_billing_summary(user, month, year):
    """
    Generate a detailed billing summary for a user in a given month/year, taking into account plan changes.
    Returns a JSON array with details for each service and total amount.
    """
    # Get the user's subscription history during the specified month/year
    subscriptions = UserSubscription.objects.filter(
        Q(start_date__year=year, start_date__month=month) | Q(end_date__isnull=True) | Q(end_date__year=year, end_date__month=month),
        user=user,
    ).order_by("start_date")

    usage_data = Usage.objects.filter(user=user, timestamp__month=month, timestamp__year=year)

    groups = defaultdict(
        lambda: {"total_cost": Decimal("0.00"), "services": defaultdict(lambda: {"total_cost": Decimal("0.00"), "details": []})}
    )
    total_cost = Decimal("0.00")

    feature_name_to_display_name = {pf.slug: pf.name for pf in PlanFeature.objects.all()}

    # Track free tier usage and costs for each plan during the month
    feature_usage_per_plan = defaultdict(lambda: defaultdict(Decimal))

    # Process usage data
    for feature_usage in usage_data:
        feature_slug = feature_usage.feature
        total_quantity = Decimal(feature_usage.quantity)
        usage_timestamp = feature_usage.timestamp

        # Find the correct subscription for this usage based on the timestamp

        print()

        active_subscription = next(
            (sub for sub in subscriptions if sub.start_date <= usage_timestamp <= (sub.end_date or timezone_now())), None
        )

        if not active_subscription:
            print(f"No active subscription found for feature {feature_slug} at timestamp {usage_timestamp}")
            continue

        # Find the plan feature for this subscription
        try:
            plan_feature = PlanFeature.objects.get(slug=feature_slug, subscription_plan=active_subscription.subscription_plan)
        except PlanFeature.DoesNotExist:
            print(
                f"No plan feature found for feature {feature_slug} under the user's subscription plan {active_subscription.subscription_plan}"
            )
            continue

        # Find the relevant feature version
        plan_feature_version = PlanFeatureVersion.objects.filter(plan_feature=plan_feature).order_by("version").last()

        if not plan_feature_version:
            print(f"No version found for plan feature {feature_slug}")
            continue

        # Calculate free tier limit for this plan
        free_tier_limit = Decimal(plan_feature_version.free_tier_limit if plan_feature_version.free_tier_limit else 0)

        # Calculate the cost for this usage
        service_cost = Decimal("0.00")
        service_details = []

        # Check if the user is still within the free tier for the current plan
        if feature_usage_per_plan[active_subscription.id][feature_slug] + total_quantity <= free_tier_limit:
            # Entire usage is within free tier
            service_details.append(
                {
                    "description": f"${0.00:.2f} for {free_tier_limit} {plan_feature_version.unit} (Free tier)",
                    "quantity": total_quantity,
                    "cost": Decimal("0.00"),
                }
            )
            feature_usage_per_plan[active_subscription.id][feature_slug] += total_quantity
        else:
            # Part of the usage is within free tier, rest is chargeable
            free_units_remaining = max(free_tier_limit - feature_usage_per_plan[active_subscription.id][feature_slug], 0)
            chargeable_quantity = total_quantity - free_units_remaining

            if free_units_remaining > 0:
                service_details.append(
                    {
                        "description": f"£{0.00:.2f} for {free_units_remaining} {plan_feature_version.unit} (Free tier)",
                        "quantity": free_units_remaining,
                        "cost": Decimal("0.00"),
                    }
                )

            units_to_charge_for = chargeable_quantity / Decimal(plan_feature_version.units_per_cost)
            raw_cost = units_to_charge_for * Decimal(plan_feature_version.cost_per_unit)

            service_details.append(
                {
                    "description": f"£{plan_feature_version.cost_per_unit:.2f} per {plan_feature_version.units_per_cost} "
                    f"{plan_feature_version.unit} ({active_subscription.subscription_plan.name} plan)",
                    "quantity": chargeable_quantity,
                    "cost": raw_cost,
                }
            )
            service_cost += raw_cost

        # Track total usage and cost
        feature_usage_per_plan[active_subscription.id][feature_slug] += total_quantity
        total_cost += service_cost
        feature_group = plan_feature.group.name

        # Organize into groups
        groups[feature_group]["total_cost"] += service_cost
        groups[feature_group]["services"][feature_slug]["total_cost"] += service_cost
        groups[feature_group]["services"][feature_slug]["details"].extend(service_details)

    # Add subscription plan cost as an additional service
    for sub in subscriptions:
        subscription_cost = sub.custom_subscription_price_per_month or sub.subscription_plan.price_per_month
        subscription_service_name = f"Active MyFinances subscription tier ({sub.subscription_plan.name})"

        groups["Subscription"]["total_cost"] += subscription_cost
        groups["Subscription"]["services"][subscription_service_name]["total_cost"] = subscription_cost
        groups["Subscription"]["services"][subscription_service_name]["details"].append(
            {
                "description": f"Subscription to {sub.subscription_plan.name} plan",
                "quantity": 1,
                "cost": subscription_cost,
            }
        )
        total_cost += subscription_cost

    # Prepare billing summary
    billing_summary = {
        "total_services": len([s for g in groups.values() for s in g["services"]]),
        "total_cost": round_currency(total_cost),
        "groups": [],
    }

    for group_name, data in groups.items():
        group_summary = {
            "group_name": group_name,
            "total_cost": round_currency(data["total_cost"]),
            "services": [],
        }
        for service_name, service_data in data["services"].items():
            service_summary = {
                "service_name": feature_name_to_display_name.get(service_name, service_name),
                "total_cost": round_currency(service_data["total_cost"]),
                "details": service_data["details"],
            }
            group_summary["services"].append(service_summary)

        billing_summary["groups"].append(group_summary)

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
