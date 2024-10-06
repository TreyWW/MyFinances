from typing import Any

from django import template

register = template.Library()


@register.simple_tag
def dict_get(dictionary: dict, key: Any):
    return dictionary.get(key)


register.filter("dict_get", dict_get)
