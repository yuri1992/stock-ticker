from django import template
from django.template.defaultfilters import stringfilter

from stocks import utils

register = template.Library()


@register.filter
@stringfilter
def lower(value):
    return value.lower()


@register.filter
def hash(h, key):
    return h[key]


@register.simple_tag
def percentage_change(p1, p2):
    if p1 and p2:
        return utils.get_change(p1, p2)
    return 0
