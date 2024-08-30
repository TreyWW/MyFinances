# from backend.utils.calendar import timezone_now
# from backend.utils.dataclasses import BaseServiceResponse
# from collections import defaultdict
# from decimal import Decimal
# from typing import Dict, List, Tuple
#
# # from .file_storage import calculate_storage_cost, calculate_transfer_cost
# from .utils import round_currency, calculate_free_tier_cost, calculate_chargeable_cost
# from .subscription import get_user_subscriptions, get_highest_subscription_cost
# # from backend.models import Usage, PlanFeature, PlanFeatureVersion, UserSubscription
#
#
# class GenerateBillingServiceResponse(BaseServiceResponse[dict]):
#     ...
#
#
# def aggregate_usage_data(usage_data: List[Usage], subscriptions: List[UserSubscription]) -> Dict[UserSubscription, Dict[str, Decimal]]:
#     """Aggregate usage data by feature and subscription."""
#     aggregated_usage = defaultdict(lambda: defaultdict(Decimal))
#
#     for feature_usage in usage_data:
#         feature_slug = feature_usage.feature
#         total_quantity = Decimal(feature_usage.quantity)
#         usage_timestamp = feature_usage.timestamp
#
#         # Find active subscription for this usage
#         active_subscription = next(
#             (sub for sub in subscriptions if sub.start_date <= usage_timestamp <= (sub.end_date or timezone_now())), None
#         )
#
#         if active_subscription:
#             aggregated_usage[active_subscription][feature_slug] += total_quantity
#
#     return aggregated_usage
#
#
# def fetch_plan_and_version(feature_slug: str, active_subscription: UserSubscription) -> Tuple[PlanFeature, PlanFeatureVersion]:
#     """Fetch PlanFeature and its latest PlanFeatureVersion for the given feature and subscription plan."""
#     try:
#         plan_feature = PlanFeature.objects.get(slug=feature_slug, subscription_plan=active_subscription.subscription_plan)
#     except PlanFeature.DoesNotExist:
#         return None, None
#
#     plan_feature_version = PlanFeatureVersion.objects.filter(plan_feature=plan_feature).order_by("version").last()
#
#     return plan_feature, plan_feature_version
#
#
# def process_free_tier(
#     feature_usage_per_plan: Dict[int, Dict[str, Decimal]],
#     active_subscription: UserSubscription,
#     feature_slug: str,
#     total_quantity: Decimal,
#     free_tier_limit: Decimal,
#     plan_feature_version,
# ) -> Tuple[List[dict], Decimal]:
#     """Calculate free tier usage and cost."""
#     service_details = []
#     service_cost = Decimal("0.00")
#
#     if feature_usage_per_plan[active_subscription.id][feature_slug] + total_quantity <= free_tier_limit:
#         service_details.append(calculate_free_tier_cost(total_quantity, free_tier_limit, plan_feature_version.unit))
#         feature_usage_per_plan[active_subscription.id][feature_slug] += total_quantity
#     return service_details, service_cost
#
#
# def process_chargeable_cost(
#     feature_usage_per_plan: Dict[int, Dict[str, Decimal]],
#     active_subscription: UserSubscription,
#     feature_slug: str,
#     total_quantity: Decimal,
#     free_tier_limit: Decimal,
#     plan_feature_version,
# ) -> Tuple[List[dict], Decimal]:
#     """Calculate the chargeable cost for the quantity exceeding the free tier."""
#     service_details = []
#     service_cost = Decimal("0.00")
#
#     free_units_remaining = max(free_tier_limit - feature_usage_per_plan[active_subscription.id][feature_slug], 0)
#     chargeable_quantity = total_quantity - free_units_remaining
#
#     if free_units_remaining > 0:
#         service_details.append(calculate_free_tier_cost(free_units_remaining, free_units_remaining, plan_feature_version.unit))
#
#     # Calculate chargeable cost
#     service_details.append(
#         calculate_chargeable_cost(
#             quantity=chargeable_quantity,
#             cost_per_unit=Decimal(plan_feature_version.cost_per_unit),
#             units_per_cost=Decimal(plan_feature_version.units_per_cost),
#             unit=plan_feature_version.unit,
#             plan_name=active_subscription.subscription_plan.name,
#         )
#     )
#     service_cost += (chargeable_quantity / Decimal(plan_feature_version.units_per_cost)) * Decimal(plan_feature_version.cost_per_unit)
#
#     feature_usage_per_plan[active_subscription.id][feature_slug] += total_quantity
#
#     return service_details, service_cost
#
#
# def update_groups(groups: Dict[str, dict], feature_group: str, feature_slug: str, service_details: List[dict], service_cost: Decimal):
#     """Update the groups dictionary with the new service details and costs."""
#     groups[feature_group]["total_cost"] += service_cost
#     groups[feature_group]["services"][feature_slug]["total_cost"] += service_cost
#     groups[feature_group]["services"][feature_slug]["details"].extend(service_details)
#
#
# def process_feature_usage(usage_data: List[Usage], subscriptions: List[UserSubscription]) -> Tuple[Dict[str, dict], Decimal]:
#     """Process the usage data to generate cost per feature."""
#     feature_usage_per_plan = defaultdict(lambda: defaultdict(Decimal))
#     groups = defaultdict(
#         lambda: {"total_cost": Decimal("0.00"), "services": defaultdict(lambda: {"total_cost": Decimal("0.00"), "details": []})}
#     )
#     total_cost: Decimal = Decimal("0.00")
#
#     # Step 1: Aggregate usage data
#     aggregated_usage = aggregate_usage_data(usage_data, subscriptions)
#
#     # Step 2: Process each aggregated usage entry
#     for active_subscription, features in aggregated_usage.items():
#         for feature_slug, total_quantity in features.items():
#             plan_feature, plan_feature_version = fetch_plan_and_version(feature_slug, active_subscription)
#             if not plan_feature or not plan_feature_version:
#                 continue
#
#             free_tier_limit = Decimal(plan_feature_version.free_tier_limit or 0)
#
#             # Step 3: Process free tier usage
#             if feature_usage_per_plan[active_subscription.id][feature_slug] + total_quantity <= free_tier_limit:
#                 service_details, service_cost = process_free_tier(
#                     feature_usage_per_plan, active_subscription, feature_slug, total_quantity, free_tier_limit, plan_feature_version
#                 )
#             else:
#                 # Step 4: Process chargeable usage
#                 service_details, service_cost = process_chargeable_cost(
#                     feature_usage_per_plan, active_subscription, feature_slug, total_quantity, free_tier_limit, plan_feature_version
#                 )
#
#             # Step 5: Update groups
#             update_groups(groups, plan_feature.group.name, feature_slug, service_details, service_cost)
#
#             total_cost += service_cost
#
#     return groups, total_cost
#
#
# def generate_monthly_billing_summary(user, month: int, year: int) -> GenerateBillingServiceResponse:
#     """Main entry function to generate the billing summary."""
#     total_cost: Decimal = Decimal(0)
#
#     subscriptions = get_user_subscriptions(user, month, year)
#     usage_data = Usage.objects.filter(user=user, timestamp__month=month, timestamp__year=year)
#
#     groups, usage_total_cost = process_feature_usage(usage_data, subscriptions)
#     total_cost += usage_total_cost
#
#     # storage pricing
#
#     # storage_costs = calculate_storage_cost(user, month, year, subscriptions)
#     # transfer_costs = calculate_transfer_cost(user, month, year, subscriptions)
#     #
#     # print(storage_costs)
#     #
#     # # Add dynamic storage costs under appropriate groups
#     # for service_name, data in storage_costs.items():
#     #     total_cost += data["cost"]
#     #     group_name = "Strelix File Storage" if "Strelix" in service_name else "Receipts"
#     #     if group_name not in groups:
#     #         groups[group_name] = {"total_cost": Decimal("0.00"), "services": {}}
#     #
#     #     groups[group_name]["total_cost"] += data["cost"]
#     #     groups[group_name]["services"][service_name] = {
#     #         "total_cost": data["cost"],
#     #         "details": [{"description": service_name, "quantity": data["quantity"], "cost": data["cost"]}],
#     #     }
#     #
#     # # Add dynamic transfer costs under the Data Transfer group
#     # for service_name, data in transfer_costs.items():
#     #     total_cost += data["cost"]
#     #     if "Data Transfer" not in groups:
#     #         groups["Data Transfer"] = {"total_cost": Decimal("0.00"), "services": {}}
#     #
#     #     groups["Data Transfer"]["total_cost"] += data["cost"]
#     #     groups["Data Transfer"]["services"][service_name] = {
#     #         "total_cost": data["cost"],
#     #         "details": [{"description": service_name, "quantity": data["quantity"], "cost": data["cost"]}],
#     #     }
#
#     # # subscription pricing
#
#     highest_subscription_object, highest_subscription_cost = get_highest_subscription_cost(subscriptions)
#
#     total_cost = usage_total_cost + highest_subscription_cost
#     groups["Subscription"]["total_cost"] += highest_subscription_cost
#     if highest_subscription_cost >= 0:
#         groups["Subscription"]["services"]["Active Subscription"]["total_cost"] = highest_subscription_cost
#         groups["Subscription"]["services"]["Active Subscription"]["details"].append(
#             {
#                 "description": f"{highest_subscription_object.subscription_plan.name.title()} plan (highest plan this month)",
#                 "quantity": 1,
#                 "cost": highest_subscription_cost,
#             }
#         )
#
#     # Prepare billing summary response
#     billing_summary = {
#         "total_services": len([s for g in groups.values() for s in g["services"]]),
#         "total_cost": round_currency(total_cost),
#         "groups": [],
#     }
#
#     for group_name, data in groups.items():
#         group_summary = {
#             "group_name": group_name,
#             "total_cost": round_currency(data["total_cost"]),
#             "services": [],
#         }
#         for service_name, service_data in data["services"].items():
#             service_summary = {
#                 "service_name": service_name,
#                 "total_cost": round_currency(service_data["total_cost"]),
#                 "details": service_data["details"],
#             }
#             group_summary["services"].append(service_summary)
#
#         billing_summary["groups"].append(group_summary)
#
#     return GenerateBillingServiceResponse(True, response=billing_summary)
