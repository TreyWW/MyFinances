from django import template

register = template.Library()


def split(string, char=" "):
    return string.split(char)


def dashify(string, recurrence=2):
    num_str = str(string)

    return "-".join(num_str[i : i + recurrence] for i in range(0, len(num_str), recurrence))


def contains(value, arg):
    return arg in str(value)


register.filter("split", split)
register.filter("dashify", dashify)
register.filter("contains", contains)
