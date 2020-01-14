"""Filters used in generation of CWR files.

Their goal is to format the incoming data to the right fixed-length
format, as well as do some basic validation.
"""

from django import template
from decimal import Decimal, ROUND_HALF_UP
from music_publisher import models
from django.conf import settings

register = template.Library()

PRP_SHARE = settings.PUBLISHING_AGREEMENT_PUBLISHER_PR
MRP_SHARE = settings.PUBLISHING_AGREEMENT_PUBLISHER_MR
SRP_SHARE = settings.PUBLISHING_AGREEMENT_PUBLISHER_SR
PRW_SHARE = Decimal('1') - PRP_SHARE
MRW_SHARE = Decimal('1') - MRP_SHARE
SRW_SHARE = Decimal('1') - SRP_SHARE


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


@register.filter(name='soc')
def soc(value):
    """Format society fields."""

    if not value:
        return '   '
    value = value.rjust(3, '0')
    return value


def calculate_value(value, share):
    value = Decimal(value or 0)
    value *= share
    return value


@register.filter(name='prw')
def prw(value):
    return calculate_value(value, PRW_SHARE)


@register.filter(name='prp')
def prp(value):
    return calculate_value(value, PRP_SHARE)


@register.filter(name='mrw')
def mrw(value):
    return calculate_value(value, MRW_SHARE)


@register.filter(name='mrp')
def mrp(value):
    return calculate_value(value, MRP_SHARE)


@register.filter(name='srw')
def srw(value):
    return calculate_value(value, SRW_SHARE)


@register.filter(name='srp')
def srp(value):
    return calculate_value(value, SRP_SHARE)


@register.filter(name='cwrshare')
def cwrshare(value):
    value = (value * Decimal('10000')).quantize(
        Decimal('1.'), rounding=ROUND_HALF_UP)
    value = int(value)
    return '{:05d}'.format(value)


@register.filter(name='perc')
def perc(value):
    """Display shares as human-readable string."""

    value = Decimal(value) / Decimal('100')
    return '{}%'.format(value)


@register.filter(name='soc_name')
def soc_name(value):
    """Display society name"""

    value = value.strip()
    return models.SOCIETY_DICT.get(value, '')


@register.filter(name='capacity')
def capacity(value):
    """Display capacity"""

    value = value.strip()
    obj = models.WriterInWork(capacity=value)
    return obj.get_capacity_display()


@register.filter(name='agreement_type')
def capacity(value):
    """Display agreement_type"""

    value = value.strip()
    return {
        'OG': 'Original general',
        'OS': 'Original specific',
    }.get(value, 'Unknown')
