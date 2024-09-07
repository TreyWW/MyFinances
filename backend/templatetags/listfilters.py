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


@register.simple_tag
def common_items(*lists: list[list]) -> list:
    result = set(lists[0])
    for lst in lists[1:]:
        result.intersection_update(lst)
    return list(result)


@register.simple_tag
def common_items_count(*lists: list[list]) -> int:
    return len(common_items(*lists))


def common_children_filter(list1, list2):
    return common_items(list1, list2)


@register.filter
def get_first_n_items(value, n):
    """
    Returns the first n items of a list.
    """
    try:
        return value[:n]
    except TypeError:
        return []


register.filter("list_item_prefix_distinct", list_item_prefix_distinct)
register.filter("lookup_separator_perms", lookup_separator_perms)
register.filter("at_index", at_index)
register.filter("common_children_filter", common_children_filter)
