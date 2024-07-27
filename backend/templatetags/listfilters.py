from typing import Any

from django import template

register = template.Library()


@register.simple_tag
def list_item_prefix_distinct(items: list, index: int = 0, separator=":"):
    return set(i.split(separator)[index] for i in items)


def lookup_separator_perms(items: list, lookup_value: Any):
    values = [i.split(":")[-1] for i in items if i.split(":")[0] == lookup_value]
    return values


def at_index(items: list, index: int = 0):
    return items[index]


register.filter("list_item_prefix_distinct", list_item_prefix_distinct)
register.filter("lookup_separator_perms", lookup_separator_perms)
register.filter("at_index", at_index)
