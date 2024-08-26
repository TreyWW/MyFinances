from __future__ import annotations

import logging

from django.db.models.signals import post_migrate
from django.dispatch import receiver

from backend.data.default_feature_flags import default_feature_flags
from backend.data.default_quota_limits import default_quota_limits
from backend.data.default_usage_plans import default_usage_plans, default_subscription_plans, Feature, SubscriptionPlanItem
from backend.models import FeatureFlags, QuotaLimit, PlanFeature, PlanFeatureVersion, PlanFeatureGroup, SubscriptionPlan


@receiver(post_migrate)
def update_feature_flags(**kwargs):
    for feature_flag in default_feature_flags:
        existing_item = FeatureFlags.objects.filter(name=feature_flag.name).first()

        if existing_item:
            name, value, description = (
                existing_item.name,
                existing_item.value,
                existing_item.description,
            )

            existing_item.name = name
            existing_item.description = description

            if existing_item.name != name or existing_item.description != description:
                existing_item.save()
                logging.info(f"Updated feature flag: {feature_flag.name}")
        else:
            FeatureFlags.objects.create(name=feature_flag.name, value=feature_flag.default, description=feature_flag.description)
            logging.info(f"Added feature flag: {feature_flag.name}")


@receiver(post_migrate)
def update_quota_limits(**kwargs):
    for group in default_quota_limits:
        for item in group.items:
            existing = QuotaLimit.objects.filter(slug=f"{group.name}-{item.slug}").first()
            if existing:
                name, value, adjustable, description, limit_type = (
                    existing.name,
                    existing.value,
                    existing.adjustable,
                    existing.description,
                    existing.limit_type,
                )
                existing.name = item.name
                existing.adjustable = item.adjustable
                existing.description = item.description
                existing.limit_type = item.period
                if (
                    item.name != name
                    or item.default_value != value
                    or item.adjustable != adjustable
                    or item.description != description
                    or item.period != limit_type
                ):
                    logging.info(f"Updated QuotaLimit {item.name}")
                    existing.save()
            else:
                QuotaLimit.objects.create(
                    name=item.name,
                    slug=f"{group.name}-{item.slug}",
                    value=item.default_value,
                    adjustable=item.adjustable,
                    description=item.description,
                    limit_type=item.period,
                )
                logging.info(f"Added QuotaLimit {item.name}")


@receiver(post_migrate)
def update_usage_plans(**kwargs):
    subscription_plans: dict = {}

    subscription_plan: SubscriptionPlanItem

    for subscription_plan in default_subscription_plans:
        if plan := SubscriptionPlan.objects.filter(name=subscription_plan.name).first():
            subscription_plans[plan.name] = plan
        else:
            subscription_plans[subscription_plan.name] = SubscriptionPlan.objects.create(
                name=subscription_plan.name,
                description=subscription_plan.description,
                price_per_month=subscription_plan.price_per_month,
                maximum_duration_months=subscription_plan.maximum_duration_months,
            )
            logging.info(f"Added SubscriptionPlan {subscription_plan.name}")

    for group in default_usage_plans:
        group_obj, created = PlanFeatureGroup.objects.get_or_create(name=group.name)

        if created:
            logging.info(f"Created group {group.name}")

        item: Feature
        for item in group.items:
            existing: PlanFeature = PlanFeature.objects.filter(
                slug=item.slug, subscription_plan=SubscriptionPlan.objects.get(name=item.subscription_plan.name)
            ).first()

            if existing:
                name, description, old_subscription_plan = (existing.name, existing.description, existing.subscription_plan)

                existing.name = item.name
                existing.description = item.description

                if existing.name != name or existing.description != description:
                    existing.save()
                    logging.info(f"Updated PlanFeature name/description {item.name}")
            else:
                existing = PlanFeature.objects.create(
                    group=group_obj,
                    name=item.name,
                    description=item.description,
                    slug=item.slug,
                    subscription_plan=SubscriptionPlan.objects.get(name=item.subscription_plan.name),
                )

                PlanFeatureVersion.objects.create(
                    plan_feature=existing,
                    free_tier_limit=item.free_tier_limit,
                    free_period_in_months=item.free_period_in_months,
                    unit=item.unit,
                    cost_per_unit=item.cost_per_unit,
                    minimum_billable_size=item.minimum_billable_size,
                )
                logging.info(f"Added PlanFeature {item.name}")
