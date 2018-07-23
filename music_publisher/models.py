from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.deconstruct import deconstructible
import re
import requests


SETTINGS = settings.MUSIC_PUBLISHER_SETTINGS
VALIDATE = SETTINGS.get('validator_url') and SETTINGS.get('token')
SOCIETIES = (
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
    ('034', 'HFA, United States'),
)


@deconstructible
class CWRFieldValidator:
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

    class Meta:
        abstract = True

    def validate_fields(self, fields):
        keys = list(fields.keys())
        values = list(fields.values())
        data = {'fields': values}
        response = requests.post(
            SETTINGS.get('validator_url'),
            headers={'Authorization': 'Token {}'.format(
                SETTINGS.get('token'))},
            json=data, timeout=10)
        if response.status_code != 200:
            raise ValidationError('Validation failed', code='invalid')
        errors = {}
        rfields = response.json()['fields']
        for i in range(len(fields)):
            field_name = keys[i]
            field_dict = rfields[i]
            if field_dict.get('conditionally_valid'):
                print(field_dict)
            else:
                errors[field_name] = (
                    field_dict['error'] or 'Unknown Error')
        if errors:
            raise ValidationError(errors)

    def clean_fields(self, *args, **kwargs):
        if VALIDATE:
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
            self.validate_fields(fields)
        super().clean_fields(*args, **kwargs)


class TitleBase(MusicPublisherBase):

    class Meta:
        abstract = True

    title = models.CharField(
        max_length=60, db_index=True, validators=(
            CWRFieldValidator('work_title'),))

    def __str__(self):
        return self.title.upper()


class WorkBase(TitleBase):

    class Meta:
        abstract = True

    iswc = models.CharField(
        'ISWC', max_length=15, blank=True, null=True, unique=True,
        validators=(CWRFieldValidator('iswc'),))

    def clean_fields(self, *args, **kwargs):
        if self.iswc:
            self.iswc = self.iswc.replace('-', '').replace('.', '')
        return super().clean_fields(*args, **kwargs)


class AlbumCDBase(MusicPublisherBase):

    class Meta:
        abstract = True
        verbose_name = 'Album and/or Library CD'
        verbose_name_plural = 'Albums and Library CDs'

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
        if not self.cd_identifier and not self.album_title:
            raise ValidationError({
                'cd_identifier': 'Required if Album Title is not set.',
                'album_title': 'Required if CD Identifier is not set.'})
        if (self.ean or self.release_date) and not self.album_title:
            raise ValidationError({
                'album_title': 'Required if EAN or release date is set.'})


class FirstRecordingBase(MusicPublisherBase):

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
            self.isrc = self.isrc.replace('-', '').replace('.', '')
        return super().clean_fields(*args, **kwargs)


class PersonBase(MusicPublisherBase):

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

    class Meta:
        abstract = True
        ordering = ('last_name', 'first_name', 'ipi_name')

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
    generally_controlled = models.BooleanField(default=False)

    def clean_fields(self, *args, **kwargs):
        if self.ipi_base:
            self.ipi_base = self.ipi_base.replace('.', '')
            self.ipi_base = re.sub(
                r'(I).?(\d{9}).?(\d)', r'\1-\2-\3', self.ipi_base)
            print(self.ipi_base)
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

    def __str__(self):
        name = super().__str__()
        if self.generally_controlled:
            return name + ' (*)'
        return name


class Work(WorkBase):
    artists = models.ManyToManyField('Artist', through='ArtistInWork')
    writers = models.ManyToManyField('Writer', through='WriterInWork')

    @property
    def json(self):
        data = {
            'work_title': self.title,
            'iswc': self.iswc,
            'alternate_titles': [
                at.json for at in self.alternatetitle_set.all()],
            'artists': [
                aiw.artist.json for aiw in self.artistinwork_set.all()],
            'writers': [
                wiw.json for wiw in self.writerinwork_set.all()],
        }
        if self.firstrecording:
            data.update(self.firstrecording.json)
        return {self.id: data}


class AlternateTitle(TitleBase):

    work = models.ForeignKey(Work, on_delete=models.CASCADE)

    @property
    def json(self):
        return {'alternate_title': self.title}


class AlbumCD(AlbumCDBase):
    pass


class FirstRecording(FirstRecordingBase):

    work = models.OneToOneField(Work, on_delete=models.CASCADE)
    album_cd = models.ForeignKey(
        AlbumCD, on_delete=models.PROTECT, blank=True, null=True,
        verbose_name='Album / Library CD')

    def __str__(self):
        return str(self.work)

    @property
    def json(self):
        return {
            'first_release_date': (
                self.release_date.strftime('%Y-%m-%d') if self.release_date
                else None),
            'first_release_duration': (
                self.duration.strftime('%H%M%S') if self.duration else None),
            'first_album_title': (
                self.album_cd.album_title if self.album_cd else None),
            'first_album_label': (
                self.album_cd.album_label if self.album_cd else None),
            'first_release_catalog_number': self.catalog_number,
            'ean': (self.album_cd.ean if self.album_cd else None),
            'isrc': self.isrc,
            'library': (
                self.album_cd.library if self.album_cd else None),
            'cd_identifier': (
                self.album_cd.cd_identifier if self.album_cd else None)}


class Artist(PersonBase):
    class Meta:
        verbose_name = 'Performing Artist'
        verbose_name_plural = 'Performing Artists'

    @property
    def json(self):
        return {
            'artist_last_name': self.last_name,
            'artist_first_name': self.first_name}


class ArtistInWork(models.Model):
    work = models.ForeignKey(Work, on_delete=models.CASCADE)
    artist = models.ForeignKey(Artist, on_delete=models.PROTECT)

    class Meta:
        verbose_name = 'Artist Performing Work'
        verbose_name_plural = 'Artists Performing Work'

    def __str__(self):
        return str(self.artist)


class Writer(WriterBase):
    def clean(self, *args, **kwargs):
        super().clean(*args, **kwargs)
        if self.pk is None or self._can_be_controlled:
            return
        if self.writerinwork_set.filter(controlled=True).exists():
            raise ValidationError(
                'This writer is controlled in at least one work, '
                'required are: Last name, IPI Name # and Performing '
                'Rights Society.')


class WriterInWork(models.Model):
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
        return {
            'writer_id': (
                self.writer.ipi_name.rjust(11, '0')[0:9]
                if self.writer.ipi_name else None),
            'writer_last_name': self.writer.last_name,
            'writer_first_name': self.writer.first_name,
            'writer_ipi_name': self.writer.ipi_name,
            'writer_pr_society': self.writer.pr_society,
            'controlled': self.controlled,
            'capacity': self.capacity,
            'relative_share': str(self.relative_share / 100),
            'saan': self.saan or self.writer.saan or ''
        }
