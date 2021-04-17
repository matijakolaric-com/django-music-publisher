"""Filters used in generation of CWR files.

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
    """Calculate writer share, performance"""
    return calculate_value(value, PRW_SHARE)


@register.filter(name='prp')
def prp(value):
    """Calculate publisher share, performance"""
    return calculate_value(value, PRP_SHARE)


@register.filter(name='mrw')
def mrw(value):
    """Calculate writer share, mechanical"""
    return calculate_value(value, MRW_SHARE)


@register.filter(name='mrp')
def mrp(value):
    """Calculate publisher share, mechanical"""
    return calculate_value(value, MRP_SHARE)


@register.filter(name='srw')
def srw(value):
    """Calculate writer share, sync"""
    return calculate_value(value, SRW_SHARE)


@register.filter(name='srp')
def srp(value):
    """Calculate publisher share, sync"""
    return calculate_value(value, SRP_SHARE)


@register.filter(name='cwrshare')
def cwrshare(value):
    """Get CWR-compatible output for share fields"""
    value = (value * Decimal('10000')).quantize(
        Decimal('1.'), rounding=ROUND_HALF_UP)
    value = int(value)
    return '{:05d}'.format(value)
