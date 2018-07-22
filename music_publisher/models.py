from django.db import models
from django.conf import settings

SETTINGS = settings.MUSIC_PUBLISHER_SETTINGS


class MusicPublisherBase(models.Model):

    class Meta:
        abstract = True


class TitleBase(MusicPublisherBase):

    class Meta:
        abstract = True

    title = models.CharField(max_length=60, db_index=True)


class WorkBase(TitleBase):

    class Meta:
        abstract = True

    iswc = models.CharField(
        max_length=15, blank=True, null=True, unique=True)


class AlbumCDBase(MusicPublisherBase):

    class Meta:
        abstract = True

    cd_identifier = models.CharField(
        max_length=15, blank=True, null=True, unique=True)

    release_date = models.DateField(blank=True, null=True)
    album_title = models.CharField(max_length=60, blank=True)
    ean = models.CharField(
        max_length=13, blank=True, null=True, unique=True)

    @property
    def album_label(self):
        if self.album_title:
            return SETTINGS.get('label')

    @property
    def library(self):
        if self.cd_identifier:
            return SETTINGS.get('library')


class FirstRecordingBase(MusicPublisherBase):

    class Meta:
        abstract = True

    isrc = models.CharField(max_length=15, blank=True, null=True, unique=True)
    release_date = models.DateField(blank=True, null=True)
    duration = models.TimeField(blank=True, null=True)
    catalog_number = models.CharField(
        max_length=18, blank=True, null=True, unique=True)


class PersonBase(MusicPublisherBase):

    class Meta:
        abstract = True

    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=45, db_index=True)


class Work(WorkBase):
    pass


class AlternateTitle(TitleBase):

    work = models.OneToOneField(Work, on_delete=models.CASCADE)


class AlbumCD(AlbumCDBase):
    pass


class FirstRecording(FirstRecordingBase):

    work = models.OneToOneField(Work, on_delete=models.CASCADE)
    album_cd = models.ForeignKey(AlbumCD, on_delete=models.PROTECT)


class Artist(PersonBase):
    pass



    # work = models.OneToOneField(Work, on_delete=models.CASCADE)


