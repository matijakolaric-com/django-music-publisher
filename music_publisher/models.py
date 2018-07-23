from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

SETTINGS = settings.MUSIC_PUBLISHER_SETTINGS

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


class MusicPublisherBase(models.Model):

    class Meta:
        abstract = True


class TitleBase(MusicPublisherBase):

    class Meta:
        abstract = True

    title = models.CharField(max_length=60, db_index=True)

    def __str__(self):
        return self.title.upper()


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
        help_text='Can be overridden by recording data.',
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

    def clean(self):
        self.isrc = self.isrc.replace('-', '')


class PersonBase(MusicPublisherBase):

    class Meta:
        abstract = True

    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=45, db_index=True)

    def __str__(self):
        if self.first_name:
            return '{0.first_name} {0.last_name}'.format(self).upper()
        return self.last_name.upper()


class WriterBase(PersonBase):

    class Meta:
        abstract = True
        ordering = ('last_name', 'first_name', 'ipi_name')

    ipi_name = models.CharField(
        'IPI Name #', max_length=11, blank=True, null=True, unique=True)
    ipi_base = models.CharField(
        'IPI Base #', max_length=15, blank=True, null=True)
    pr_society = models.CharField(
        'Performing Rights Society', max_length=3, blank=True, null=True,
        choices=SOCIETIES)
    saan = models.CharField(
        'Society-assigned agreement number',
        help_text='Use this field for general agreements only.',
        max_length=14, blank=True, null=True, unique=True)

    _can_be_controlled = models.BooleanField(editable=False, default=False)
    generally_controlled = models.BooleanField(default=False)

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
                'saan':
                    'Only for generally controlled writers.'})

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
        return {self.id: {
            'work_title': self.title,
            'iswc': self.iswc,
            'alternate_titles': [
                at.json for at in self.alternatetitle_set.all()]
        }}


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


class Artist(PersonBase):
    class Meta:
        verbose_name = 'Performing Artist'
        verbose_name_plural = 'Performing Artists'


class ArtistInWork(models.Model):
    work = models.ForeignKey(Work, on_delete=models.PROTECT)
    artist = models.ForeignKey(Artist, on_delete=models.PROTECT)

    class Meta:
        verbose_name = 'Artist Performing Work'
        verbose_name_plural = 'Artists Performing Work'

    def __str__(self):
        return str(self.artist)


class Writer(WriterBase):
    pass


class WriterInWork(models.Model):
    work = models.ForeignKey(Work, on_delete=models.PROTECT)
    writer = models.ForeignKey(Writer, on_delete=models.PROTECT,
                               blank=True, null=True)
    saan = models.CharField(
        'Society-assigned agreement number',
        help_text='Use this field for specific agreements only.',
        max_length=14, blank=True, null=True)
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
