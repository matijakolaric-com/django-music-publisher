from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

SETTINGS = settings.MUSIC_PUBLISHER_SETTINGS


class MusicPublisherBase(models.Model):

    class Meta:
        abstract = True


class TitleBase(MusicPublisherBase):

    class Meta:
        abstract = True

    title = models.CharField(max_length=60, db_index=True)

    def __str__(self):
        return self.title


class WorkBase(TitleBase):

    class Meta:
        abstract = True

    iswc = models.CharField(
        'ISWC', max_length=15, blank=True, null=True, unique=True)


class AlbumCDBase(MusicPublisherBase):

    class Meta:
        abstract = True
        verbose_name = 'Album and/or Library CD'
        verbose_name_plural = 'Albums and Library CDs'

    cd_identifier = models.CharField(
        'CD Identifier',
        help_text='This will set the purpose to Library.',
        max_length=15, blank=True, null=True, unique=True)
    release_date = models.DateField(
        help_text='Can be owerridden with work first recording releaase date.',
        blank=True, null=True)
    album_title = models.CharField(
        help_text='This will set the label.',
        max_length=60, blank=True, null=True, unique=True)
    ean = models.CharField(
        'EAN',
        max_length=13, blank=True, null=True, unique=True)

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
            ValidationError({
                'album_title': 'Required if EAN or release date is set.'})
        if self.cd_identifier:
            self.cd_identifier = self.cd_identifier.upper()


class FirstRecordingBase(MusicPublisherBase):

    class Meta:
        abstract = True
        verbose_name_plural = 'First recording of the work'

    isrc = models.CharField(
        'ISRC', max_length=15, blank=True, null=True, unique=True)
    release_date = models.DateField(blank=True, null=True)
    duration = models.TimeField(blank=True, null=True)
    catalog_number = models.CharField(
        max_length=18, blank=True, null=True, unique=True)


class PersonBase(MusicPublisherBase):

    class Meta:
        abstract = True

    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=45, db_index=True)

    def __str__(self):
        if self.first_name:
            return '{0.first_name} {0.last_name}'.format(self)
        return self.last_name


class Work(WorkBase):
    artists = models.ManyToManyField('Artist', through='ArtistInWork')


class AlternateTitle(TitleBase):

    work = models.OneToOneField(Work, on_delete=models.CASCADE)


class AlbumCD(AlbumCDBase):
    pass


class FirstRecording(FirstRecordingBase):

    work = models.OneToOneField(Work, on_delete=models.CASCADE)
    album_cd = models.ForeignKey(
        AlbumCD, on_delete=models.PROTECT, blank=True, null=True,
        verbose_name='Album / Library CD')

    def __str__(self):
        return str(self.work)


class Artist(PersonBase):
    class Meta:
        verbose_name = 'Performing Artist'
        verbose_name_plural = 'Performing Artists'


class ArtistInWork(models.Model):
    work = models.ForeignKey(Work, on_delete=models.PROTECT)
    artist = models.ForeignKey(Artist, on_delete=models.PROTECT)

    def __str__(self):
        return str(self.artist)
