from django import template

from backend.utils import get_feature_status

register = template.Library()


@register.simple_tag
def feature_enabled(feature):
    return get_feature_status(feature)
