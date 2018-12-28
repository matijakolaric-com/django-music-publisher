from collections import OrderedDict, defaultdict
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
import requests
from .base import *
from .cwr_templates import *
from datetime import datetime
from django.template import Context
from decimal import Decimal


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
        if self.original_title:
            data['version_type'] = 'modification'
            data['original_title'] = self.original_title
        else:
            data['version_type'] = 'original'
        if self.iswc:
            data['iswc'] = self.iswc
        data['alternate_titles'] = [
            at.json for at in self.alternatetitle_set.all()]
        data['publishers'] = {}
        data['writers'] = {}

        data['writers_for_work'] = []
        for wiw in self.writerinwork_set.all():
            j = wiw.json
            writer = j.pop('writer', None)
            if writer:
                id = writer.pop('writer_id')
                data['writers'][id] = writer
            data['writers_for_work'].append(j)
        data['albums'] = {}
        data['artists'] = {}
        try:
            data.update(self.firstrecording.json)
        except ObjectDoesNotExist:
            pass
        data['live_artists'] = []
        for aiw in self.artistinwork_set.all():
            j = aiw.json
            data['artists'][j['artist_id']] = j.pop('artist')
            data['live_artists'].append(j)
        data['society_work_codes'] = []
        for wa in self.workacknowledgement_set.filter(
                remote_work_id__gt='').values(
                'society_code', 'remote_work_id').distinct():
            wa['society_code'] = wa['society_code'].lstrip('0')
            data['society_work_codes'].append(wa)
        return (self.work_id, data)

    @property
    def work_id(self):
        """Create Work ID used in registrations

        Returns:
            str: Internal Work ID
        """
        if self.id is None:
            return ''
        return '{}{:06}'.format(SETTINGS.get('work_id_prefix', ''), self.id)

    def __str__(self):
        return '{} {} ({})'.format(
            self.work_id,
            self.title.upper(),
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
        j = {'last_name': self.last_name}
        if self.first_name:
            j['first_name'] = self.first_name
        if self.isni:
            j['isni'] = self.isni
        return j


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
            artist_id = 'A{:06d}'.format(self.artist.id)
            data['artist_id'] = artist_id
        if self.album_cd and self.album_cd.album_title:
            if self.album_cd.release_date:
                data['release_date'] = (
                    self.album_cd.release_date.strftime('%Y%m%d'))
            album_id = 'AL{:03d}'.format(self.album_cd.id)
            data['album_id'] = album_id
        if self.release_date:
            data['release_date'] = self.release_date.strftime('%Y%m%d')
        data = {'recordings': [data]}
        if self.artist:
            data['artists'] = {artist_id: self.artist.json}
        if self.album_cd and self.album_cd.album_title:
            album = {
                'title': self.album_cd.album_title
            }
            if self.album_cd.release_date:
                album['release_date'] = (
                    self.album_cd.release_date.strftime('%Y%m%d'))
            if self.album_cd.album_label:
                album['label'] = self.album_cd.album_label
            if self.album_cd.ean:
                album['ean'] = self.album_cd.ean
            data['albums'] = {album_id: album}
        if self.album_cd and self.album_cd.library:
            data['libraries'] = {'L001': {'name': self.album_cd.library}}
            data['source'] = {
                'type': 'library',
                'library_id': 'L001',
                'cd_identifier': self.album_cd.cd_identifier}
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

    @property
    def json(self):
        data = {}
        data['artist_id'] = 'A{:06d}'.format(self.artist.id)
        data['artist'] = self.artist.json
        return data


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
        unique_together = (('work', 'writer', 'controlled'),)
        ordering = (
            '-controlled', 'writer__last_name', 'writer__first_name', '-id')

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
        ('CA', 'Composer&Lyricist'),
        ('C ', 'Composer'),
        ('A ', 'Lyricist'),
        ('AR', 'Arranger'),
        ('AD', 'Adaptor'),
        ('TR', 'Translator'),
    ) if SETTINGS.get('allow_modifications') else (
        ('CA', 'Composer&Lyricist'),
        ('C ', 'Composer'),
        ('A ', 'Lyricist'),
    ))
    publisher_fee = models.DecimalField(
        max_digits=5, decimal_places=2, blank=True, null=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text='Percentage of royalties kept by the publisher')

    def __str__(self):
        return str(self.writer)

    def clean_fields(self, *args, **kwargs):
        """Turn SAAN into uppercase.

        Args:
            *args: passing through
            **kwargs: passing through

        Returns:
            TYPE: Description
        """
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
        d = {}
        if self.controlled:
            if not self.capacity:
                d['capacity'] = 'Must be set for a controlled writer.'
            if not self.writer:
                d['writer'] = 'Must be set for a controlled writer.'
            else:
                if not self.writer._can_be_controlled:
                    d['writer'] = CAN_NOT_BE_CONTROLLED_MSG
                if (ENFORCE_SAAN and
                        not self.writer.generally_controlled and
                        not self.saan):
                    d['saan'] = \
                        'Must be set. (controlled, no general agreement)'
                if (ENFORCE_PUBLISHER_FEE and
                        not self.writer.generally_controlled and
                        not self.publisher_fee):
                    d['publisher_fee'] = \
                        'Must be set. (controlled, no general agreement)'
        else:
            if self.saan:
                d['saan'] = 'Must be empty if writer is not controlled.'
            if self.publisher_fee:
                d['publisher_fee'] = \
                    'Must be empty if writer is not controlled.'
        if d:
            raise ValidationError(d)

    @property
    def json(self):
        """Create a data structure that can be serielized as JSON.

        Returns:
            dict: JSON-serializable data structure
        """
        data = OrderedDict()
        data.update({
            'controlled': self.controlled,
            'relative_share': str(self.relative_share / 100),
        })
        if self.writer:
            data['writer_id'] = 'W{:06d}'.format(self.writer.id)
            data['writer'] = {
                'writer_id': data['writer_id'],
                'last_name': self.writer.last_name
            }
            if self.writer.first_name:
                data['writer']['first_name'] = self.writer.first_name
            if self.writer.ipi_name:
                data['writer']['ipi_name'] = self.writer.ipi_name
            if self.writer.ipi_base:
                data['writer']['ipi_base'] = self.writer.ipi_base
            if self.writer.pr_society:
                data['writer']['pr_society'] = self.writer.pr_society

        if self.capacity:
            data['capacity'] = self.capacity,
        if self.controlled:
            publisher = self.writer.get_publisher_dict()
            pwr = {
                'publisher_id': publisher.get('publisher_id'),
            }
            data['publishers_for_writer'] = [pwr]
            data['writer']['publisher_dict'] = {
                'name': publisher.get('publisher_name'),
                'publisher_id': publisher.get('publisher_id'),
                'pr_society': publisher.get('pr_society'),
            }
            if self.saan:
                agr = {'saan': self.saan, 'type': 'OS'}
                data['publishers_for_writer'][0]['agreement'] = agr
            elif self.writer.saan:
                agr = {'saan': self.writer.saan, 'type': 'OG'}
                data['publishers_for_writer'][0]['agreement'] = agr
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
        'CWR version/type', max_length=3, db_index=True, default='NWR',
        choices=(
            ('NWR', 'CWR 2.1: New work registration'),
            ('REV', 'CWR 2.1: Revision of registered work')))
    cwr = models.TextField(blank=True, editable=False)
    year = models.CharField(
        max_length=2, db_index=True, editable=False, blank=True)
    num_in_year = models.PositiveSmallIntegerField(default=0)
    works = models.ManyToManyField(Work, related_name='cwr_exports')
    _work_count = models.IntegerField(
        editable=False, null=True)

    @property
    def filename(self):
        """REturn proper CWR filename.

        Returns:
            str: CWR file name
        """
        return 'CW{}{:04}{}_000.V21'.format(
            self.year,
            self.num_in_year,
            SETTINGS.get('publisher_id'))

    def __str__(self):
        return self.filename

    def get_record(self, key, record):
        """Create CWR record (row) from the key and dict.

        Args:
            key (str): type of record
            record (dict): field values

        Returns:
            str: CWR record (row)
        """
        template = TEMPLATES_21.get(key)
        return template.render(Context(record)).upper()

    def get_transaction_record(self, key, record):
        """Create CWR transaction record (row) from the key and dict.

        This methods adds transaction and record sequences.

        Args:
            key (str): type of record
            record (dict): field values

        Returns:
            str: CWR record (row)
        """
        record['transaction_sequence'] = self.transaction_count
        record['record_sequence'] = self.record_sequence
        line = self.get_record(key, record)
        self.record_count += 1
        self.record_sequence += 1
        return line

    def yield_lines(self, works):
        """Yield CWR transaction records (rows/lines) for works

        Args:
            works (query): :class:`.models.Work` query

        Yields:
            str: CWR recors (row/line)
        """
        self.record_count = self.record_sequence = self.transaction_count = 0
        yield self.get_record('HDR', {
            'creation_date': datetime.now(),
            **SETTINGS
        })
        yield self.get_record('GRH', {'transaction_type': self.nwr_rev})

        for work in works:
            self.record_sequence = 0
            d = {
                'record_type': self.nwr_rev,
                'work_id': work.work_id,
                'work_title': work.title,
                'iswc': work.iswc}
            try:
                d['isrc'] = work.firstrecording.isrc
                d['duration'] = work.firstrecording.duration
                d['recorded_indicator'] = 'Y'
            except ObjectDoesNotExist:
                d['recorded_indicator'] = 'U'
            d['version_type'] = (
                'MOD   UNSUNS' if work.is_modification() else
                'ORI         ')
            yield self.get_transaction_record('NWR', d)
            publishers = OrderedDict()
            other_publisher_share = None
            controlled_writer_ids = []
            controlled_writer_shares = defaultdict(Decimal)
            for wiw in work.writerinwork_set.order_by(
                    '-controlled', 'id'):
                if wiw.controlled:
                    controlled_writer_ids.append(wiw.writer_id)
                    controlled_writer_shares[wiw.writer_id] += \
                        wiw.relative_share
                    d = wiw.writer.get_publisher_dict()
                    key = d['publisher_id']
                    if key in publishers:
                        publishers[key]['share'] += wiw.relative_share
                    else:
                        publishers[key] = d
                        publishers[key]['share'] = wiw.relative_share
                elif wiw.writer_id in controlled_writer_ids:
                    controlled_writer_shares[wiw.writer_id] += \
                        wiw.relative_share
                    if other_publisher_share is None:
                        other_publisher_share = wiw.relative_share
                    else:
                        other_publisher_share += wiw.relative_share
            for i, (key, publisher) in enumerate(publishers.items()):
                publisher['sequence'] = i + 1
                yield self.get_transaction_record('SPU', publisher)
                yield self.get_transaction_record('SPT', publisher)
            if other_publisher_share:
                yield self.get_transaction_record(
                    'OPU', {
                        'share': other_publisher_share,
                        'sequence': len(publishers) + 1})
            for wiw in work.writerinwork_set.order_by(
                    '-controlled', 'id'):
                if not wiw.controlled:
                    continue
                w = wiw.writer
                record = {
                    'capacity': wiw.capacity,
                    'share': controlled_writer_shares[w.id],
                    'saan': wiw.saan or w.saan}
                record['interested_party_number'] = 'W{:06d}'.format(w.id)
                record['ipi_name'] = w.ipi_name
                record['ipi_base'] = w.ipi_base
                record['last_name'] = w.last_name
                record['first_name'] = w.first_name
                record['pr_society'] = w.pr_society
                yield self.get_transaction_record('SWR', record)
                yield self.get_transaction_record('SWT', record)
                record.update(w.get_publisher_dict())
                yield self.get_transaction_record('PWR', record)
            for wiw in work.writerinwork_set.order_by(
                    '-controlled', 'id'):
                if wiw.controlled or wiw.writer_id in controlled_writer_ids:
                    continue
                record = {
                    'capacity': wiw.capacity,
                    'share': wiw.relative_share}
                if wiw.writer:
                    w = wiw.writer
                    record['interested_party_number'] = 'W{:06d}'.format(w.id)
                    record['ipi_name'] = w.ipi_name
                    record['ipi_base'] = w.ipi_base
                    record['last_name'] = w.last_name
                    record['first_name'] = w.first_name
                    record['pr_society'] = w.pr_society
                else:
                    record['writer_unknown_indicator'] = 'Y'
                yield self.get_transaction_record('OWR', record)

            for record in work.alternatetitle_set.order_by('title'):
                yield self.get_transaction_record('ALT', {
                    'alternate_title': record.title})
            if work.is_modification():
                yield self.get_transaction_record('VER', {
                    'original_title': work.original_title})
            for artist in work.artists.order_by(
                    'last_name', 'first_name', 'id'):
                yield self.get_transaction_record('PER', {
                    'first_name': artist.first_name,
                    'last_name': artist.last_name,
                })
            try:
                artist = work.firstrecording.artist
                if artist:
                    yield self.get_transaction_record('PER', {
                        'first_name': artist.first_name,
                        'last_name': artist.last_name,
                    })
            except ObjectDoesNotExist:
                pass
            try:
                rec = work.firstrecording
                release_date = rec.release_date
                record_label = rec.record_label
                album_title = ''
                if rec.album_cd:
                    release_date = release_date or rec.album_cd.release_date
                    album_title = album_title or rec.album_cd.album_title
                    album_label = rec.album_cd.album_label or record_label
                yield self.get_transaction_record('REC', {
                    'isrc': rec.isrc,
                    'duration': rec.duration,
                    'release_date': release_date,
                    'album_title': album_title,
                    'album_label': album_label
                })
            except ObjectDoesNotExist:
                pass
            try:
                album = work.firstrecording.album_cd
                if album.cd_identifier:
                    yield self.get_transaction_record('ORN', {
                        'library': album.library,
                        'cd_identifier': album.cd_identifier})
            except ObjectDoesNotExist:
                pass
            self.transaction_count += 1

        yield self.get_record('GRT', {
            'transaction_count': self.transaction_count,
            'record_count': self.record_count + 2})
        yield self.get_record('TRL', {
            'transaction_count': self.transaction_count,
            'record_count': self.record_count + 4})

    def create_cwr(self):
        """Create CWR and save.
        """
        if self.cwr:
            return
        self.cwr = ''.join(self.yield_lines(self.works.order_by('id',)))
        self.year = self.cwr[66:68]
        nr = type(self).objects.filter(year=self.year)
        nr = nr.order_by('-num_in_year').first()
        if nr:
            self.num_in_year = nr.num_in_year + 1
        else:
            self.num_in_year = 1
        super().save()


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

