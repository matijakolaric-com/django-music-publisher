"""Filters used in generation of CWR files.

Their goal is to format the incoming data to the right fixed-length
format, as well as do some basic validation.
"""

from decimal import Decimal

from django import template

from music_publisher import models
from music_metadata.territories.territory import Territory

register = template.Library()


@register.filter(name='perc')
def perc(value):
    """Display shares as human-readable string."""

    value = Decimal(value) / Decimal('100')
    return '{}%'.format(value)


@register.filter(name='soc_name')
def soc_name(value):
    """Display society name"""

    value = value.strip().lstrip('0')
    return models.SOCIETY_DICT.get(value, '')


@register.filter(name='capacity')
def capacity(value):
    """Display capacity"""

    value = value.strip()
    obj = models.WriterInWork(capacity=value)
    return obj.get_capacity_display()


@register.filter(name='agreement_type')
def agreement_type(value):
    """Display agreement_type"""

    value = value.strip()
    return {
        'OG': 'Original general',
        'OS': 'Original specific',
    }.get(value, 'Unknown')


@register.filter(name='status')
def status(value):
    """Transaction Status"""

    value = value.strip()
    obj = models.WorkAcknowledgement(status=value)
    return obj.get_status_display()


@register.filter(name='flag')
def flag(value):
    """Transaction Status"""

    value = value.strip()
    return {
        'Y': 'Yes',
        'N': 'No',
        'U': 'Unknown',
    }.get(value, 'Not set')


@register.filter(name='orimod')
def orimod(value):
    """Transaction Status"""

    value = value.strip()
    return {
        'ORI': 'Original Work',
        'MOD': 'Modification',
    }.get(value, 'Not set')


@register.filter(name='terr')
def terr(value):
    """Territory name"""

    value = value.strip()
    territory = Territory.get(value)
    return str(territory)


@register.filter(name='ie')
def ie(value):
    """Included / Excluded"""

    value = value.strip()
    if value == 'E':
        return 'excluding '
    return ''


@register.filter(name='role')
def role(value):
    """Publisher role"""

    return {
        'E ': 'Original Publisher',
        'AM': 'Administrator',
        'SE': 'Sub-publisher'
    }.get(value, 'Unknown publisher role')
