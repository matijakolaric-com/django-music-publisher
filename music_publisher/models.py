from collections import OrderedDict, defaultdict
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import models
from django.utils.deconstruct import deconstructible
import re
import requests


# SETTINGS and few other things, that will go to Client class

SETTINGS = settings.MUSIC_PUBLISHER_SETTINGS
VALIDATE = (
    SETTINGS.get('validator_url') and
    SETTINGS.get('generator_url') and
    SETTINGS.get('token'))


# Defaults only have 12 societies from 6 countries. These are G7, without Japan

try:
    SOCIETIES = settings.MUSIC_PUBLISHER_SOCIETIES
except AttributeError:
    SOCIETIES = [
        ('101', 'SOCAN, Canada'),
        ('088', 'CMRRA, Canada'),

        ('058', 'SACEM, France'),
        ('068', 'SDRM, France'),

        ('035', 'GEMA, Germany'),

        ('074', 'SIAE, Italy'),

        ('052', 'PRS, United Kingdom'),
        ('044', 'MCPS, United Kingdom'),


        ('010', 'ASCAP, United States'),
        ('021', 'BMI, United States'),
        ('071', 'SESAC Inc., United States'),
        ('034', 'HFA, United States')]


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
    """Validate fields for CWR complance.

    This validator that does not really validate, it just sets the correct
    field type.

    Fields are validate in batches in MusicPublisherBase.clean_fields().
    """

    field = ''

    def __init__(self, field):
        self.field = field

    def __call__(self, value):
        return

    def __eq__(self, other):
        return (
            isinstance(other, CWRFieldValidator) and
            self.field == other.field)


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
            if field_dict.get('conditionally_valid'):
                pass  # maybe replace by a recommended value?
            else:
                errors[field_name] = (
                    field_dict['error'] or 'Unknown Error')
        if errors:
            raise ValidationError(errors, code='invalid')
        self._cwr = True

    def construct_field_dict(self):
        """Construct dictionary appropriate for external validation."""
        fields = {}
        for field in self._meta.fields:
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

    cd_identifier = models.CharField(
        'CD Identifier',
        help_text='This will set the purpose to Library.',
        max_length=15, blank=True, null=True, unique=True, validators=(
            CWRFieldValidator('cd_identifier'),))
    release_date = models.DateField(
        help_text='Can be overridden by recording data.',
        blank=True, null=True)
    album_title = models.CharField(
        help_text='This will set the label.',
        max_length=60, blank=True, null=True, unique=True, validators=(
            CWRFieldValidator('first_album_title'),))
    ean = models.CharField(
        'EAN',
        max_length=13, blank=True, null=True, unique=True, validators=(
            CWRFieldValidator('ean'),))

    def __str__(self):
        if self.cd_identifier and self.album_title:
            return '{} ({})'.format(
                self.album_title or '', self.cd_identifier).upper()
        return (self.album_title or self.cd_identifier).upper()

    @property
    def album_label(self):
        if self.album_title:
            return SETTINGS.get('label')

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


class PersonBase(MusicPublisherBase):
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


class WriterBase(PersonBase):
    """Base class for writers, the second most important top-level class."""

    class Meta:
        abstract = True
        ordering = ('last_name', 'first_name', 'ipi_name')
        verbose_name_plural = ' Writers'

    ipi_name = models.CharField(
        'IPI Name #', max_length=11, blank=True, null=True, unique=True,
        help_text='Required for a controlled writer',
        validators=(CWRFieldValidator('writer_ipi_name'),))
    ipi_base = models.CharField(
        'IPI Base #', max_length=15, blank=True, null=True,
        validators=(CWRFieldValidator('writer_ipi_base'),))
    pr_society = models.CharField(
        'Performing Rights Society', max_length=3, blank=True, null=True,
        help_text='Required for a controlled writer',
        validators=(CWRFieldValidator('writer_pr_society'),),
        choices=SOCIETIES)
    saan = models.CharField(
        'Society-assigned agreement number',
        help_text='Use this field for general agreements only.',
        validators=(CWRFieldValidator('saan'),),
        max_length=14, blank=True, null=True, unique=True)

    _can_be_controlled = models.BooleanField(editable=False, default=False)
    generally_controlled = models.BooleanField(default=False)

    def get_publisher_dict(self):
        return get_publisher_dict(self.pr_society)

    def clean_fields(self, *args, **kwargs):
        if self.ipi_base:
            self.ipi_base = self.ipi_base.replace('.', '')
            self.ipi_base = re.sub(
                r'(I).?(\d{9}).?(\d)', r'\1-\2-\3', self.ipi_base)
        return super().clean_fields(*args, **kwargs)

    def clean(self):
        self._can_be_controlled = bool(
            self.last_name and self.ipi_name and self.pr_society)
        if not self._can_be_controlled and self.saan:
            raise ValidationError({
                'saan': 'Last name, IPI name # and PR Society must be set.'})
        if not self._can_be_controlled and self.generally_controlled:
            raise ValidationError({
                'generally_controlled':
                    'Last name, IPI name # and PR Society must be set.'})
        if self.saan and not self.generally_controlled:
            raise ValidationError({
                'saan': 'Only for generally controlled writers.'})

    @property
    def is_us_writer(self):
        return self.pr_society in ['010', '021', '071']

    def __str__(self):
        name = super().__str__()
        if self.generally_controlled:
            return name + ' (*)'
        return name


class Work(WorkBase):
    """Concrete class, with references to foreign objects.
    """

    artists = models.ManyToManyField('Artist', through='ArtistInWork')
    writers = models.ManyToManyField('Writer', through='WriterInWork')
    last_change = models.DateTimeField(
        'Last Edited', editable=False, null=True)

    @property
    def json(self):
        """Create data structure that can be serielized as JSON.

        Note that serialization is not performed here.
        """

        data = OrderedDict()
        data['work_title'] = self.title
        if self.iswc:
            data['iswc'] = self.iswc
        data['writers'] = [wiw.json for wiw in self.writerinwork_set.all()]
        data['alternate_titles'] = [
            at.json for at in self.alternatetitle_set.all()]
        data['artists'] = [
            aiw.artist.json for aiw in self.artistinwork_set.all()]
        try:
            data.update(self.firstrecording.json)
        except ObjectDoesNotExist:
            pass
        return {self.work_id: data}

    @property
    def work_id(self):
        return '{:06}'.format(self.id)

    def __str__(self):
        return '{} {} ({})'.format(
            self.work_id,
            self.title,
            ' / '.join(w.last_name.upper() for w in self.writers.all()))


class AlternateTitle(TitleBase):
    """Conrete class for alternate titles."""

    work = models.ForeignKey(Work, on_delete=models.CASCADE)

    class Meta:
        unique_together = (('work', 'title'),)

    @property
    def json(self):
        return {'alternate_title': self.title}


class AlbumCD(AlbumCDBase):
    """Conrete class for album / CD."""
    pass


class FirstRecording(FirstRecordingBase):
    """Concrete class for first recording."""

    work = models.OneToOneField(Work, on_delete=models.CASCADE)
    album_cd = models.ForeignKey(
        AlbumCD, on_delete=models.PROTECT, blank=True, null=True,
        verbose_name='Album / Library CD')

    def __str__(self):
        return str(self.work)

    @property
    def json(self):
        """Create serializable data structure, including album/cd data.
        """
        data = OrderedDict()
        if self.duration:
            data['first_release_duration'] = self.duration.strftime('%H%M%S')
        if self.isrc:
            data['isrc'] = self.isrc
        if self.catalog_number:
            data['first_release_catalog_number'] = self.catalog_number
        if self.album_cd:
            if self.album_cd.release_date:
                data['first_release_date'] = (
                    self.album_cd.release_date.strftime('%Y-%m-%d'))
            data.update({
                'first_album_title': self.album_cd.album_title or '',
                'first_album_label': self.album_cd.album_label or '',
                'ean': self.album_cd.ean or ''})
        if self.release_date:
            data['first_release_date'] = self.release_date.strftime('%Y-%m-%d')
        if self.album_cd and self.album_cd.library:
            data.update({
                'library': self.album_cd.library,
                'cd_identifier': self.album_cd.cd_identifier})
        return data


class Artist(PersonBase):
    """Concrete class for performing artists."""
    class Meta:
        verbose_name = 'Performing Artist'
        verbose_name_plural = ' Performing Artists'

    @property
    def json(self):
        return {
            'artist_last_name': self.last_name,
            'artist_first_name': self.first_name}


class ArtistInWork(models.Model):
    """Intermediary class in M2M relationship.

    It is always better to write them explicitely.
    """

    work = models.ForeignKey(Work, on_delete=models.CASCADE)
    artist = models.ForeignKey(Artist, on_delete=models.PROTECT)

    class Meta:
        verbose_name = 'Artist Performing Work'
        verbose_name_plural = 'Artists Performing Work'
        unique_together = (('work', 'artist'),)

    def __str__(self):
        return str(self.artist)


class Writer(WriterBase):
    """Concrete class for writers."""

    def clean(self, *args, **kwargs):
        """Controlled writer requires more data, so once a writer is in
        that role, it is not allowed to remove required data."""

        super().clean(*args, **kwargs)
        if self.pk is None or self._can_be_controlled:
            return
        if self.writerinwork_set.filter(controlled=True).exists():
            raise ValidationError(
                'This writer is controlled in at least one work, '
                'required are: Last name, IPI Name # and Performing '
                'Rights Society.')


class WriterInWork(models.Model):
    """Intermediary class in M2M relationship with few additional fields.

    Please note that in some societies, SAAN is a required field.
    Capacity is limited to roles by original writers."""

    class Meta:
        verbose_name_plural = 'Writers in Work'
        unique_together = (('work', 'writer'),)

    work = models.ForeignKey(Work, on_delete=models.CASCADE)
    writer = models.ForeignKey(
        Writer, on_delete=models.PROTECT,
        blank=True, null=True)
    saan = models.CharField(
        'Society-assigned agreement number',
        help_text='Use this field for specific agreements only.',
        max_length=14, blank=True, null=True,
        validators=(CWRFieldValidator('saan'),),)
    controlled = models.BooleanField(default=False)
    relative_share = models.DecimalField(max_digits=5, decimal_places=2)
    capacity = models.CharField(max_length=2, blank=True, choices=(
        ('C ', 'Composer'),
        ('A ', 'Lyricist'),
        ('CA', 'Composer&Lyricist'),
    ))

    def __str__(self):
        return str(self.writer)

    def clean(self):
        """Make sure that contrlled writers have all the required data."""
        if (self.writer and self.writer.generally_controlled and
                not self.controlled):
            raise ValidationError({
                'controlled': 'Must be set for a generally controlled writer.'
            })
        if self.controlled and not self.capacity:
            raise ValidationError({
                'capacity': 'Must be set for a controlled writer.'
            })
        if self.controlled and not self.writer:
            raise ValidationError({
                'writer': 'Must be set for a controlled writer.'
            })
        if (self.controlled and not self.writer._can_be_controlled):
            raise ValidationError(
                'Writer \'{}\' is controlled in at least one work, '
                'required are: Last name, IPI Name # and Performing '
                'Rights Society.'.format(self.writer))

    @property
    def json(self):
        data = OrderedDict()
        if self.writer:
            data['writer_id'] = (
                self.writer.ipi_name.rjust(11, '0')[0:9]
                if self.writer.ipi_name else '')
            data['writer_last_name'] = self.writer.last_name
            data['writer_first_name'] = self.writer.first_name
            if self.writer.ipi_name:
                data['writer_ipi_name'] = self.writer.ipi_name
            if self.writer.ipi_base:
                data['writer_ipi_base'] = self.writer.ipi_base
            if self.writer.pr_society:
                data['writer_pr_society'] = self.writer.pr_society
        else:
            data['writer_id'] = ''
            data['writer_last_name'] = ''
        data.update({
            'controlled': self.controlled,
            'capacity': self.capacity,
            'relative_share': str(self.relative_share / 100),
            'saan': (
                self.saan or
                (self.writer.saan if self.writer else None) or
                '')
        })
        return data


class CWRExport(models.Model):
    class Meta:
        verbose_name = 'CWR Export'
        verbose_name_plural = 'CWR Exports'
        ordering = ('-id',)

    nwr_rev = models.CharField(
        'NWR/REV', max_length=3, db_index=True, default='NWR', choices=(
            ('NWR', 'New work registration'),
            ('REV', 'Revision of registered work')))
    cwr = models.TextField(blank=True, editable=False)
    year = models.CharField(
        max_length=2, db_index=True, editable=False, blank=True)
    num_in_year = models.PositiveSmallIntegerField(default=0)
    works = models.ManyToManyField(Work)

    @property
    def json(self):
        j = OrderedDict([('revision', self.nwr_rev == 'REV')])
        j.update({
            "publisher_id": SETTINGS.get('publisher_id'),
            "publisher_name": SETTINGS.get('publisher_name'),
            "publisher_ipi_name": SETTINGS.get('publisher_ipi_name'),
            "publisher_ipi_base": SETTINGS.get('publisher_ipi_base'),
            "publisher_pr_society": SETTINGS.get(
                'publisher_pr_society'),
            "publisher_mr_society": SETTINGS.get(
                'publisher_mr_society'),
            "publisher_sr_society": SETTINGS.get(
                'publisher_pr_society'),
        })
        works = OrderedDict()
        for work in self.works.order_by('id'):
            works.update(work.json)
        j.update({"works": works})
        return j

    @property
    def filename(self):
        if not self.cwr:
            return 'CW DRAFT {}'.format(self.id)
        return 'CW{}{:04}{}_000.V21'.format(
            self.year,
            self.num_in_year,
            SETTINGS.get('publisher_id'))

    def __str__(self):
        return self.filename

    def get_cwr(self):
        if self.cwr:
            return

        try:
            response = requests.post(
                SETTINGS.get('generator_url'),
                headers={'Authorization': 'Token {}'.format(
                    SETTINGS.get('token'))},
                json=self.json, timeout=30)
        except requests.exceptions.ConnectionError:
            raise ValidationError('Network error', code='service')

        if response.status_code == 400:
            raise ValidationError('Bad Request', code='service')
        elif response.status_code == 401:
            raise ValidationError('Unauthorized', code='service')
        elif response.status_code != 200:
            raise ValidationError('Unknown Error', code='service')
        else:
            self.cwr = response.json()['cwr']
            self.year = self.cwr[66:68]
            nr = CWRExport.objects.filter(year=self.year)
            nr = nr.order_by('-num_in_year').first()
            if nr:
                self.num_in_year = nr.num_in_year + 1
            else:
                self.num_in_year = 1
            self.save()


class WorkAcknowledgement(models.Model):

    TRANSACTION_STATUS_CHOICES = (
        ('CO', 'Conflict'),
        ('DU', 'Duplicate'),
        ('RA', 'Transaction Accepted'),
        ('SA', 'Registration Accepted'),
        ('AC', 'Registration Accepted with Changes'),
        ('RJ', 'Rejected'),
        ('NP', 'No Participation'),
        ('RC', 'Claim rejected'),
    )

    work = models.ForeignKey(Work, on_delete=models.PROTECT)
    society_code = models.CharField(
        'Society', max_length=3, choices=SOCIETIES)
    date = models.DateField()
    status = models.CharField(max_length=2, choices=TRANSACTION_STATUS_CHOICES)
    remote_work_id = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return self.status


class ACKImport(models.Model):

    class Meta:
        verbose_name = 'CWR ACK Import'

    filename = models.CharField(max_length=60, editable=False)
    society_code = models.CharField(max_length=3, editable=False)
    society_name = models.CharField(max_length=45, editable=False)
    date = models.DateField(editable=False)
    report = models.TextField(editable=False)
