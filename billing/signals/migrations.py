from __future__ import annotations

import logging

from django.db.models.signals import post_migrate
from django.dispatch import receiver

from billing.data.default_usage_plans import default_usage_plans, default_subscription_plans, DefaultFeature, DefaultSubscriptionPlan
from billing.models import PlanFeature, PlanFeatureGroup, SubscriptionPlan


#
@receiver(post_migrate)
def update_usage_plans(**kwargs):
    subscription_plans: dict = {}

    subscription_plan: DefaultSubscriptionPlan

    for subscription_plan in default_subscription_plans:
        if plan := SubscriptionPlan.objects.filter(name=subscription_plan.name).first():
            subscription_plans[plan.name] = plan
        else:
            subscription_plans[subscription_plan.name] = SubscriptionPlan.objects.create(
                name=subscription_plan.name,
                description=subscription_plan.description,
                price_per_month=subscription_plan.price_per_month,
            )
            logging.info(f"Added SubscriptionPlan {subscription_plan.name}")

    for group in default_usage_plans:
        group_obj, created = PlanFeatureGroup.objects.get_or_create(name=group.name)

        if created:
            logging.info(f"Created group {group.name}")

        item: DefaultFeature
        for item in group.items:
            existing: PlanFeature = PlanFeature.objects.filter(
                slug=item.slug, subscription_plan=SubscriptionPlan.objects.get(name=item.subscription_plan.name)
            ).first()

            if existing:
                description, old_subscription_plan, max_limit_per_month = (
                    existing.description,
                    existing.subscription_plan,
                    existing.max_limit_per_month,
                )

                existing.description = item.description
                existing.max_limit_per_month = item.max_limit_per_month if item.max_limit_per_month != -1 else None

                if (
                    existing.description != description
                    or (existing.max_limit_per_month == None and max_limit_per_month != -1)
                    or (existing.max_limit_per_month != None and max_limit_per_month == -1)
                    or (existing.max_limit_per_month != None and existing.max_limit_per_month != max_limit_per_month)
                ):
                    existing.save()

                    logging.info(f"Updated PlanFeature description/limits for {item.slug}")
            else:
                existing = PlanFeature.objects.create(
                    group=group_obj,
                    description=item.description,
                    slug=item.slug,
                    max_limit_per_month=item.max_limit_per_month,
                    subscription_plan=SubscriptionPlan.objects.get(name=item.subscription_plan.name),
                )
                logging.info(f"Added PlanFeature {item.slug}")
