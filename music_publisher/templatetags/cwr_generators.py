"""Filters used in generation of CWR files.

Their goal is to format the incoming data to the right fixed-length
format, as well as do some basic validation.
"""

from decimal import Decimal, ROUND_HALF_UP

from django import template
from django.conf import settings

from music_publisher import models
from music_metadata.territories.territory import Territory

register = template.Library()

if hasattr(settings, 'PUBLISHING_AGREEMENT_PUBLISHER_PR'):
    PRP_SHARE = settings.PUBLISHING_AGREEMENT_PUBLISHER_PR
else:
    PRP_SHARE = Decimal('0.5')
if hasattr(settings, 'PUBLISHING_AGREEMENT_PUBLISHER_MR'):
    MRP_SHARE = settings.PUBLISHING_AGREEMENT_PUBLISHER_MR
else:
    MRP_SHARE = Decimal(1)
if hasattr(settings, 'PUBLISHING_AGREEMENT_PUBLISHER_SR'):
    SRP_SHARE = settings.PUBLISHING_AGREEMENT_PUBLISHER_SR
else:
    SRP_SHARE = Decimal(1)
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
    value = value.rjust(length, '0')[0:length]
    return value


@register.filter(name='ljust')
def ljust(value, length):
    """Format general alphanumeric fields."""

    if value is None:
        value = ''
    else:
        value = str(value)
    value = value.ljust(length, ' ')[0:length]
    return value


@register.filter(name='soc')
def soc(value):
    """Format society fields."""

    if not value:
        return '   '
    value = value.rjust(3, '0')
    return value


def calculate_value(value, share):
    """Convert string to a decimal and multiply with share."""
    value = Decimal(value or 0)
    value *= share
    return value


@register.filter(name='prw')
def prw(value):
    """Writer share, PR"""
    return calculate_value(value, PRW_SHARE)


@register.filter(name='prp')
def prp(value):
    """Publisher share, PR"""
    return calculate_value(value, PRP_SHARE)


@register.filter(name='mrw')
def mrw(value):
    """Writer share, MR"""
    return calculate_value(value, MRW_SHARE)


@register.filter(name='mrp')
def mrp(value):
    """Publisher share, MR"""
    return calculate_value(value, MRP_SHARE)


@register.filter(name='srw')
def srw(value):
    """Writer share, SR"""
    return calculate_value(value, SRW_SHARE)


@register.filter(name='srp')
def srp(value):
    """Publisher share, SR"""
    return calculate_value(value, SRP_SHARE)


@register.filter(name='cwrshare')
def cwrshare(value):
    """Get CWR-compatible output for the Share field."""
    value = (value * Decimal('10000')).quantize(
        Decimal('1.'), rounding=ROUND_HALF_UP)
    value = int(value)
    return '{:05d}'.format(value)
