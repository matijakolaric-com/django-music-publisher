from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.deconstruct import deconstructible
import re
import requests


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
VALIDATE = (
    SETTINGS.get('validator_url') and
    SETTINGS.get('generator_url') and
    SETTINGS.get('token'))


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


def get_publisher_dict(pr_society):
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

    Fields are validate in batches in MusicPublisherBase.clean_fields().
    """

    field = ''

    def __init__(self, field):
        self.field = field

    def __call__(self, value):
        return

    # def __eq__(self, other):
    #     return (
    #         isinstance(other, CWRFieldValidator) and
    #         self.field == other.field)


class MusicPublisherBase(models.Model):
    """Abstract class for all top-level classes."""

    class Meta:
        abstract = True

    _cwr = models.BooleanField(
        'CWR-Compliance', editable=False, default=False)

    def validate_fields(self, fields):
        """Validate the fields with an external service."""

        keys = list(fields.keys())
        values = list(fields.values())
        data = {'fields': values}
        try:
            response = requests.post(
                SETTINGS.get('validator_url'),
                headers={'Authorization': 'Token {}'.format(
                    SETTINGS.get('token'))},
                json=data, timeout=10)
        except requests.exceptions.ConnectionError:
            raise ValidationError('Network error', code='service')
        if response.status_code != 200:
            raise ValidationError('Validation failed', code='service')
        errors = {}
        rfields = response.json()['fields']
        for i in range(len(fields)):
            field_name = keys[i]
            field_dict = rfields[i]
            if not field_dict.get('conditionally_valid'):
                errors[field_name] = (
                    field_dict['error'] or 'Unknown Error')
        if errors:
            raise ValidationError(errors, code='invalid')
        self._cwr = True

    def construct_field_dict(self):
        """Construct dictionary appropriate for external validation."""
        fields = {}
        for field in self._meta.fields:
            if not hasattr(self, field.name):
                continue
            value = getattr(self, field.name)
            if not value:
                continue
            for validator in field.validators:
                if isinstance(validator, CWRFieldValidator):
                    fields[field.name] = {
                        'field': validator.field,
                        'value': value}
        return fields

    def clean_fields(self, *args, **kwargs):
        """If external service is used, prepare the data for validation."""

        if not VALIDATE:
            self._cwr = False
            return super().clean_fields(*args, **kwargs)

        fields = self.construct_field_dict()
        try:
            self.validate_fields(fields)
        except ValidationError as ve:
            self._cwr = False
            if 'service' not in ve.args:
                # This means it is an unknown error
                raise
        return super().clean_fields(*args, **kwargs)


class TitleBase(MusicPublisherBase):
    """Abstract class for all classes that have a title."""

    class Meta:
        abstract = True
        ordering = ('-id',)

    title = models.CharField(
        max_length=60, db_index=True, validators=(
            # Original CWR Generator matks all alternate titles as 'AT',
            # so the validation is the sane as in NWR.work_title
            CWRFieldValidator('work_title'),))

    def __str__(self):
        return self.title.upper()


class WorkBase(TitleBase):
    """Abstract class for musical works, most important top-level class."""

    class Meta:
        abstract = True
        verbose_name_plural = '  Works'

    iswc = models.CharField(
        'ISWC', max_length=15, blank=True, null=True, unique=True,
        validators=(CWRFieldValidator('iswc'),))

    def clean_fields(self, *args, **kwargs):
        """Deal with various ways ISWC is written."""
        if self.iswc:
            # CWR holds ISWC in TNNNNNNNNNNC format
            self.iswc = self.iswc.replace('-', '').replace('.', '')
        return super().clean_fields(*args, **kwargs)


class AlbumCDBase(MusicPublisherBase):
    """Abstract class that deals with albums and music liibrary data.

    Note that label and library are set in the settings, so there can
    be only a single 'instance'.

    This limitation is part of this design, other solutions are possible.
    """

    class Meta:
        abstract = True
        verbose_name = 'Album and/or Library CD'
        verbose_name_plural = ' Albums and Library CDs'
        ordering = ('album_title', 'cd_identifier')
        unique_together = (('album_title', 'album_label'),)

    cd_identifier = models.CharField(
        'CD Identifier',
        help_text='This will set the purpose to Library.',
        max_length=15, blank=True, null=True, unique=True, validators=(
            CWRFieldValidator('cd_identifier'),))
    release_date = models.DateField(
        help_text='Can be overridden by recording data.',
        blank=True, null=True)
    album_title = models.CharField(
        max_length=60, blank=True, unique=True, validators=(
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
        if self.cd_identifier:
            return SETTINGS.get('library')

    def clean(self):
        """Make sure that either cd_identifier or album are used.

        Also, enforce some common sense, although it is not strictly
        required by CWR specs.
        """

        if not self.cd_identifier and not self.album_title:
            raise ValidationError({
                'cd_identifier': 'Required if Album Title is not set.',
                'album_title': 'Required if CD Identifier is not set.'})
        if (self.ean or self.release_date) and not self.album_title:
            raise ValidationError({
                'album_title': 'Required if EAN or release date is set.'})


class FirstRecordingBase(MusicPublisherBase):
    """Holds data on first recording.

    Note that the limitation of just one REC record per work has been
    removed in the specs, but some societies still complain about it,
    so only a single instance is allowed."""

    class Meta:
        abstract = True
        verbose_name_plural = 'First recording of the work'

    isrc = models.CharField(
        'ISRC', max_length=15, blank=True, null=True, unique=True,
        validators=(CWRFieldValidator('isrc'),))
    release_date = models.DateField(blank=True, null=True)
    duration = models.TimeField(blank=True, null=True)
    catalog_number = models.CharField(
        max_length=18, blank=True, null=True, unique=True, validators=(
            CWRFieldValidator(
                'first_release_catalog_number'),))

    def clean_fields(self, *args, **kwargs):
        if self.isrc:
            # Removing all characters added for readability
            self.isrc = self.isrc.replace('-', '').replace('.', '')
        return super().clean_fields(*args, **kwargs)


class PersonBase(models.Model):
    """Base class for all classes that contain people with first and last name.
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
    class Meta:
        abstract = True

    ipi_name = models.CharField(
        'IPI Name #', max_length=11, blank=True, null=True, unique=True,
        validators=(CWRFieldValidator('writer_ipi_name'),))
    ipi_base = models.CharField(
        'IPI Base #', max_length=15, blank=True, null=True,
        validators=(CWRFieldValidator('writer_ipi_base'),))
    pr_society = models.CharField(
        'Performing Rights Society', max_length=3, blank=True, null=True,
        validators=(CWRFieldValidator('writer_pr_society'),),
        choices=SOCIETIES)
    saan = models.CharField(
        'Society-assigned agreement number',
        help_text='Use this field for general agreements only.',
        validators=(CWRFieldValidator('saan'),),
        max_length=14, blank=True, null=True, unique=True)

    _can_be_controlled = models.BooleanField(editable=False, default=False)
    generally_controlled = models.BooleanField(
        'General Agreement', default=False)
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
    """Concrete class for performing artists."""
    class Meta:
        abstract = True
        verbose_name = 'Performing Artist'
        verbose_name_plural = ' Performing Artists'


class WriterBase(PersonBase, IPIBase, MusicPublisherBase):
    """Base class for writers, the second most important top-level class."""

    class Meta:
        abstract = True
        ordering = ('last_name', 'first_name', 'ipi_name')
        verbose_name_plural = ' Writers'

    _cwr = models.BooleanField(
        'CWR-Compliance', editable=False, default=False)

    def get_publisher_dict(self):
        return get_publisher_dict(self.pr_society)

    def __str__(self):
        name = super().__str__()
        if self.generally_controlled:
            return name + ' (*)'
        return name
