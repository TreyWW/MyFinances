from collections import defaultdict
from datetime import datetime
from decimal import Decimal
from typing import List, Tuple, Dict

from django.db.models import Q
from django.utils.timezone import make_aware

from backend.models import StorageUsage, PlanFeature, UserSubscription, PlanFeatureVersion, TransferUsage
from backend.utils.calendar import timezone_now


def calculate_storage_cost(user, month: int, year: int, subscriptions: List[UserSubscription]) -> Dict[str, Dict[str, Tuple[Decimal, str]]]:
    """
    Calculate storage costs and details for a user based on their subscription plans and storage usage.
    Returns a dictionary with total cost and quantity for each storage feature.
    """

    # return a list of services for storage, e.g.:
    #
    # {
    #     "groups": {
    #         "Receipts": {
    #             "cost": 125,
    #             "details": ...
    #         }
    #     }
    # }

    pass


def calculate_transfer_cost(
    user, month: int, year: int, subscriptions: List[UserSubscription]
) -> Dict[str, Dict[str, Tuple[Decimal, str]]]:
    transfer_costs = defaultdict(lambda: {"cost": Decimal("0.00"), "quantity": Decimal("0.00")})

    # Aggregate usage data for transfers
    transfers = TransferUsage.objects.filter(user=user, timestamp__year=year, timestamp__month=month)

    for transfer in transfers:
        # Find the active subscription for this transfer
        active_subscription = next(
            (sub for sub in subscriptions if sub.start_date <= transfer.timestamp <= (sub.end_date or timezone_now())), None
        )
        if not active_subscription:
            continue

        # Dynamically fetch the PlanFeature and PlanFeatureVersion for this transfer type
        try:
            plan_feature = transfer.feature
            plan_feature_version = PlanFeatureVersion.objects.filter(plan_feature=plan_feature).order_by("version").last()
        except PlanFeature.DoesNotExist:
            continue

        # Extract relevant fields from the PlanFeatureVersion
        cost_per_unit = Decimal(plan_feature_version.cost_per_unit)
        units_per_cost = Decimal(plan_feature_version.units_per_cost or 1)
        minimum_billable_size = Decimal(plan_feature_version.minimum_billable_size or 0)

        # Calculate amount in MB, ensuring it's at least the minimum billable size
        amount_mb = max(transfer.amount_in_MB, minimum_billable_size)

        # Calculate billable amount beyond the free tier
        billable_amount = amount_mb / units_per_cost

        # Calculate the cost
        cost = billable_amount * cost_per_unit

        # Aggregate cost and quantity by service_name
        transfer_costs[plan_feature.name]["cost"] += cost
        transfer_costs[plan_feature.name]["quantity"] += billable_amount

    # Format the response to include cost and quantity
    formatted_transfer_costs = {
        service_name: {"cost": cost_quantity["cost"], "quantity": f"{cost_quantity['quantity']:.2f} GB"}
        for service_name, cost_quantity in transfer_costs.items()
    }

    return formatted_transfer_costs
