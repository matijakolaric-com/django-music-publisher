"""Filters used in generation of CWR files.

Their goal is to format the incoming data to the right fixed-length
format, as well as do some basic validation.
"""

from django import template
from datetime import date, time
from decimal import Decimal
from django.utils.html import mark_safe


register = template.Library()


@register.filter(name='rjust')
def rjust(value, length):
    """Format general numeric fields."""

    if value is None or value == '':
        value = '0'
    else:
        value = str(value)
    value = value.rjust(length, '0')
    return value


@register.filter(name='ljust')
def ljust(value, length):
    """Format general alphanumeric fields."""

    if value is None:
        value = ''
    else:
        value = str(value)
    value = value.ljust(length, ' ')
    return value


@register.filter(name='prshare')
def prshare(value):
    """Format and validate fields containing shares."""
    value = value or 0
    value = int(round(value * 50))
    return '{:05d}'.format(value)


@register.filter(name='mrshare')
def mrshare(value):
    """Format and validate fields containing shares."""

    value = value or 0
    value = int(round(value * 100))
    return '{:05d}'.format(value)
