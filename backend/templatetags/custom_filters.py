from django import template

register = template.Library()


@register.filter(name="add")
def add(value, arg):
    return value + arg


@register.filter(name="subtract")
def subtract(value, arg):
    return value - arg


@register.filter(name="multiply")
def multiply(value, arg):
    return value * arg


@register.filter(name="divide")
def divide(value, arg):
    return value / arg if arg != 0 else 0  # Avoid division by zero
