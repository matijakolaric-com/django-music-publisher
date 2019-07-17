from collections import OrderedDict, defaultdict
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from .base import *
from .cwr_templates import *
from datetime import datetime
from django.template import Context
from decimal import Decimal


class Artist(PersonBase, models.Model):
    """Concrete class for performing artists.

    Attributes:
        isni (django.db.models.CharField):
            International Standard Name Identifier
    """

    class Meta:
        verbose_name = 'Performing Artist'
        verbose_name_plural = '  Performing Artists'
        ordering = ('last_name', 'first_name', '-id')

    isni = models.CharField(
        'ISNI',
        max_length=16, blank=True, null=True, unique=True,
        validators=(CWRFieldValidator('isni'),))

    def clean_fields(self, *args, **kwargs):
        if self.isni:
            self.isni = self.isni.rjust(16, '0').upper()
        return models.Model.clean_fields(self, *args, **kwargs)

    def get_dict(self):
        """Create a data structure that can be serialized as JSON.

        Returns:
            dict: JSON-serializable data structure
        """
        j = {
            'last_name': self.last_name,
            'first_name': self.first_name or None,
            'isni': self.isni or None,
        }
        return {self.artist_id: j}

    @property
    def artist_id(self):
        return 'A{:06d}'.format(self.id)


class Label(models.Model):
    class Meta:
        verbose_name_plural = ' Music Labels'
        ordering = ('name', )

    name = models.CharField(
        max_length=60, unique=True,
        validators=(CWRFieldValidator('label'),))

    def __str__(self):
        return self.name

    @property
    def label_id(self):
        return 'LA{:06d}'.format(self.id)

    def get_dict(self):
        """Create a data structure that can be serialized as JSON.

        Returns:
            dict: JSON-serializable data structure
        """
        return {self.label_id: {'name': self.name}}


class Library(models.Model):
    class Meta:
        verbose_name_plural = ' Music Libraries'
        ordering = ('name',)

    name = models.CharField(
        max_length=60, unique=True,
        validators=(CWRFieldValidator('library'),))

    def __str__(self):
        return self.name

    @property
    def library_id(self):
        return 'LI{:06d}'.format(self.id)

    def get_dict(self):
        """Create a data structure that can be serialized as JSON.

        Returns:
            dict: JSON-serializable data structure
        """
        return {self.library_id: {'name': self.name}}


class Release(models.Model):
    class Meta:
        ordering = ('release_title', 'cd_identifier', '-id')

    cd_identifier = models.CharField(
        'CD identifier',
        max_length=15, blank=True, null=True, unique=True, validators=(
            CWRFieldValidator('cd_identifier'),))
    library = models.ForeignKey(
        Library, null=True, blank=True, on_delete=models.PROTECT)
    release_date = models.DateField(
        blank=True, null=True)
    release_title = models.CharField(
        'Release (album) title ',
        max_length=60, blank=True, null=True, unique=True, validators=(
            CWRFieldValidator('release_title'),))
    ean = models.CharField(
        'Release (album) EAN',
        max_length=13, blank=True, null=True, unique=True, validators=(
            CWRFieldValidator('ean'),))
    release_label = models.ForeignKey(
        Label,
        verbose_name='Release (album) label',
        null=True, blank=True,
        on_delete=models.PROTECT
    )

    recordings = models.ManyToManyField(
        'Recording', through='Track')

    def __str__(self):
        if self.cd_identifier:
            if self.release_title:
                return '{}: {} ({})'.format(
                    self.cd_identifier,
                    self.release_title.upper(),
                    self.library)
            else:
                return '{} ({})'.format(
                    self.cd_identifier, self.library)
        else:
            if self.release_label:
                return '{} ({})'.format(self.release_label, self.release_title.upper())
            return self.release_title.upper()


    def clean(self):
        if not self.cd_identifier and not self.release_title:
            raise ValidationError({
                'cd_identifier': 'Required if Album Title is not set.',
                'release_title': 'Required if CD Identifier is not set.'})
        if ((self.ean or self.release_date or self.release_label)
                and not self.release_title):
            raise ValidationError({
                'release_title': 'Required if EAN or release date is set.'})

    @property
    def release_id(self):
        return 'RE{:06d}'.format(self.id)

    def get_dict(self):
        """Create a data structure that can be serialized as JSON.

        Returns:
            dict: JSON-serializable data structure
        """
        if not (self.release_title or
                self.release_label or
                self.release_date or
                self.ean):
            return None
        j = {
            'release_title': self.release_title or None,
            'release_date':
                self.release_date.strftime('%Y%m%d') if self.release_date
                else None,
            'release_label':
                self.release_label.get_dict() if self.release_label else None,
            'ean': self.ean,
        }
        return {self.release_id: j}


class LibraryReleaseManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(cd_identifier__isnull=False)


class LibraryRelease(Release):
    class Meta:
        proxy = True
        verbose_name_plural = ' Library Releases'
    objects = LibraryReleaseManager()

    def get_origin_dict(self):
        """Create a data structure that can be serialized as JSON.

        Returns:
            dict: JSON-serializable data structure
        """
        j = {
            'origin_type': {
                'code': 'LIB',
                'name': 'Library Work'
            },
            'cd_identifier': self.cd_identifier,
            'library': self.library.get_dict()
        }
        return {'OR{:06d}'.format(self.id): j}


class CommercialReleaseManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(cd_identifier__isnull=True)


class CommercialRelease(Release):
    class Meta:
        proxy = True
        verbose_name_plural = ' Commercial Releases'
    objects = CommercialReleaseManager()


class Writer(PersonBase, IPIBase, models.Model):
    """Base class for writers, the second most important top-level class.
    """

    class Meta:
        ordering = ('last_name', 'first_name', 'ipi_name', '-id')
        verbose_name_plural = '  Writers'

    def __str__(self):
        name = super().__str__()
        if self.generally_controlled:
            return name + ' (*)'
        return name

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

    @property
    def writer_id(self):
        return 'WR{:06d}'.format(self.id)

    def get_dict(self):
        """Create a data structure that can be serialized as JSON.

        Returns:
            dict: JSON-serializable data structure
        """

        j = {
            'first_name': self.first_name or None,
            'last_name': self.last_name or None,
            'ipi_name': self.ipi_name or None,
            'ipi_base': self.ipi_base or None,
            'affiliations': [{
                'organization': {
                    'code': self.pr_society,
                    'name': self.get_pr_society_display().split(',')[0],
                },
                'affiliation_type': {
                    'code': 'PR',
                    'name': 'Performance Rights'
                },
                'territory': {
                    'code': '2136',
                    'tis_code': '2136',
                    'name': 'World'
                }
            }] if self.pr_society else []
        }
        return {'WR{:06d}'.format(self.id): j}


class WorkManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().prefetch_related('writers')


class Work(TitleBase):
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

    class Meta:
        verbose_name_plural = '    Works'
        ordering = ('-id', )

    iswc = models.CharField(
        'ISWC', max_length=15, blank=True, null=True, unique=True,
        validators=(CWRFieldValidator('iswc'),))
    original_title = models.CharField(
        max_length=60, db_index=True, blank=True,
        help_text='Use only for modification of existing works.',
        validators=(
            CWRFieldValidator('work_title'),))
    library_release = models.ForeignKey(
        'LibraryRelease', on_delete=models.PROTECT, blank=True, null=True,
        related_name='works',
        verbose_name='Library Release')

    last_change = models.DateTimeField(
        'Last Edited', editable=False, null=True)

    artists = models.ManyToManyField('Artist', through='ArtistInWork')
    writers = models.ManyToManyField('Writer', through='WriterInWork')

    objects = WorkManager()

    @property
    def work_id(self):
        """Create Work ID used in registrations

        Returns:
            str: Internal Work ID
        """
        if self.id is None:
            return ''
        return '{}{:06}'.format(SETTINGS.get('work_id_prefix', ''), self.id)

    def is_modification(self):
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

    def __str__(self):
        return '{} {} ({})'.format(
            self.work_id,
            self.title.upper(),
            ' / '.join(w.last_name.upper() for w in self.writers.all()))


    def get_dict(self, normalize=True):
        """Create a data structure that can be serialized as JSON.

        Returns:
            dict: JSON-serializable data structure
        """

        j = {
            'work_title': self.title,
            'version_type': {
                'code': 'MOD',
                'name': 'Modified Version of a musical work',
                'original_work': {
                    'work_title': self.original_title,
                }
            } if self.original_title else {
                'code': 'ORI',
                'name': 'Original Work',
            },
            'iswc': self.iswc,
            'other_titles': [
                at.get_dict() for at in self.alternatetitle_set.all()],

            'affiliation_types': {},
            'agreement_types': {},
            'artists': {},
            'labels': {},
            'libraries': {},
            'organizations': {},
            'territories': {},
            'publishers': {
                SETTINGS['publisher_id']: {
                    'name' : SETTINGS['publisher_name'],
                    'ipi_name': SETTINGS['publisher_ipi_name'],
                    'ipi_base': SETTINGS.get('publisher_ipi_base'),
                    'affiliations': [{
                        'organization': {
                            'code': SETTINGS['publisher_pr_society'],
                            'name': SOCIETY_DICT.get(
                                SETTINGS['publisher_pr_society']
                            ).split(',')[0],
                        },
                        'affiliation_type': {
                            'code': 'PR',
                            'name': 'Performance Rights'
                        },
                        'territory': {
                            'code': '2136',
                            'tis_code': '2136',
                            'name': 'World'
                        }
                    }]
                }
            },
            'writers': {},
            'origin': (
                self.library_release.get_origin_dict() if self.library_release
                else None),
            'recordings': {},
            'writers_for_work': [],
            'artists_for_work': [],
        }
        if SETTINGS.get('publisher_mr_society'):
            j['publishers'][SETTINGS['publisher_id']]['affiliations'].append({
                'organization': {
                    'code': SETTINGS['publisher_mr_society'],
                    'name': SOCIETY_DICT.get(
                        SETTINGS['publisher_mr_society']
                    ).split(',')[0],
                },
                'affiliation_type': {
                    'code': 'MR',
                    'name': 'Mechanical Rights'
                },
                'territory': {
                    'code': '2136',
                    'tis_code': '2136',
                    'name': 'World'
                }
            })
        if SETTINGS.get('publisher_sr_society'):
            j['publishers'][SETTINGS['publisher_id']]['affiliations'].append({
                'organization': {
                    'code': SETTINGS['publisher_sr_society'],
                    'name': SOCIETY_DICT.get(
                        SETTINGS['publisher_sr_society']
                    ).split(',')[0],
                },
                'affiliation_type': {
                    'code': 'SR',
                    'name': 'Synchronization Rights'
                },
                'territory': {
                    'code': '2136',
                    'tis_code': '2136',
                    'name': 'World'
                }
            })

        if normalize:
            for aff in j['publishers'][SETTINGS['publisher_id']]['affiliations']:
                org = aff['organization']
                code = org.pop('code')
                j['organizations'].update(
                    {code: org})
                aff['organization'] = code
                typ = aff['affiliation_type']
                code = typ.pop('code')
                j['affiliation_types'].update(
                    {code: org})
                aff['organization'] = code
                ter = aff['territory']
                code = ter.pop('code')
                j['territories'].update(
                    {code: ter})
                aff['territory'] = code


        if normalize and self.library_release:
            key = next(iter(j['origin']))
            l = j['origin'][key]['library']
            j['libraries'].update(j['origin'][key]['library'])
            j['origin'][key]['library'] = \
                next(iter(j['origin'][key]['library']))

        for wiw in self.artistinwork_set.all():
            d = wiw.get_dict()
            a = d.get('artist', None)
            if normalize:
                d['artist'] = next(iter(a))
                j['artists'].update(a)
            j['artists_for_work'].append(d)

        for wiw in self.writerinwork_set.all():
            d = wiw.get_dict()
            w = d.get('writer', None)
            if not w:
                continue
            for aff in w[next(iter(w))].get('affiliations', []):
                org = aff.get('organization')
                if not org:
                    continue
                if normalize:
                    code = org.pop('code')
                    j['organizations'].update(
                        {code: org})
                    aff['organization'] = code
            if normalize:
                d['writer'] = next(iter(w))
                for pwr in d.get('publishers_for_writer', []):
                    agreement = pwr.get('agreement')
                    if not agreement:
                        continue
                    org = agreement['recipient_organization']
                    j['organizations'].update(
                        {org['code']: {'name': org['name']}})
                    agreement['recipient_organization'] = \
                        agreement['recipient_organization']['code']
                    agreement_type = agreement['agreement_type']
                    code = agreement_type['code']
                    agreement['agreement_type'] = agreement_type.pop('code')
                    j['agreement_types'].update({
                        code: agreement_type})

            if normalize:
                j['writers'].update(w)
            j['writers_for_work'].append(d)

        for recording in self.recordings.all():
            d = recording.get_dict(with_releases=True)
            if normalize:
                key = next(iter(d))
                rec = d[key]
                artist = rec['recording_artist']
                if artist:
                    j['artists'].update(artist)
                    d[key]['recording_artist'] = next(iter(artist))
                label = rec['record_label']
                if label:
                    j['labels'].update(label)
                    d[key]['record_label'] = next(iter(label))
                tracks = rec['tracks']
                for track in tracks:
                    rel = track['release']
                    rel_key = next(iter(rel))
                    label = rel[rel_key]['release_label']
                    if label:
                        j['labels'].update(label)
                        rel[rel_key]['release_label'] = next(iter(label))

        j['recordings'].update(d)

        return {self.work_id: j}


class AlternateTitle(TitleBase):
    """Concrete class for alternate titles.

    Attributes:
        work (django.db.models.ForeignKey): Foreign key to Work model
    """

    work = models.ForeignKey(Work, on_delete=models.CASCADE)
    suffix = models.BooleanField(
        default=False,
        help_text='Select if this title is only a suffix to the main title.')

    class Meta:
        unique_together = (('work', 'title'),)
        ordering = ('-suffix', 'title')

    def get_dict(self):
        """Create a data structure that can be serialized as JSON.

        Returns:
            dict: JSON-serializable data structure
        """
        return {
            'alternate_title': str(self),
            'title_type': {
                'code': 'AT',
                'name': 'Alternative Title',
            },
        }


    def __str__(self):
        if self.suffix:
            return '{} {}'.format(self.work.title, self.title)
        return self.title


class ArtistInWork(models.Model):
    """Artist performing the work (live in CWR 3).

    Attributes:
        artist (django.db.models.ForeignKey): FK to Artist
        work (django.db.models.ForeignKey): FK to Work
    """

    work = models.ForeignKey(Work, on_delete=models.CASCADE)
    artist = models.ForeignKey(Artist, on_delete=models.PROTECT)

    class Meta:
        verbose_name = 'Performing artist'
        verbose_name_plural = 'Performing artists (not mentioned in recordings section)'
        unique_together = (('work', 'artist'),)
        ordering = ('artist__last_name', 'artist__first_name')

    def __str__(self):
        return str(self.artist)

    def get_dict(self):
        return {'artist': self.artist.get_dict()}


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

    def get_dict(self):
        """Create a data structure that can be serialized as JSON.

        Returns:
            dict: JSON-serializable data structure
        """

        j = {
            'writer': self.writer.get_dict() if self.writer else None,
            'controlled': self.controlled,
            'relative_share': str(self.relative_share / 100),
            'capacity': {
                'code': self.capacity.strip(),
                'name': self.get_capacity_display()
            } if self.capacity else None,
            'publishers_for_writer': [{
                'publisher': SETTINGS['publisher_id'],
                'agreement': {
                    'recipient_organization': {
                        'code': SETTINGS['publisher_pr_society'],
                        'name': SOCIETY_DICT[SETTINGS['publisher_pr_society']].split(',')[0],
                    },
                    'recipient_agreement_number': self.saan,
                    'agreement_type': {
                        'code': 'OS',
                        'name': 'Original Specific',
                    }
                } if (self.saan and self.saan != self.writer.saan) else {
                    'recipient_organization': {
                        'code': SETTINGS['publisher_pr_society'],
                        'name': SOCIETY_DICT[SETTINGS['publisher_pr_society']].split(',')[0],
                    },
                    'recipient_agreement_number': self.writer.saan,
                    'agreement_type': {
                        'code': 'OG',
                        'name': 'Original General',
                    }
                } if self.writer.saan else None
            }] if self.controlled else [],
        }
        return j


class Recording(models.Model):
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
        verbose_name_plural = '   Recordings'
        ordering = ('-id',)

    recording_title = models.CharField(
        blank=True,
        max_length=60, validators=(
            CWRFieldValidator('work_title'),))
    recording_title_suffix = models.BooleanField(
        default=False,
        help_text='A suffix to the WORK title.')
    version_title = models.CharField(
        blank=True,
        max_length=60, validators=(
            CWRFieldValidator('work_title'),))
    version_title_suffix = models.BooleanField(
        default=False,
        help_text='A suffix to the RECORDING title.')
    release_date = models.DateField(blank=True, null=True)
    duration = models.DurationField(blank=True, null=True)
    isrc = models.CharField(
        'ISRC', max_length=15, blank=True, null=True, unique=True,
        validators=(CWRFieldValidator('isrc'),))
    record_label = models.ForeignKey(
        Label,
        verbose_name='Record label',
        null=True, blank=True,
        on_delete=models.PROTECT
    )
    work = models.ForeignKey(Work, on_delete=models.CASCADE, related_name='recordings')
    artist = models.ForeignKey(
        Artist, on_delete=models.PROTECT, blank=True, null=True,
        verbose_name='Recording Artist')

    releases = models.ManyToManyField(Release, through='Track')

    def clean_fields(self, *args, **kwargs):
        if self.isrc:
            # Removing all characters added for readability
            self.isrc = self.isrc.replace('-', '').replace('.', '')
        return super().clean_fields(*args, **kwargs)

    @property
    def complete_recording_title(self):
        if self.recording_title_suffix:
            return '{} {}'.format(self.work.title, self.recording_title)
        return self.recording_title

    @property
    def complete_version_title(self):
        if self.version_title_suffix:
            return '{} {}'.format(
                self.complete_recording_title or self.work.title,
                self.version_title)
        return self.version_title

    def __str__(self):
        return (
            self.complete_version_title or
            self.recording_title or
            self.work.title)

    @property
    def recording_id(self):
        """Create Recording ID used in registrations

        Returns:
            str: Internal Recording ID
        """
        if self.id is None:
            return ''
        return '{}R{:06}'.format(SETTINGS.get('work_id_prefix', ''), self.id)


    def get_dict(self, with_releases=False):
        """Create a data structure that can be serialized as JSON.

        Returns:
            dict: JSON-serializable data structure
        """
        j = {
            'recording_title': (
                self.complete_recording_title or self.work.title),
            'version_title': self.complete_version_title,
            'release_date': (
                self.release_date.strftime('%Y%m%d') if self.release_date
                else None),
            'duration': self.duration.strftime('%H%M%S') if self.duration
                else None,
            'isrc': self.isrc,
            'recording_artist': self.artist.get_dict() if self.artist else None,
            'record_label': (
                self.record_label.get_dict() if self.record_label else None),
        }
        if with_releases:
            j['tracks'] = []
            for track in self.tracks.all():
                d = track.release.get_dict()
                if not d:
                    continue
                j['tracks'].append({
                    'cut_number': track.cut_number,
                    'release': d,
                })
        return {self.recording_id: j}


class Track(models.Model):
    class Meta:
        unique_together = (('recording', 'release'), ('release', 'cut_number'))
        ordering = ('release', 'cut_number',)

    recording = models.ForeignKey(
        Recording, on_delete=models.PROTECT, related_name='tracks')
    release = models.ForeignKey(
        Release, on_delete=models.PROTECT, related_name='tracks')
    cut_number = models.PositiveSmallIntegerField(
        blank=True, null=True,
        validators=(MinValueValidator(1), MaxValueValidator(9999)))


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
    description = models.CharField('Internal Note', blank=True, max_length=60)

    @property
    def filename(self):
        """Return proper CWR filename.

        Returns:
            str: CWR file name
        """
        return 'CW{}{:04}{}_000.V21'.format(
            self.year,
            self.num_in_year,
            SETTINGS.get('publisher_id'))

    def __str__(self):
        return self.filename

    @staticmethod
    def get_record(key, record):
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

    def yield_lines(self):
        """Yield CWR transaction records (rows/lines) for works

        Args:
            works (query): :class:`.models.Work` query

        Yields:
            str: CWR recors (row/line)
        """
        works = self.works.order_by('id',)
        works = works.select_related('firstrecording')
        works = works.prefetch_related('firstrecording__artist')
        works = works.prefetch_related('firstrecording__album_cd')
        works = works.prefetch_related(models.Prefetch(
            'writerinwork_set',
            queryset=WriterInWork.objects.order_by(
                '-controlled', 'id').prefetch_related('writer'),
            to_attr='wiws'))
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
            for wiw in work.wiws:
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
            for wiw in work.wiws:
                if not wiw.controlled:
                    continue
                w = wiw.writer
                record = dict(capacity=wiw.capacity,
                              share=controlled_writer_shares[w.id],
                              saan=wiw.saan or w.saan)
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
            for wiw in work.wiws:
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
                    'alternate_title': str(record)})
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
                release_title = ''
                release_label = ''
                if rec.album_cd:
                    release_date = release_date or rec.album_cd.release_date
                    release_title = release_title or rec.album_cd.release_title
                    release_label = rec.album_cd.release_label or record_label
                yield self.get_transaction_record('REC', {
                    'isrc': rec.isrc,
                    'duration': rec.duration,
                    'release_date': release_date,
                    'release_title': release_title,
                    'release_label': release_label
                })
            except ObjectDoesNotExist:
                pass
            try:
                album = work.firstrecording.album_cd
                if album and album.cd_identifier:
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
        self.cwr = ''.join(self.yield_lines())
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
        ordering = ('-date', '-id')

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
        ordering = ('-date', '-id')

    filename = models.CharField(max_length=60, editable=False)
    society_code = models.CharField(max_length=3, editable=False)
    society_name = models.CharField(max_length=45, editable=False)
    date = models.DateField(editable=False)
    report = models.TextField(editable=False)

    def __str__(self):
        return self.filename

