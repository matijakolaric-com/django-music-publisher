from collections import OrderedDict
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
import requests
from .base import *


class Work(WorkBase):
    """Concrete class, with references to foreign objects.

    Attributes:
        artists (django.db.models.ManyToManyField):
            Artists performing the work
        last_change (django.db.models.DateTimeField):
            when the last change was made to this object or any of the child
            objects, basically used in filtering
        writers (django.db.models.ManyToManyField):
            Writers who created the work
    """

    artists = models.ManyToManyField('Artist', through='ArtistInWork')
    writers = models.ManyToManyField('Writer', through='WriterInWork')
    last_change = models.DateTimeField(
        'Last Edited', editable=False, null=True)

    @property
    def json(self):
        """Create a data structure that can be serielized as JSON.

        Returns:
            dict: JSON-serializable data structure
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
        data['society_work_codes'] = [
            wa for wa in self.workacknowledgement_set.filter(
                remote_work_id__gt='').values(
                'society_code', 'remote_work_id').distinct()]
        try:
            data.update(self.firstrecording.json)
        except ObjectDoesNotExist:
            pass
        return {self.work_id: data}

    @property
    def work_id(self):
        """Create Work ID used in registrations

        Returns:
            str: Internal Work ID
        """
        if self.id is None:
            return ''
        return '{}{:06}'.format(WORK_ID_PREFIX, self.id)

    def __str__(self):
        return '{} {} ({})'.format(
            self.work_id,
            self.title,
            ' / '.join(w.last_name.upper() for w in self.writers.all()))


class AlternateTitle(TitleBase):
    """Conrete class for alternate titles.

    Attributes:
        work (django.db.models.ForeignKey): Foreign key to Work model
    """

    work = models.ForeignKey(Work, on_delete=models.CASCADE)

    class Meta:
        unique_together = (('work', 'title'),)

    @property
    def json(self):
        """Create a data structure that can be serielized as JSON.

        Returns:
            dict: JSON-serializable data structure
        """
        return {'alternate_title': self.title}


class AlbumCD(AlbumCDBase):
    """Conrete class for album / CD."""
    pass


class Artist(ArtistBase):
    """Concrete class for performing artists."""

    @property
    def json(self):
        """Create a data structure that can be serielized as JSON.

        Returns:
            dict: JSON-serializable data structure
        """
        return {
            'artist_first_name': self.first_name,
            'artist_last_name': self.last_name,
            'isni': self.isni}


class FirstRecording(RecordingBase):
    """Concrete class for first recording.

    Attributes:
        album_cd (django.db.models.ForeignKey): FK to Album/CD
        artist (django.db.models.ForeignKey):
            FK to Artist, in this context, it is a recording artist
        work (django.db.models.OneToOneField): One to One field to Work
    """

    work = models.OneToOneField(Work, on_delete=models.CASCADE)
    artist = models.ForeignKey(
        Artist, on_delete=models.PROTECT, blank=True, null=True,
        verbose_name='Recording Artist')
    album_cd = models.ForeignKey(
        AlbumCD, on_delete=models.PROTECT, blank=True, null=True,
        verbose_name='Album / Library CD')

    def __str__(self):
        return str(self.work)

    @property
    def json(self):
        """Create a data structure that can be serielized as JSON.

        Returns:
            dict: JSON-serializable data structure
        """
        data = OrderedDict()
        if self.duration:
            data['first_release_duration'] = self.duration.strftime('%H%M%S')
        data['isrc'] = self.isrc or ''
        data['record_label'] = self.record_label
        if self.artist:
            data['recording_artist'] = self.artist.json
        if self.album_cd:
            if self.album_cd.release_date:
                data['first_release_date'] = (
                    self.album_cd.release_date.strftime('%Y%m%d'))
            data.update({
                'first_album_title': self.album_cd.album_title or '',
                'first_album_label': self.album_cd.album_label or '',
                'ean': self.album_cd.ean or ''})
        if self.release_date:
            data['first_release_date'] = self.release_date.strftime('%Y%m%d')
        if self.album_cd and self.album_cd.library:
            data.update({
                'library': self.album_cd.library,
                'cd_identifier': self.album_cd.cd_identifier})
        return data


class ArtistInWork(models.Model):
    """Artist performing the work (live in CWR 3).

    Attributes:
        artist (django.db.models.ForeignKey): FK to Artist
        work (django.db.models.ForeignKey): FK to Work
    """

    work = models.ForeignKey(Work, on_delete=models.CASCADE)
    artist = models.ForeignKey(Artist, on_delete=models.PROTECT)

    class Meta:
        verbose_name = 'Artist performing work'
        verbose_name_plural = 'Artists performing works'
        unique_together = (('work', 'artist'),)

    def __str__(self):
        return str(self.artist)


class Writer(WriterBase):
    """Concrete class for writers.
    """

    def clean(self, *args, **kwargs):
        super().clean(*args, **kwargs)
        if self.pk is None or self._can_be_controlled:
            return
        # A controlled writer requires more data, so once a writer is in
        # that role, it is not allowed to remove required data."""
        if self.writerinwork_set.filter(controlled=True).exists():
            raise ValidationError(
                'This writer is controlled in at least one work. ' +
                CAN_NOT_BE_CONTROLLED_MSG)


class WriterInWork(models.Model):
    """Writers who created this work.

    At least one writer in work must be controlled.
    Sum of relative shares must be (roughly) 100%.
    Capacity is limited to roles for original writers.

    Attributes:
        capacity (django.db.models.CharField): Role of the writer in this work
        controlled (django.db.models.BooleanField): A complete mistery field
        publisher_fee (django.db.models.DecimalField): Percentage of royalties
            kept by publisher
        relative_share (django.db.models.DecimalField): Initial split among
            writers, prior to publishing
        saan (django.db.models.CharField): Society-assigned agreement number
            between the writer and the original publisher, please note that
            this field is for SPECIFIC agreements, for a general agreement,
            use :attr:`.base.IPIBase.saan`
        work (django.db.models.ForeignKey): FK to Work
        writer (django.db.models.ForeignKey): FK to Writer
    """

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
        """Make sure that controlled writers have all the required data.

        Also check that writers that are not controlled do not have data
        that can not apply to them."""

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
        """Create a data structure that can be serielized as JSON.

        Returns:
            dict: JSON-serializable data structure
        """
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
        })
        if self.controlled:
            publisher = self.writer.get_publisher_dict()
            saan = (
                self.saan or
                (self.writer.saan if self.writer else None) or
                ''
            )
            data.update({
                'publisher_for_writer_id': publisher.get('publisher_id'),
                'saan': saan,
                'general_agreement': bool(saan and not self.saan),
            })
        return data


class CWRExport(models.Model):
    """Export in CWR format.

    Common Works Registration format is a standard format for registration of
    musical works world-wide. As of November 2018, version 2.1r7 is used
    everywhere, while some societies accept 2.2 as well, it adds no benefits
    in this context. Version 3.0 is in draft.

    Attributes:
        nwr_rev (django.db.models.CharField): Choice field where user can
            select which version and type of CWR it is.
    """

    class Meta:
        verbose_name = 'CWR Export'
        verbose_name_plural = 'CWR Exports'
        ordering = ('-id',)

    nwr_rev = models.CharField(
        'NWR/REV', max_length=3, db_index=True, default='NWR', choices=(
            ('NWR', 'CWR 2.1: New work registration'),
            ('REV', 'CWR 2.1: Revision of registered work'),
            ('WRK', 'CWR 3.0: Work registration (alpha)')))
    cwr = models.TextField(blank=True, editable=False)
    year = models.CharField(
        max_length=2, db_index=True, editable=False, blank=True)
    num_in_year = models.PositiveSmallIntegerField(default=0)
    works = models.ManyToManyField(Work, related_name='cwr_exports')
    _work_count = models.IntegerField(
        editable=False, null=True)

    @property
    def is_version_3(self):
        return self.nwr_rev == 'WRK'

    @property
    def filename(self):
        if not self.cwr:
            return '{} DRAFT {}'.format(self.nwr_rev, self.id)
        if self.is_version_3:
            return 'CW{}{:04}{}_000_V3-0-0.SUB'.format(
                self.year,
                self.num_in_year,
                SETTINGS.get('publisher_id'))
        return 'CW{}{:04}{}_000.V21'.format(
            self.year,
            self.num_in_year,
            SETTINGS.get('publisher_id'))

    def __str__(self):
        return self.filename

    def get_json(self, qs=None):
        """Create a data structure that can be serielized as JSON.

        Returns:
            dict: JSON-serializable data structure
        """
        if qs is None:
            qs = self.works.order_by('id')
        if self.is_version_3:
            j = OrderedDict([
                ('filename', self.filename),
                ('version', '3.0'),
            ])
        else:
            j = OrderedDict([('revision', self.nwr_rev == 'REV')])
        j.update({
            "sender_id": SETTINGS.get('publisher_ipi_name'),
            "sender_name": SETTINGS.get('publisher_name'),
            "publisher_id": SETTINGS.get('publisher_id'),
            "publisher_name": SETTINGS.get('publisher_name'),
            "publisher_ipi_name": SETTINGS.get('publisher_ipi_name'),
            "publisher_ipi_base": SETTINGS.get('publisher_ipi_base', ''),
            "publisher_pr_society": SETTINGS.get(
                'publisher_pr_society'),
            "publisher_mr_society": SETTINGS.get(
                'publisher_mr_society'),
            "publisher_sr_society": SETTINGS.get(
                'publisher_sr_society'),
        })
        us = SETTINGS.get('us_publisher_override', {})
        if us:
            j["ascap_publisher"] = us.get('ASCAP')
            j["bmi_publisher"] = us.get('BMI')
            j["sesac_publisher"] = us.get('SESAC')
        works = OrderedDict()
        for work in qs:
            works.update(work.json)
        j.update({"works": works})
        return j

    @property
    def json(self):
        """Property that wraps :meth:`get_json`.

        Returns:
            dict: JSON-serializable data structure
        """
        return self.get_json()

    def get_cwr(self):
        """Get CWR from the external service, and save.

        Returns:
            None

        Raises:
            ValidationError: Validation errors are raised in case of
                network issues, bad requests, etc, so they can be
                handeled by admin.
        """
        if self.cwr:
            return
        url = SETTINGS.get('generator_url')
        json = self.json
        self._work_count = len(json.get('works'))
        if url is None:
            raise ValidationError('CWR generator URL not set.')
        try:
            response = requests.post(
                url,
                headers={'Authorization': 'Token {}'.format(
                    SETTINGS.get('token'))},
                json=json, timeout=30)
        except requests.exceptions.ConnectionError:
            raise ValidationError('Network error', code='service')
        if response.status_code == 400:
            raise ValidationError('Bad Request', code='service')
        elif response.status_code == 401:
            raise ValidationError('Unauthorized', code='service')
        elif response.status_code != 200:
            raise ValidationError('Unknown Error', code='service')

        nr = CWRExport.objects.filter(year=self.year)
        nr = nr.order_by('-num_in_year').first()
        if nr:
            self.num_in_year = nr.num_in_year + 1
        else:
            self.num_in_year = 1
        if self.is_version_3:
            cwr = response.json()['cwr']
            self.cwr = cwr[0:157]
            self.year = self.cwr[56:58]
            # self.filename depends on self.year !!!
            self.cwr += self.filename.ljust(27)
            self.cwr += cwr[184:]
        else:
            self.cwr = response.json()['cwr']
            self.year = self.cwr[66:68]
        self.save()


class WorkAcknowledgement(models.Model):
    """Acknowledgement of work registration.

    Attributes:
        date (django.db.models.DateField): Acknowledgement date
        remote_work_id (django.db.models.CharField): Remote work ID
        society_code (django.db.models.CharField): 3-digit society code
        status (django.db.models.CharField): 2-letter status code
        TRANSACTION_STATUS_CHOICES (tuple): choices for status
        work (django.db.models.ForeignKey): FK to Work
    """

    class Meta:
        verbose_name = 'Registration Acknowledgement'

    TRANSACTION_STATUS_CHOICES = (
        ('CO', 'Conflict'),
        ('DU', 'Duplicate'),
        ('RA', 'Transaction Accepted'),
        ('AS', 'Registration Accepted'),
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
    """CWR acknowledgement file import.

    Attributes:
        date (django.db.models.DateField): Acknowledgement date
        filename (django.db.models.CharField): Description
        report (django.db.models.CharField): Basically a log
        society_code (models.CharField): 3-digit society code,
            please note that ``choices`` is not set.
        society_name (models.CharField): Society name,
            used if society code is missing.
    """

    class Meta:
        verbose_name = 'CWR ACK Import'

    filename = models.CharField(max_length=60, editable=False)
    society_code = models.CharField(max_length=3, editable=False)
    society_name = models.CharField(max_length=45, editable=False)
    date = models.DateField(editable=False)
    report = models.TextField(editable=False)

    def __str__(self):
        return self.filename
