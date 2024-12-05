"""Filters used in parsing of CWR files.

"""

from decimal import Decimal, ConversionSyntax, InvalidOperation

from django import template

from music_publisher import models
from music_metadata.territories.territory import Territory

register = template.Library()


@register.filter(name="perc")
def perc(value):
    """Display shares as human-readable string."""
    try:
        value = Decimal(value) / Decimal("100")
        return "{}%".format(value)
    except (ConversionSyntax, InvalidOperation, TypeError):
        return "Not convertible to percents."


@register.filter(name="soc_name")
def soc_name(value):
    """Display society name"""

    value = value.strip().lstrip("0")
    return models.SOCIETY_DICT.get(value, "")


@register.filter(name="capacity")
def capacity(value):
    """Display writer capacity/role"""

    value = value[0:2]
    obj = models.WriterInWork(capacity=value)
    return obj.get_capacity_display()


@register.filter(name="agreement_type")
def agreement_type(value):
    """Display publishing agreement type"""

    value = value.strip()
    return {
        "OG": "Original general",
        "OS": "Original specific",
        "PG": "Sub-Publishing general",
        "PS": "Sub-Publishing specific",
    }.get(value, "Unknown")


@register.filter(name="status")
def status(value):
    """Display acknowledgement status"""

    value = value.strip()
    obj = models.WorkAcknowledgement(status=value)
    return obj.get_status_display()


@register.filter(name="flag")
def flag(value):
    """Display flag value"""

    value = value.strip()
    return {
        "Y": "Yes",
        "N": "No",
        "U": "Unknown",
    }.get(value, "Not set")


@register.filter(name="orimod")
def orimod(value):
    """Display original or modification"""

    value = value.strip()
    return {
        "ORI": "Original Work",
        "MOD": "Modification",
    }.get(value, "Not set")


@register.filter(name="terr")
def terr(value):
    """Display territory"""

    value = value.strip()
    territory = Territory.get(value)
    return str(territory)


@register.filter(name="ie")
def ie(value):
    """Display Included / Excluded"""

    value = value.strip()
    if value == "E":
        return "excluding "
    return ""


@register.filter(name="role")
def role(value):
    """Display publisher role/capacity"""

    return {
        "E ": "Original Publisher",
        "AM": "Administrator",
        "SE": "Sub-publisher",
    }.get(value, "Unknown publisher role")


@register.filter(name="title_type")
def title_type(value):
    """Display alternative title type"""

    value = value.strip()
    obj = models.AlternateTitle(title_type=value)
    return obj.get_title_type_display()