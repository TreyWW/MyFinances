from django import template

register = template.Library()


def split(string, char=" "):
    return string.split(char)


register.filter("split", split)
