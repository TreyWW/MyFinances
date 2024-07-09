from typing import Any

from django import template

register = template.Library()


@register.simple_tag
def list_item_prefix_distinct(items: list, index: int = 0, seperator=":"):
    return set(i.split(seperator)[index] for i in items)


def lookup_seperator_perms(items: list, lookup_value: Any):
    values = [i.split(":")[-1] for i in items if i.split(":")[0] == lookup_value]
    return values


register.filter("list_item_prefix_distinct", list_item_prefix_distinct)
register.filter("lookup_seperator_perms", lookup_seperator_perms)
