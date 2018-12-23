"""Contains base (abstract) classes used in :mod:`.models`

Attributes:
    CAN_NOT_BE_CONTROLLED_MSG (str): \
        Error message when required fields are missing
    CONTROLLED_WRITER_REQUIRED_FIELDS (list): List of required fields
    ENFORCE_IPI_NAME (bool): \
        Is IPI Name # a required field for controlled writers?
    ENFORCE_PR_SOCIETY (TYPE): \
        Is PR Society Code a required field for controlled writers?
    ENFORCE_PUBLISHER_FEE (TYPE): \
        Is Publisher Fee a required field for controlled writers?
    ENFORCE_SAAN (TYPE): \
        Is Society-assigned agreement number a required field for controlled \
        writers?
    WORK_ID_PREFIX (TYPE): Prefix for Submitter Work ID, which is numerical
"""

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.deconstruct import deconstructible
import re
import warnings


# SETTINGS, strictly not required, except for validation and CWR generation

if hasattr(settings, 'MUSIC_PUBLISHER_SETTINGS'):
    SETTINGS = settings.MUSIC_PUBLISHER_SETTINGS
else:
    SETTINGS = {}

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
WORK_ID_PREFIX = SETTINGS.get('work_id_prefix') or ''


# Default only has 18 societies from 12 countries. These are G7, without Japan,
# where we have no information about CWR use and all other societies covered
# by ICE Services
# If you need to add some, do it in the settings, not here.

try:
    SOCIETIES = settings.MUSIC_PUBLISHER_SOCIETIES
except AttributeError:
    SOCIETIES = [
        ('055', 'SABAM, Belgium'),

        ('101', 'SOCAN, Canada'),
        ('088', 'CMRRA, Canada'),

        ('040', 'KODA, Denmark'),

        ('089', 'TEOSTO, Finland'),

        ('058', 'SACEM, France'),

        ('035', 'GEMA, Germany'),

        ('074', 'SIAE, Italy'),

        ('023', 'BUMA, Netherlands'),
        ('078', 'STEMRA, Netherlands'),

        ('090', 'TONO, Norway'),

        ('079', 'STIM, Sweden'),

        ('052', 'PRS, United Kingdom'),
        ('044', 'MCPS, United Kingdom'),

        ('010', 'ASCAP, United States'),
        ('021', 'BMI, United States'),
        ('071', 'SESAC Inc., United States'),
        ('034', 'HFA, United States'),

        ('319', 'ICE Services, Administrative Agency'),
        ('707', 'Musicmark, Administrative Agency')]


TITLES_CHARS = re.escape(
    "!\"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\]^_`{}~£€"
)

NAMES_CHARS = re.escape(
    "!#$%&'()+-./0123456789?@ABCDEFGHIJKLMNOPQRSTUVWXYZ`"
)

RE_TITLE = r'(^[{0}][ {0}]+$)'.format(TITLES_CHARS)

RE_NAME = r'(^[{0}][ {0}]+$)'.format(NAMES_CHARS)

RE_ISWC = re.compile(r'(^T\d{10}$)')

RE_ISRC = re.compile(r'(^[A-Z]{2}[A-Z0-9]{3}[0-9]{7}$)')

RE_ISNI = re.compile(r'(^[0-9]{15}[0-9X]$)')

RE_IPI_BASE = re.compile(r'(I-\d{9}-\d)')


def check_ean_digit(ean):
    number = ean[:-1]
    ch = str(
        (10 - sum(
            (3, 1)[i % 2] * int(n)
            for i, n in enumerate(reversed(number))
        )) % 10)
    if ean[-1] != ch:
        raise ValidationError('Invalid EAN.')


def check_iswc_digit(iswc, weight):
    digits = re.sub(r'\D', r'', iswc)
    sum = weight
    for i, d in enumerate(digits[:9]):
        sum += (i + 1) * int(d)
    checksum = (10 - sum % 10) % 10
    if checksum != int(digits[9]):
        raise ValidationError('Not a valid ISWC {}.'.format(iswc))


def check_ipi_digit(all_digits):
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
    digits = all_digits[:-1]
    sum = 0
    for i, digit in enumerate(digits):
        sum = 2 * (sum + int(digit))
    sum = (12 - (sum % 11)) % 11
    sum = 'X' if sum == 10 else str(sum)
    if sum != all_digits[-1]:
        raise ValidationError('Not a valid ISNI {}.'.format(all_digits))


def get_publisher_dict(pr_society):
    """Return publisher settings based on society code.

    Args:
        pr_society (str): CISAC Society code, 3-digit format with leading zero.

    Returns:
        dict: Data on publisher in question, default one if not found.
    """

    mapping = {'010': 'ASCAP', '021': 'BMI', '071': 'SESAC'}
    key = mapping.get(pr_society)
    us_publisher_override = SETTINGS.get('us_publisher_override', {})
    pub = us_publisher_override.get(key)
    if pub:
        pub['pr_society'] = 'pr_society'
        return pub
    return SETTINGS


@deconstructible
class CWRFieldValidator:
    """Validate fields for CWR compliance.

    This validator that does not really validate, it just sets the correct
    field type.
    Fields are validated in batches in :meth:`MusicPublisherBase.clean_fields`.

    Attributes:
        field (str): Validation service name of the field being validated
    """

    field = ''

    def __init__(self, field):
        """Initialize the validator.

        Args:
            field (str): Validation service name of the field being validated
        """
        self.field = field

    def __call__(self, value):
        """Use custom validation, based on the name of the field.

        Args:
            value (): Input valie

        Returns:
            None: If all is well.

        Raises:
            ValidationError: If the valie does not pass the validation.
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
                'cd_identifier', 'saan']):
            if not re.match(RE_NAME, value.upper()):
                raise ValidationError('Name contains invalid characters.')


class MusicPublisherBase(models.Model):
    """Abstract class for all top-level classes.

    Not used any more, kept for backward-compatibility.
    """

    class Meta:
        abstract = True


class TitleBase(MusicPublisherBase):
    """Abstract class for all classes that have a title.

    Attributes:
        title (django.db.models.CharField): Title, used in work title,
            alternate title, etc.
    """

    class Meta:
        abstract = True
        ordering = ('-id',)

    title = models.CharField(
        max_length=60, db_index=True, validators=(
            # Original CWR Generator marks all alternate titles as 'AT',
            # so the validation is the same as in NWR.work_title
            CWRFieldValidator('work_title'),))

    def __str__(self):
        return self.title.upper()


class WorkBase(TitleBase):
    """Abstract class for musical works, most important top-level class.

    Attributes:
        iswc (django.db.models.CharField):
            ISWC - International Standard Work Code
    """

    class Meta:
        abstract = True
        verbose_name_plural = '  Works'

    iswc = models.CharField(
        'ISWC', max_length=15, blank=True, null=True, unique=True,
        validators=(CWRFieldValidator('iswc'),))

    original_title = models.CharField(
        max_length=60, db_index=True, blank=True,
        help_text='Use only for modification of existing works.',
        validators=(
            CWRFieldValidator('work_title'),))

    def is_modification(self):
        if self.id:
            return bool(self.original_title)

    def clean_fields(self, *args, **kwargs):
        """Deal with various ways ISWC is written.
        """
        if self.iswc:
            # CWR 2.x holds ISWC in TNNNNNNNNNC format
            # CWR 3.0 holds ISWC in T-NNNNNNNNN-C format
            # sometimes it comes in T-NNN.NNN.NNN-C format
            self.iswc = self.iswc.replace('-', '').replace('.', '')
        return super().clean_fields(*args, **kwargs)


class AlbumCDBase(MusicPublisherBase):
    """Abstract class that deals with albums and music liibrary data.

    Note that label and library are set in the settings, serving as defualts.

    Attributes:
        album_label (django.db.models.CharField): Album Label
        album_title (django.db.models.CharField): Album Title
        cd_identifier (django.db.models.CharField):
            CD Indetifier (for Library works)
        ean (django.db.models.CharField): Album (or other release) EAN
        release_date (django.db.models.DateField):
            The date of the album release, can be overridden in recordings
    """

    class Meta:
        abstract = True
        verbose_name = 'Album and/or Library CD'
        verbose_name_plural = ' Albums and Library CDs'
        ordering = ('album_title', 'cd_identifier')

    cd_identifier = models.CharField(
        'CD identifier',
        help_text='This will set the purpose to Library.',
        max_length=15, blank=True, null=True, unique=True, validators=(
            CWRFieldValidator('cd_identifier'),))
    release_date = models.DateField(
        help_text='Can be overridden by recording data.',
        blank=True, null=True)
    album_title = models.CharField(
        max_length=60, blank=True, null=True, unique=True, validators=(
            CWRFieldValidator('first_album_title'),))
    ean = models.CharField(
        'EAN',
        max_length=13, blank=True, null=True, unique=True, validators=(
            CWRFieldValidator('ean'),))
    album_label = models.CharField(
        default=SETTINGS.get('label') or '',
        max_length=60, blank=True, validators=(
            CWRFieldValidator('first_album_label'),))

    def __str__(self):
        if self.cd_identifier and self.album_title:
            return '{} ({})'.format(
                self.album_title or '', self.cd_identifier).upper()
        return (self.album_title or self.cd_identifier).upper()

    @property
    def library(self):
        """Return Library name if cd_identifier is present

        Returns:
            str: Name of the library, or None
        """
        if self.cd_identifier:
            return SETTINGS.get('library')

    def clean(self):
        if not self.cd_identifier and not self.album_title:
            raise ValidationError({
                'cd_identifier': 'Required if Album Title is not set.',
                'album_title': 'Required if CD Identifier is not set.'})
        if (self.ean or self.release_date) and not self.album_title:
            raise ValidationError({
                'album_title': 'Required if EAN or release date is set.'})


class RecordingBase(MusicPublisherBase):
    """Holds data on first recording.

    Note that the CWR 2.x limitation of just one REC record per work has been
    removed in the specs, but some societies still complain about it,
    so only a single instance is allowed.

    Attributes:
        duration (django.db.models.TimeField): Recording Duration
        isrc (django.db.models.CharField):
            International Standard Recording Code
        record_label (django.db.models.CharField): Record Label
        release_date (django.db.models.DateField): Recording Release Date
    """

    class Meta:
        abstract = True
        verbose_name_plural = 'First recording of the work'

    release_date = models.DateField(blank=True, null=True)
    duration = models.TimeField(blank=True, null=True)
    isrc = models.CharField(
        'ISRC', max_length=15, blank=True, null=True, unique=True,
        validators=(CWRFieldValidator('isrc'),))
    record_label = models.CharField(
        default=SETTINGS.get('label') or '',
        max_length=60, blank=True, validators=(
            CWRFieldValidator('first_album_label'),))

    def clean_fields(self, *args, **kwargs):
        if self.isrc:
            # Removing all characters added for readability
            self.isrc = self.isrc.replace('-', '').replace('.', '')
        return super().clean_fields(*args, **kwargs)


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
        if self.saan:
            self.saan = self.saan.upper()
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
        if not self._can_be_controlled and self.generally_controlled:
            raise ValidationError({
                'generally_controlled': error_msg})
        if self.saan and not self.generally_controlled:
            raise ValidationError({
                'saan': 'Only for a general agreement.'})
        if self.publisher_fee and not self.generally_controlled:
            raise ValidationError({
                'publisher_fee': 'Only for a general agreement.'})
        if self.generally_controlled and enforce_saan and not self.saan:
            raise ValidationError({
                'saan': 'This field is required.'})
        if (self.generally_controlled and enforce_publisher_fee and
                not self.publisher_fee):
            raise ValidationError({
                'publisher_fee': 'This field is required.'})


class ArtistBase(PersonBase, MusicPublisherBase):
    """Concrete class for performing artists.

    Attributes:
        isni (django.db.models.CharField):
            International Standard Name Identifier
    """
    class Meta:
        abstract = True
        verbose_name = 'Performing Artist'
        verbose_name_plural = ' Performing Artists'

    isni = models.CharField(
        'ISNI',
        max_length=16, blank=True, null=True, unique=True,
        validators=(CWRFieldValidator('isni'),))

    def clean_fields(self, *args, **kwargs):
        if self.isni:
            self.isni = self.isni.rjust(16, '0').upper()
        return models.Model.clean_fields(self, *args, **kwargs)


class WriterBase(PersonBase, IPIBase, MusicPublisherBase):
    """Base class for writers, the second most important top-level class.
    """

    class Meta:
        abstract = True
        ordering = ('last_name', 'first_name', 'ipi_name')
        verbose_name_plural = ' Writers'

    def get_publisher_dict(self):
        """Return data on publisher.

        This is the default publisher, except in cases when the writer
        is affiliated with one of the US PROs and this publisher's data
        is set in 'us_publisher_override' of the MUSIC_PUBLISHER_SETTINGS.

        Returns:
            dict: Data on publisher
        """
        return get_publisher_dict(self.pr_society)

    def __str__(self):
        name = super().__str__()
        if self.generally_controlled:
            return name + ' (*)'
        return name
