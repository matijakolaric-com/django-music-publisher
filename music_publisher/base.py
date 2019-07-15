"""Contains base (abstract) classes used in :mod:`.models`

Attributes:
    CAN_NOT_BE_CONTROLLED_MSG (str): \
        Error message when required fields are missing
    CONTROLLED_WRITER_REQUIRED_FIELDS (list): List of required fields
    ENFORCE_IPI_NAME (bool): \
        Is IPI Name # a required field for controlled writers?
    ENFORCE_PR_SOCIETY (bool): \
        Is PR Society Code a required field for controlled writers?
    ENFORCE_PUBLISHER_FEE (bool): \
        Is Publisher Fee a required field for controlled writers?
    ENFORCE_SAAN (bool): \
        Is Society-assigned agreement number a required field for controlled \
        writers?
    NAMES_CHARS (str): Characters allowed in CWR names
    RE_IPI_BASE (str): Regex pattern for IPI Base
    RE_ISNI (str): Regex pattern for ISNI
    RE_ISRC (str): Regex pattern for ISRC (lax)
    RE_ISWC (str): Regex pattern for ISWC
    RE_NAME (str): Regex pattern for CWR names
    RE_TITLE (str): Regex pattern for CWR titles
    TITLES_CHARS (str): Characters allowed in CWR titles
"""
from datetime import date

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.deconstruct import deconstructible
import re
import warnings

SETTINGS = settings.MUSIC_PUBLISHER_SETTINGS

ENFORCE_SAAN = SETTINGS.get('enforce_saan')
ENFORCE_PUBLISHER_FEE = SETTINGS.get('enforce_publisher_fee')
ENFORCE_PR_SOCIETY = SETTINGS.get('enforce_pr_society')
ENFORCE_IPI_NAME = SETTINGS.get('enforce_ipi_name')

CONTROLLED_WRITER_REQUIRED_FIELDS = ['Last Name']
if ENFORCE_PR_SOCIETY:
    CONTROLLED_WRITER_REQUIRED_FIELDS.append('Performing Rights Society')
if ENFORCE_IPI_NAME:
    CONTROLLED_WRITER_REQUIRED_FIELDS.append('IPI Name #')

CAN_NOT_BE_CONTROLLED_MSG = (
    'Unsufficient data for a controlled writer, required fields are: {}.'
).format(', '.join(CONTROLLED_WRITER_REQUIRED_FIELDS))

# Default only has 18 societies from 12 countries. These are G7, without Japan,
# where we have no information about CWR use and all other societies covered
# by ICE Services
# If you need to add some, do it in the settings, not here.

try:
    SOCIETIES = settings.MUSIC_PUBLISHER_SOCIETIES
except AttributeError:
    SOCIETIES = [
        ('55', 'SABAM, Belgium'),

        ('101', 'SOCAN, Canada'),
        ('88', 'CMRRA, Canada'),

        ('40', 'KODA, Denmark'),

        ('89', 'TEOSTO, Finland'),

        ('58', 'SACEM, France'),

        ('35', 'GEMA, Germany'),

        ('74', 'SIAE, Italy'),

        ('23', 'BUMA, Netherlands'),
        ('78', 'STEMRA, Netherlands'),

        ('90', 'TONO, Norway'),

        ('79', 'STIM, Sweden'),

        ('52', 'PRS, United Kingdom'),
        ('44', 'MCPS, United Kingdom'),

        ('10', 'ASCAP, United States'),
        ('21', 'BMI, United States'),
        ('71', 'SESAC Inc., United States'),
        ('34', 'HFA, United States'),

        ('319', 'ICE Services, Administrative Agency'),
        ('707', 'Musicmark, Administrative Agency')]

TITLES_CHARS = re.escape(
    r"!\"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\]^_`{}~£€"
)
NAMES_CHARS = re.escape(
    r"!#$%&'()+-./0123456789?@ABCDEFGHIJKLMNOPQRSTUVWXYZ`"
)

RE_TITLE = r'(^[{0}][ {0}]*$)'.format(TITLES_CHARS)
RE_NAME = r'(^[{0}][ {0}]*$)'.format(NAMES_CHARS)
RE_ISWC = re.compile(r'(^T\d{10}$)')
RE_ISRC = re.compile(r'(^[A-Z]{2}[A-Z0-9]{3}[0-9]{7}$)')
RE_ISNI = re.compile(r'(^[0-9]{15}[0-9X]$)')
RE_IPI_BASE = re.compile(r'(I-\d{9}-\d)')


def check_ean_digit(ean):
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


def check_iswc_digit(iswc, weight):
    """ISWC / IPI Base checksum validation.

    Args:
        iswc (str): ISWC or IPI Base #
        weight (int): 1 for ISWC, 2 for IPI Base #

    Raises:
        ValidationError
    """
    digits = re.sub(r'\D', r'', iswc)
    sum = weight
    for i, d in enumerate(digits[:9]):
        sum += (i + 1) * int(d)
    checksum = (10 - sum % 10) % 10
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
    sum = 0
    for i, digit in enumerate(digits):
        sum += int(digit) * (10 - i)
    sum = sum % 101
    if sum != 0:
        sum = (101 - sum) % 100
    if '{:02d}'.format(sum) != all_digits[-2:]:
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
    sum = 0
    for i, digit in enumerate(digits):
        sum = 2 * (sum + int(digit))
    sum = (12 - (sum % 11)) % 11
    sum = 'X' if sum == 10 else str(sum)
    if sum != all_digits[-1]:
        raise ValidationError('Not a valid ISNI {}.'.format(all_digits))


@deconstructible
class CWRFieldValidator:
    """Validate fields for CWR compliance.

    Attributes:
        field (str): Validation service name of the field being validated
    """

    field = ''

    def __init__(self, field):
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


class TitleBase(models.Model):
    """Abstract class for all classes that have a title.

    Attributes:
        title (django.db.models.CharField): Title, used in work title,
            alternate title, etc.
    """

    class Meta:
        abstract = True

    title = models.CharField(
        max_length=60, db_index=True, validators=(
            # Original CWR Generator marks all alternate titles as 'AT',
            # so the validation is the same as in NWR.work_title
            CWRFieldValidator('work_title'),))

    def __str__(self):
        return self.title.upper()


class PersonBase(models.Model):
    """Base class for all classes that contain people with first and last name.

    Attributes:
        first_name (django.db.models.CharField): First Name
        last_name (django.db.models.CharField): Last Name
    """

    class Meta:
        abstract = True

    first_name = models.CharField(
        max_length=30, blank=True,
        validators=(CWRFieldValidator('artist_first_name'),))
    last_name = models.CharField(
        max_length=45, db_index=True,
        validators=(CWRFieldValidator('artist_last_name'),))

    def __str__(self):
        if self.first_name:
            return '{0.first_name} {0.last_name}'.format(self).upper()
        return self.last_name.upper()


class IPIBase(models.Model):
    """Abstract base for all objects containing IPI numbers.

    Attributes:
        generally_controlled (django.db.models.BooleanField):
            General agreement (renamed in verbose_name)
        ipi_base (django.db.models.CharField): IPI Base Number
        ipi_name (django.db.models.CharField): IPI Name Number
        pr_society (django.db.models.CharField):
            Performing Rights Society Code
        publisher_fee (django.db.models.DecimalField): Publisher Fee
        saan (django.db.models.CharField):
            Society-assigned agreement number, in this context it is used for
            general agreements, for specific agreements use
            :attr:`.models.WriterInWork.saan`.
        _can_be_controlled (django.db.models.BooleanField):
            used to determine if there is enough data for a writer
            to be controlled.
        generally_controlled (django.db.models.BooleanField):
            flags if a writer is generally controlled (in all works)
        publisher_fee (django.db.models.DecimalField):
            this field is used in calculating publishing fees
    """

    class Meta:
        abstract = True

    ipi_name = models.CharField(
        'IPI Name #', max_length=11, blank=True, null=True, unique=True,
        validators=(CWRFieldValidator('writer_ipi_name'),))
    ipi_base = models.CharField(
        'IPI Base #', max_length=15, blank=True, null=True,
        validators=(CWRFieldValidator('writer_ipi_base'),))
    pr_society = models.CharField(
        'Performing rights society', max_length=3, blank=True, null=True,
        validators=(CWRFieldValidator('writer_pr_society'),),
        choices=SOCIETIES)
    saan = models.CharField(
        'Society-assigned agreement number',
        help_text='Use this field for general agreements only.',
        validators=(CWRFieldValidator('saan'),),
        max_length=14, blank=True, null=True, unique=True)

    _can_be_controlled = models.BooleanField(editable=False, default=False)
    generally_controlled = models.BooleanField(
        'General agreement', default=False)
    publisher_fee = models.DecimalField(
        max_digits=5, decimal_places=2, blank=True, null=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text='Percentage of royalties kept by the publisher')

    def clean_fields(self, *args, **kwargs):
        """
        Data cleanup, allowing various import formats to be converted into
        consistently formatted data.
        """
        if self.saan:
            self.saan = self.saan.upper()  # only in CWR, uppercase anyway
        if self.ipi_name:
            self.ipi_name = self.ipi_name.rjust(11, '0')
        if self.ipi_base:
            self.ipi_base = self.ipi_base.replace('.', '')
            self.ipi_base = re.sub(
                r'(I).?(\d{9}).?(\d)', r'\1-\2-\3', self.ipi_base)
        return super().clean_fields(*args, **kwargs)

    def clean(
            self,
            enforce_ipi_name=ENFORCE_IPI_NAME,
            enforce_pr_society=ENFORCE_PR_SOCIETY,
            enforce_saan=ENFORCE_SAAN,
            enforce_publisher_fee=ENFORCE_PUBLISHER_FEE,
            error_msg=CAN_NOT_BE_CONTROLLED_MSG):
        """Clean with a lot of arguments.

        In DMP they come from settings, but in other (closed source) solutions
        that use this code, these values are set dynamically.


        Args:
            enforce_ipi_name (bool, optional):
                Makes IPI Name # required if controlled
            enforce_pr_society (bool, optional):
                Makes PR Society code required if controlled
            enforce_saan (bool, optional):
                Makes SAAN required if controlled
            enforce_publisher_fee (bool, optional):
                Makes Publisher fee required if controlled
            error_msg (str, optional):
                Error Message to show if required fields are not filled out
        """

        self._can_be_controlled = True
        if enforce_ipi_name:
            self._can_be_controlled &= bool(self.ipi_name)
        if enforce_pr_society:
            self._can_be_controlled &= bool(self.pr_society)
        d = {}
        if not self.generally_controlled:
            if self.saan:
                d['saan'] = 'Only for a general agreement.'
            if self.publisher_fee:
                d['publisher_fee'] = 'Only for a general agreement.'
        else:
            if not self._can_be_controlled:
                d['generally_controlled'] = error_msg
            if enforce_saan and not self.saan:
                d['saan'] = 'This field is required.'
            if enforce_publisher_fee and not self.publisher_fee:
                d['publisher_fee'] = 'This field is required.'
        if d:
            raise ValidationError(d)
