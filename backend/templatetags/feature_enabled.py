from django import template

from backend.models import User
from backend.utils.feature_flags import get_feature_status

register = template.Library()


@register.simple_tag
def feature_enabled(feature):
    return get_feature_status(feature)


@register.simple_tag
def personal_feature_enabled(user: User, feature: str):
    return user.user_profile.has_feature(feature)
