"""Filters used in generation of CWR files.

Their goal is to format the incoming data to the right fixed-length
format, as well as do some basic validation.
"""

from django import template
from datetime import date, time
from decimal import Decimal
from django.utils.html import mark_safe
# from unidecode import unidecode


register = template.Library()


# @register.filter(name='booleanfield')
# def booleanfield(value, length):
#     """Format and validate boolean fields.

#     Note that non-required flag fields are treated as boolean."""

#     if value is None or value == '':
#         value = ' '
#     elif value is False:
#         value = 'N'
#     elif value is True:
#         value = 'Y'
#     if len(value) > length:
#         raise AttributeError('Field value too long: {}'.format(value))
#     return value.ljust(length).upper()


# @register.filter(name='flagfield')
# def flagfield(value, length):
#     """Format and validate required flag fields."""

#     if value is None or value == '':
#         value = 'U'
#     elif value is False:
#         value = 'N'
#     elif value is True:
#         value = 'Y'
#     if len(value) > length:
#         raise AttributeError('Field value too long: {}'.format(value))
#     return value.ljust(length).upper()


@register.filter(name='rjust')
def rjust(value, length):
    """Format and general numeric fields."""

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
