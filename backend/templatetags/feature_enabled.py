from django import template
from django.urls import NoReverseMatch

from backend.models import User, Organization
from backend.core.utils.feature_flags import get_feature_status

from django.conf import settings

register = template.Library()


@register.simple_tag
def has_module(module_str: str):
    return module_str in settings.INSTALLED_APPS


@register.simple_tag
def safe_url(view_name, *args, **kwargs):
    from django.urls import reverse

    try:
        return reverse(view_name, args=args, kwargs=kwargs)
    except NoReverseMatch:
        return ""


@register.simple_tag
def feature_enabled(feature):
    return get_feature_status(feature)


@register.simple_tag
def personal_feature_enabled(user: User, feature: str):
    return user.user_profile.has_feature(feature)


@register.simple_tag
def has_entitlement(actor: User | Organization, entitlement: str) -> bool:
    if not settings.BILLING_ENABLED:
        return True

    from billing.service.entitlements import has_entitlement as _has_entitlement

    return _has_entitlement(actor, entitlement)
