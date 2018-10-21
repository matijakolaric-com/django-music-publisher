from collections import OrderedDict
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
import requests
from .base import *


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
        if self.id is None:
            return ''
        return '{}{:06}'.format(WORK_ID_PREFIX, self.id)

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
        data['isrc'] = self.isrc or ''
        data['first_release_catalog_number'] = self.catalog_number or ''
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


class Artist(ArtistBase):
    """Concrete class for performing artists."""

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
        ordering = ('-controlled', 'writer__last_name', 'writer__first_name')

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
    publisher_fee = models.DecimalField(
        max_digits=5, decimal_places=2, blank=True, null=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text='Percentage of royalties kept by the publisher')

    def __str__(self):
        return str(self.writer)

    def clean_fields(self, *args, **kwargs):
        if self.saan:
            self.saan = self.saan.upper()
        return super().clean_fields(*args, **kwargs)

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
        if (ENFORCE_SAAN and self.controlled and
                not self.writer.generally_controlled and not self.saan):
            raise ValidationError({
                'saan': 'Must be set. (controlled, no general agreement)'})
        if (ENFORCE_PUBLISHER_FEE and self.controlled and
                not self.writer.generally_controlled and
                not self.publisher_fee):
            raise ValidationError({
                'publisher_fee': (
                    'Must be set. (controlled, no general agreement)')})
        if not self.controlled and self.saan:
            raise ValidationError({'saan': 'Must not be set.'})
        if not self.controlled and self.publisher_fee:
            raise ValidationError({'publisher_fee': 'Must not be set.'})

    @property
    def json(self):
        data = OrderedDict()
        if self.writer:
            data['writer_id'] = 'W{:06d}'.format(self.writer.id)
            data['writer_last_name'] = self.writer.last_name or ''
            data['writer_first_name'] = self.writer.first_name or ''
            data['writer_ipi_name'] = self.writer.ipi_name or ''
            data['writer_ipi_base'] = self.writer.ipi_base or ''
            data['writer_pr_society'] = self.writer.pr_society or ''
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
            "publisher_ipi_base": SETTINGS.get('publisher_ipi_base', ''),
            "publisher_pr_society": SETTINGS.get(
                'publisher_pr_society'),
            "publisher_mr_society": SETTINGS.get(
                'publisher_mr_society'),
            "publisher_sr_society": SETTINGS.get(
                'publisher_pr_society'),
        })
        us = SETTINGS.get('us_publisher_override', {})
        if us:
            j["ascap_publisher"] = us.get('ASCAP')
            j["bmi_publisher"] = us.get('BMI')
            j["sesac_publisher"] = us.get('SESAC')
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

    class Meta:
        verbose_name = 'Registration Acknowledgement'

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

    def __str__(self):
        return self.filename
