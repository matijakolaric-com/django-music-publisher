"""CWR-compatibility field-level validation.

For formats that allow dashes and dots (ISWC, IPI Base), the actual format is
from CWR 2.x specification for compatibility.

"""

import re

from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible

TITLES_CHARS = re.escape(
    r"!\"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\]^_`{}~£€")
NAMES_CHARS = re.escape(r"!#$%&'()+-./0123456789?@ABCDEFGHIJKLMNOPQRSTUVWXYZ`")

RE_TITLE = r'(^[{0}][ {0}]*$)'.format(TITLES_CHARS)
RE_NAME = r'(^[{0}][ {0}]*$)'.format(NAMES_CHARS)
RE_ISWC = re.compile(r'(^T\d{10}$)')
RE_ISRC = re.compile(r'(^[A-Z]{2}[A-Z0-9]{3}[0-9]{7}$)')
RE_ISNI = re.compile(r'(^[0-9]{15}[0-9X]$)')
RE_IPI_BASE = re.compile(r'(I-\d{9}-\d)')


def check_ean_digit(ean: str):
    """EAN checksum validation.

    Args:
        ean (str): EAN

    Raises:
        ValidationError
    """
    number = ean[:-1]
    ch = str(
        (10 - sum(
            (3, 1)[i % 2] * int(n)
            for i, n in enumerate(reversed(number))
        )) % 10)
    if ean[-1] != ch:
        raise ValidationError('Invalid EAN.')


def check_iswc_digit(iswc: str, weight: int):
    """ISWC / IPI Base checksum validation.

    Args:
        iswc (str): ISWC or IPI Base #
        weight (int): 1 for ISWC, 2 for IPI Base #

    Raises:
        ValidationError
    """
    digits = re.sub(r'\D', r'', iswc)
    total: int = weight
    for i, d in enumerate(digits[:9]):
        total += (i + 1) * int(d)
    checksum = (10 - total % 10) % 10
    if checksum != int(digits[9]):
        raise ValidationError('Not valid: {}.'.format(iswc))


def check_ipi_digit(all_digits):
    """IPI Name checksum validation.

    Args:
        all_digits (str): IPI Name #

    Raises:
        ValidationError
    """
    digits = all_digits[:-2]
    total = 0
    for i, digit in enumerate(digits):
        total += int(digit) * (10 - i)
    total %= 101
    if total != 0:
        total = (101 - total) % 100
    if '{:02d}'.format(total) != all_digits[-2:]:
        raise ValidationError('Not a valid IPI name number {}.'.format(
            all_digits))


def check_isni_digit(all_digits):
    """ISNI checksum validation.

    Args:
        all_digits (str): ISNI

    Raises:
        ValidationError
    """
    digits = all_digits[:-1]
    total = 0
    for i, digit in enumerate(digits):
        total = 2 * (total + int(digit))
    total = (12 - (total % 11)) % 11
    total = 'X' if total == 10 else str(total)
    if total != all_digits[-1]:
        raise ValidationError('Not a valid ISNI {}.'.format(all_digits))


@deconstructible
class CWRFieldValidator:
    """Validate fields for CWR compliance.

    Attributes:
        field (str): Validation service name of the field being validated
    """

    field = ''

    def __init__(self, field: str):
        """Initialize the validator.

        Args:
            field (str): field name for the field being validated
        """
        self.field = field

    def __call__(self, value):
        """Use custom validation, based on the name of the field.

        Args:
            value (): Input value

        Returns:
            None: If all is well.

        Raises:
            ValidationError: If the value does not pass the validation.
        """

        name = self.field
        if 'title' in name:
            if not re.match(RE_TITLE, value.upper()):
                raise ValidationError('Title contains invalid characters.')
        elif name == 'isni':
            if not re.match(RE_ISNI, value):
                raise ValidationError('Value does not match ISNI format.')
            check_isni_digit(value)
        elif name == 'ean':
            if not value.isnumeric() or len(value) != 13:
                raise ValidationError('Value does not match EAN13 format.')
            check_ean_digit(value)
        elif name == 'iswc':
            if not re.match(RE_ISWC, value):
                raise ValidationError(
                    'Value does not match TNNNNNNNNNC format.')
            check_iswc_digit(value, weight=1)
        elif name == 'isrc':
            if not re.match(RE_ISRC, value):
                raise ValidationError('Value does not match ISRC format.')
        elif 'ipi_name' in name:
            if not value.isnumeric():
                raise ValidationError('Value must be numeric.')
            check_ipi_digit(value)
        elif 'ipi_base' in name:
            if not re.match(RE_IPI_BASE, value):
                raise ValidationError(
                    'Value does not match I-NNNNNNNNN-C format.')
            check_iswc_digit(value, weight=2)
        elif ('name' in name or 'label' in name or name in [
            'cd_identifier', 'saan', 'library']):
            if not re.match(RE_NAME, value.upper()):
                raise ValidationError('Name contains invalid characters.')
