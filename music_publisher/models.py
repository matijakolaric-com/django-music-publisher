"""Concrete models.

They mostly inherit from classes in :mod:`.base`.

"""

from collections import OrderedDict, defaultdict
from datetime import datetime
from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.template import Context

from .base import (
    ArtistBase, IPIBase, LabelBase, LibraryBase, PersonBase, ReleaseBase,
    TitleBase, WriterBase,
)
from .cwr_templates import (
    TEMPLATES_21, TEMPLATES_22, TEMPLATES_30, TEMPLATES_31)
from .validators import CWRFieldValidator

SOCIETY_DICT = OrderedDict(settings.SOCIETIES)

WORLD_DICT = {
    'tis-a': '2WL',
    'tis-n': '2136',
    'name': 'World'
}


class Artist(ArtistBase):
    """Performing artist.
    """

    def get_dict(self):
        """Get the object in an internal dictionary format

        Returns:
            dict: internal dict format
        """
        return {
            'id': self.id,
            'code': self.artist_id,
            'last_name': self.last_name,
            'first_name': self.first_name or None,
            'isni': self.isni or None,
        }

    @property
    def artist_id(self):
        """Artist identifier

        Returns:
            str: Artist ID
        """
        return 'A{:06d}'.format(self.id)


class Label(LabelBase):
    """Music Label.
    """

    class Meta:
        verbose_name = 'Music Label'

    def __str__(self):
        return self.name.upper()

    @property
    def label_id(self):
        """Label identifier

        Returns:
            str: Label ID
        """
        return 'LA{:06d}'.format(self.id)

    def get_dict(self):
        """Get the object in an internal dictionary format

        Returns:
            dict: internal dict format
        """
        return {
            'id': self.id,
            'code': self.label_id,
            'name': self.name,
        }


class Library(LibraryBase):
    """Music Library.
    """

    class Meta:
        verbose_name = 'Music Library'
        verbose_name_plural = 'Music Libraries'
        ordering = ('name',)

    name = models.CharField(
        max_length=60, unique=True,
        validators=(CWRFieldValidator('library'),))

    def __str__(self):
        return self.name.upper()

    @property
    def library_id(self):
        """Library identifier

        Returns:
            str: Library ID
        """
        return 'LI{:06d}'.format(self.id)

    def get_dict(self):
        """Get the object in an internal dictionary format

        Returns:
            dict: internal dict format
        """
        return {
            'id': self.id,
            'code': self.library_id,
            'name': self.name,
        }


class Release(ReleaseBase):
    """Music Release (album / other product)

    Attributes:
        library (django.db.models.ForeignKey): Foreign key to \
        :class:`.models.Library`
        release_label (django.db.models.ForeignKey): Foreign key to \
        :class:`.models.Label`
        recordings (django.db.models.ManyToManyField): M2M to \
        :class:`.models.Recording` through :class:`.models.Track`
    """

    class Meta:
        verbose_name = 'Release'

    library = models.ForeignKey(
        Library, null=True, blank=True, on_delete=models.PROTECT)
    release_label = models.ForeignKey(
        Label, verbose_name='Release (album) label', null=True, blank=True,
        on_delete=models.PROTECT)
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
                return '{} ({})'.format(
                    (self.release_title or '<no title>').upper(),
                    self.release_label)
            return (self.release_title or '<no title>').upper()

    @property
    def release_id(self):
        """Release identifier.

        Returns:
            str: Release ID
        """
        return 'RE{:06d}'.format(self.id)

    def get_dict(self, with_tracks=False):
        """Get the object in an internal dictionary format

        Args:
            with_tracks (bool): add track data to the output

        Returns:
            dict: internal dict format

        """

        d = {
            'id': self.id,
            'code': self.release_id,
            'title':
                self.release_title or None,
            'date':
                self.release_date.strftime('%Y%m%d') if self.release_date
                else None,
            'label':
                self.release_label.get_dict() if self.release_label else None,
            'ean':
                self.ean,
        }
        if with_tracks:
            d['tracks'] = [track.get_dict() for track in self.tracks.all()]
        return d


class LibraryReleaseManager(models.Manager):
    """Manager for a proxy class :class:`.models.LibraryRelease`
    """

    def get_queryset(self):
        """Return only library releases

        Returns:
            django.db.models.query.QuerySet: Queryset with instances of \
            :class:`.models.LibraryRelease`
        """
        return super().get_queryset().filter(cd_identifier__isnull=False)

    def get_dict(self, qs):
        """Get the object in an internal dictionary format

        Args:
            qs (django.db.models.query.QuerySet)

        Returns:
            dict: internal dict format
        """
        return {
            'releases': [release.get_dict(with_tracks=True) for release in qs]
        }


class LibraryRelease(Release):
    """Proxy class for Library Releases (AKA Library CDs)

    Attributes:
        objects (LibraryReleaseManager): Database Manager
    """

    class Meta:
        proxy = True
        verbose_name = 'Library Release'
        verbose_name_plural = 'Library Releases'

    objects = LibraryReleaseManager()

    def clean(self):
        """Make sure that release title is required if one of the other \
        "non-library" fields is present.

        Raises:
            ValidationError: If not compliant.
        """
        if ((self.ean or self.release_date or self.release_label)
                and not self.release_title):
            raise ValidationError({
                'release_title': 'Required if other release data is set.'
            })

    def get_origin_dict(self):
        """Get the object in an internal dictionary format.

        This is used for work origin, not release data.

        Returns:
            dict: internal dict format
        """
        return {
            'origin_type': {
                'code': 'LIB',
                'name': 'Library Work'
            },
            'cd_identifier': self.cd_identifier,
            'library': self.library.get_dict()
        }


class CommercialReleaseManager(models.Manager):
    """Manager for a proxy class :class:`.models.CommercialRelease`
    """

    def get_queryset(self):
        """Return only commercial releases

        Returns:
            django.db.models.query.QuerySet: Queryset with instances of \
            :class:`.models.CommercialRelease`
        """
        return super().get_queryset().filter(cd_identifier__isnull=True)

    def get_dict(self, qs):
        """Get the object in an internal dictionary format

        Args:
            qs (django.db.models.query.QuerySet)

        Returns:
            dict: internal dict format
        """
        return {
            'releases': [release.get_dict(with_tracks=True) for release in qs]
        }


class CommercialRelease(Release):
    """Proxy class for Commercial Releases

    Attributes:
        objects (CommercialReleaseManager): Database Manager
    """

    class Meta:
        proxy = True
        verbose_name = 'Commercial Release'
        verbose_name_plural = 'Commercial Releases'

    objects = CommercialReleaseManager()


class Writer(WriterBase):
    """Writers.

    Attributes:
        original_publishing_agreement (django.db.models.ForeignKey): \
        Foreign key to :class:`.models.OriginalPublishingAgreement`
    """

    class Meta:
        ordering = ('last_name', 'first_name', 'ipi_name', '-id')
        verbose_name = 'Writer'
        verbose_name_plural = 'Writers'

    def __str__(self):
        name = super().__str__()
        if self.generally_controlled:
            return name + ' (*)'
        return name

    def clean(self, *args, **kwargs):
        """Check if writer who is controlled still has enough data."""
        super().clean(*args, **kwargs)
        if self.pk is None or self._can_be_controlled:
            return
        # A controlled writer requires more data, so once a writer is in
        # that role, it is not allowed to remove required data."""
        if self.writerinwork_set.filter(controlled=True).exists():
            raise ValidationError(
                'This writer is controlled in at least one work. ' +
                'Required fields are: Last name, IPI name and PR society. ' +
                'See "Writers" in the user manual.')

    @property
    def writer_id(self):
        """
        Writer ID for CWR

        Returns:
            str: formatted writer ID
        """
        return 'W{:06d}'.format(self.id)

    def get_dict(self):
        """Create a data structure that can be serialized as JSON.

        Returns:
            dict: JSON-serializable data structure
        """

        d = {
            'id': self.id,
            'code': self.writer_id,
            'first_name': self.first_name or None,
            'last_name': self.last_name or None,
            'ipi_name_number': self.ipi_name or None,
            'ipi_base_number': self.ipi_base or None,
            'affiliations': [],
        }
        if self.pr_society:
            d['affiliations'].append({
                'organization': {
                    'code': self.pr_society,
                    'name': self.get_pr_society_display().split(',')[0],
                },
                'affiliation_type': {
                    'code': 'PR',
                    'name': 'Performance Rights'
                },
                'territory': WORLD_DICT,
            })
        if self.mr_society:
            d['affiliations'].append({
                'organization': {
                    'code': self.mr_society,
                    'name': self.get_mr_society_display().split(',')[0],
                },
                'affiliation_type': {
                    'code': 'MR',
                    'name': 'Mechanical Rights'
                },
                'territory': WORLD_DICT,
            })
        if self.sr_society:
            d['affiliations'].append({
                'organization': {
                    'code': self.sr_society,
                    'name': self.get_sr_society_display().split(',')[0],
                },
                'affiliation_type': {
                    'code': 'SR',
                    'name': 'Synchronization Rights'
                },
                'territory': WORLD_DICT,
            })
        return d


class WorkManager(models.Manager):
    """Manager for class :class:`.models.Work`
    """

    def get_queryset(self):
        """
        Get an optimized queryset.

        Returns:
            django.db.models.query.QuerySet: Queryset with instances of \
            :class:`.models.Work`
        """
        return super().get_queryset().prefetch_related('writers')

    def get_dict(self, qs):
        """
        Return a dictionary with works from the queryset

        Args:
            qs(django.db.models.query import QuerySet)

        Returns:
            dict: dictionary with works

        """
        qs = qs.prefetch_related('alternatetitle_set')
        qs = qs.prefetch_related('writerinwork_set__writer')
        qs = qs.prefetch_related('artistinwork_set__artist')
        qs = qs.prefetch_related('library_release__library')
        qs = qs.prefetch_related('recordings__record_label')
        qs = qs.prefetch_related('recordings__artist')
        qs = qs.prefetch_related('recordings__tracks__release__library')
        qs = qs.prefetch_related('recordings__tracks__release__release_label')
        qs = qs.prefetch_related('workacknowledgement_set')

        works = []

        for work in qs:
            j = work.get_dict()
            works.append(j)

        return {
            'works': works,
        }


class Work(TitleBase):
    """Concrete class, with references to foreign objects.

    Attributes:
        _work_id (django.db.models.CharField): permanent work id, either \
        imported or fixed when exports are created
        iswc (django.db.models.CharField): ISWC
        original_title (django.db.models.CharField): title of the original \
            work, implies modified work
        release_label (django.db.models.ForeignKey): Foreign key to \
            :class:`.models.LibraryRelease`
        last_change (django.db.models.DateTimeField):
            when the last change was made to this object or any of the child
            objects, basically used in filtering
        artists (django.db.models.ManyToManyField):
            Artists performing the work
        writers (django.db.models.ManyToManyField):
            Writers who created the work
        objects (WorkManager): Database Manager
    """

    class Meta:
        verbose_name = 'Musical Work'
        ordering = ('-id',)
        permissions = (
            ('can_process_royalties', 'Can perform royalty calculations'),)

    @staticmethod
    def persist_work_ids(qs):
        for work in qs.filter(_work_id__isnull=True):
            work.work_id = work.work_id
            work.save()

    _work_id = models.CharField(
        'Work ID', max_length=14, blank=True, null=True, unique=True,
        editable=False,
        validators=(CWRFieldValidator('name'),))
    iswc = models.CharField(
        'ISWC', max_length=15, blank=True, null=True, unique=True,
        validators=(CWRFieldValidator('iswc'),))
    original_title = models.CharField(
        verbose_name='Title of original work',
        max_length=60, db_index=True, blank=True,
        help_text='Use only for modification of existing works.',
        validators=(CWRFieldValidator('work_title'),))
    library_release = models.ForeignKey(
        'LibraryRelease', on_delete=models.PROTECT, blank=True, null=True,
        related_name='works',
        verbose_name='Library release')
    last_change = models.DateTimeField(
        'Last Edited', editable=False, null=True)
    artists = models.ManyToManyField('Artist', through='ArtistInWork')
    writers = models.ManyToManyField('Writer', through='WriterInWork')

    objects = WorkManager()

    @property
    def work_id(self):
        """Create Work ID used in registrations.

        Returns:
            str: Internal Work ID
        """
        if self._work_id:
            return self._work_id
        if self.id is None:
            return ''
        return '{}{:06}'.format(settings.PUBLISHER_CODE, self.id)

    @work_id.setter
    def work_id(self, value):
        assert self._work_id is None  # this should not be called if set
        if value:
            self._work_id = value

    def is_modification(self):
        """
        Check if the work is a modification.

        Returns:
            bool: True if modification, False if original
        """
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
        return '{}: {} ({})'.format(
            self.work_id,
            self.title.upper(),
            ' / '.join(w.last_name.upper() for w in self.writers.distinct()))

    @staticmethod
    def get_publisher_dict():
        """Create data structure for the publisher.

        Returns:
            dict: JSON-serializable data structure
        """
        j = {
            'id': 1,
            'code': settings.PUBLISHER_CODE,
            'name': settings.PUBLISHER_NAME,
            'ipi_name_number': settings.PUBLISHER_IPI_NAME,
            'ipi_base_number': settings.PUBLISHER_IPI_BASE,
            'affiliations': [{
                'organization': {
                    'code': settings.PUBLISHER_SOCIETY_PR,
                    'name': SOCIETY_DICT.get(
                        settings.PUBLISHER_SOCIETY_PR,
                        ''
                    ).split(',')[0],
                },
                'affiliation_type': {
                    'code': 'PR',
                    'name': 'Performance Rights'
                },
                'territory': WORLD_DICT,
            }]
        }

        # append MR data to affiliations id needed
        if settings.PUBLISHER_SOCIETY_MR:
            j['affiliations'].append({
                'organization': {
                    'code': settings.PUBLISHER_SOCIETY_MR,
                    'name': SOCIETY_DICT.get(
                        settings.PUBLISHER_SOCIETY_MR,
                        ''
                    ).split(',')[0],
                },
                'affiliation_type': {
                    'code': 'MR',
                    'name': 'Mechanical Rights'
                },
                'territory': WORLD_DICT,
            })

        # append SR data to affiliations id needed
        if settings.PUBLISHER_SOCIETY_SR:
            j['affiliations'].append({
                'organization': {
                    'code': settings.PUBLISHER_SOCIETY_SR,
                    'name': SOCIETY_DICT.get(
                        settings.PUBLISHER_SOCIETY_SR,
                        ''
                    ).split(',')[0],
                },
                'affiliation_type': {
                    'code': 'SR',
                    'name': 'Synchronization Rights'
                },
                'territory': WORLD_DICT,
            })

        return j

    def get_dict(self, with_recordings=True):
        """Create a data structure that can be serialized as JSON.

        Normalize the structure if required.

        Returns:
            dict: JSON-serializable data structure
        """

        j = {
            'id': self.id,
            'code': self.work_id,
            'work_title': self.title,
            'last_change': self.last_change,
            'version_type': {
                'code': 'MOD',
                'name': 'Modified Version of a musical work',
            } if self.original_title else {
                'code': 'ORI',
                'name': 'Original Work',
            },
            'iswc': self.iswc,
            'other_titles': [
                at.get_dict() for at in self.alternatetitle_set.all()],

            'origin': (
                self.library_release.get_origin_dict() if self.library_release
                else None),
            'writers': [],
            'performing_artists': [],
            'original_works': [],
            'cross_references': []
        }

        if self.original_title:
            d = {'work_title': self.original_title}
            j['original_works'].append(d)

        # add data for (live) artists in work, normalize of required
        for aiw in self.artistinwork_set.all():
            d = aiw.get_dict()
            j['performing_artists'].append(d)

        # add data for writers in work, normalize of required
        for wiw in self.writerinwork_set.all():
            d = wiw.get_dict()
            j['writers'].append(d)

        if with_recordings:
            j['recordings'] = [
                recording.get_dict(with_releases=True)
                for recording in self.recordings.all()]

        # add cross references, currently only society work ids from ACKs
        for wa in self.workacknowledgement_set.all():
            if not wa.remote_work_id:
                continue
            d = wa.get_dict()
            j['cross_references'].append(d)

        return j


class AlternateTitle(TitleBase):
    """Concrete class for alternate titles.

    Attributes:
        work (django.db.models.ForeignKey): Foreign key to Work model
        suffix (django.db.models.BooleanField): implies that the title should\
            be appended to the work title
    """

    work = models.ForeignKey(Work, on_delete=models.CASCADE)
    suffix = models.BooleanField(
        default=False,
        help_text='Select if this title is only a suffix to the main title.')

    class Meta:
        unique_together = (('work', 'title'),)
        ordering = ('-suffix', 'title')
        verbose_name = 'Alternative Title'

    def get_dict(self):
        """Create a data structure that can be serialized as JSON.

        Returns:
            dict: JSON-serializable data structure
        """
        return {
            'title': str(self),
            'title_type': {
                'code': 'AT',
                'name': 'Alternative Title',
            },
        }

    def __str__(self):
        if self.suffix:
            return '{} {}'.format(self.work.title.upper(), self.title.upper())
        return super().__str__()


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
        verbose_name_plural = \
            'Performing artists (not mentioned in recordings section)'
        unique_together = (('work', 'artist'),)
        ordering = ('artist__last_name', 'artist__first_name')

    def __str__(self):
        return str(self.artist)

    def get_dict(self):
        """

        Returns:
            dict: taken from :meth:`models.Artist.get_dict`
        """
        return {'artist': self.artist.get_dict()}


class WriterInWork(models.Model):
    """Writers who created this work.

    At least one writer in work must be controlled.
    Sum of relative shares must be (roughly) 100%.
    Capacity is limited to roles for original writers.

    Attributes:
        work (django.db.models.ForeignKey): FK to Work
        writer (django.db.models.ForeignKey): FK to Writer
        saan (django.db.models.CharField): Society-assigned agreement number
            between the writer and the original publisher, please note that
            this field is for SPECIFIC agreements, for a general agreement,
            use :attr:`.base.IPIBase.saan`
        controlled (django.db.models.BooleanField): A complete mistery field
        relative_share (django.db.models.DecimalField): Initial split among
            writers, prior to publishing
        capacity (django.db.models.CharField): Role of the writer in this work
        publisher_fee (django.db.models.DecimalField): Percentage of royalties
            kept by publisher
    """

    class Meta:
        verbose_name = 'Writer in Work'
        verbose_name_plural = 'Writers in Work'
        unique_together = (('work', 'writer', 'controlled'),)
        ordering = (
            '-controlled', 'writer__last_name', 'writer__first_name', '-id')
    ROLES = (
        ('CA', 'Composer&Lyricist'),
        ('C ', 'Composer'),
        ('A ', 'Lyricist'),
        ('AR', 'Arranger'),
        ('AD', 'Adaptor'),
        ('TR', 'Translator'))

    work = models.ForeignKey(
        Work, on_delete=models.CASCADE)
    writer = models.ForeignKey(
        Writer, on_delete=models.PROTECT, blank=True, null=True)
    saan = models.CharField(
        'Society-assigned specific agreement number',
        help_text='Use this field for specific agreements only.\n'
                  'For general agreements use the field in the Writer form.',
        max_length=14, blank=True, null=True,
        validators=(CWRFieldValidator('saan'),), )
    controlled = models.BooleanField(default=False)
    relative_share = models.DecimalField(
        'Manuscript share', max_digits=5, decimal_places=2)
    capacity = models.CharField(
        'Role',
        max_length=2, blank=True, choices=ROLES)
    publisher_fee = models.DecimalField(
        max_digits=5, decimal_places=2, blank=True, null=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text=(
            'Percentage of royalties kept by the publisher,\n'
            'in a specific agreement.'))

    def __str__(self):
        return str(self.writer)

    def clean_fields(self, *args, **kwargs):
        """Turn SAAN into uppercase.

        Args:
            *args: passing through
            **kwargs: passing through

        Returns:
            str: SAAN in uppercase
        """
        if self.saan:
            self.saan = self.saan.upper()
        return super().clean_fields(*args, **kwargs)

    def clean(self):
        """Make sure that controlled writers have all the required data.

        Also check that writers that are not controlled do not have data
        that can not apply to them."""

        if (self.writer and
                self.writer.generally_controlled and
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
                    d['writer'] = (
                        'IPI name and PR society must be set. '
                        'See "Writers" in the user manual')
                if (settings.REQUIRE_SAAN and
                        not self.writer.generally_controlled and
                        not self.saan):
                    d['saan'] = \
                        'Must be set. (controlled, no general agreement)'
                if (settings.REQUIRE_PUBLISHER_FEE and
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

    def get_agreement_dict(self):
        """Get agreement dictionary for this writer in work."""

        pub_pr_soc = settings.PUBLISHER_SOCIETY_PR
        pub_pr_name = SOCIETY_DICT.get(pub_pr_soc, '').split(',')[0]

        if not self.controlled or not self.writer:
            return None
        if self.writer.generally_controlled and not self.saan:
            # General
            return {
                'recipient_organization': {
                    'code': pub_pr_soc,
                    'name': pub_pr_name,
                },
                'recipient_agreement_number': self.writer.saan,
                'agreement_type': {
                    'code': 'OG', 'name': 'Original General',
                }
            }
        else:
            return {
                'recipient_organization': {
                    'code': pub_pr_soc,
                },
                'recipient_agreement_number': self.saan,
                'agreement_type': {
                    'code': 'OS',
                    'name': 'Original Specific',
                }
            }

    def get_dict(self):
        """Create a data structure that can be serialized as JSON.

        Returns:
            dict: JSON-serializable data structure
        """

        j = {
            'writer': self.writer.get_dict() if self.writer else None,
            'controlled': self.controlled,
            'relative_share': str(self.relative_share / 100),
            'writer_role': {
                'code': self.capacity.strip(),
                'name': self.get_capacity_display()
            } if self.capacity else None,
            'original_publishers': [{
                'publisher': self.work.get_publisher_dict(),
                'publisher_role': {
                    'code': 'E',
                    'name': 'Original publisher'
                },
                'agreement': self.get_agreement_dict()
            }] if self.controlled else [],
        }
        return j


class Recording(models.Model):
    """Recording.

    Attributes:
        release_date (django.db.models.DateField): Recording Release Date
        duration (django.db.models.TimeField): Recording Duration
        isrc (django.db.models.CharField):
            International Standard Recording Code
        record_label (django.db.models.CharField): Record Label
    """

    class Meta:
        verbose_name = 'Recording'
        verbose_name_plural = 'Recordings'
        ordering = ('-id',)

    recording_title = models.CharField(
        blank=True, max_length=60,
        validators=(CWRFieldValidator('work_title'),))
    recording_title_suffix = models.BooleanField(
        default=False, help_text='A suffix to the WORK title.')
    version_title = models.CharField(
        blank=True, max_length=60,
        validators=(CWRFieldValidator('work_title'),))
    version_title_suffix = models.BooleanField(
        default=False, help_text='A suffix to the RECORDING title.')
    release_date = models.DateField(blank=True, null=True)
    duration = models.DurationField(blank=True, null=True)
    isrc = models.CharField(
        'ISRC', max_length=15, blank=True, null=True, unique=True,
        validators=(CWRFieldValidator('isrc'),))
    record_label = models.ForeignKey(
        Label, verbose_name='Record label',
        null=True, blank=True, on_delete=models.PROTECT)
    work = models.ForeignKey(
        Work, on_delete=models.CASCADE, related_name='recordings')
    artist = models.ForeignKey(
        Artist, verbose_name='Recording Artist',
        on_delete=models.PROTECT, blank=True, null=True)

    releases = models.ManyToManyField(Release, through='Track')

    def clean_fields(self, *args, **kwargs):
        """
        ISRC cleaning, just removing dots and dashes.

        Args:
            *args: may be used in upstream
            **kwargs: may be used in upstream

        Returns:
            return from :meth:`django.db.models.Model.clean_fields`

        """
        if self.isrc:
            # Removing all characters added for readability
            self.isrc = self.isrc.replace('-', '').replace('.', '')
        return super().clean_fields(*args, **kwargs)

    @property
    def complete_recording_title(self):
        """
        Return complete recording title.

        Returns:
            str
        """
        if self.recording_title_suffix:
            return '{} {}'.format(
                self.work.title, self.recording_title).strip()
        return self.recording_title

    @property
    def complete_version_title(self):
        """
        Return complete version title.

        Returns:
            str
        """
        if self.version_title_suffix:
            return '{} {}'.format(
                self.complete_recording_title or self.work.title,
                self.version_title).strip()
        return self.version_title

    def __str__(self):
        """Return the most precise type of title"""
        return (
            self.complete_version_title if self.version_title else
            self.complete_recording_title if self.recording_title else
            self.work.title)

    @property
    def recording_id(self):
        """Create Recording ID used in registrations

        Returns:
            str: Internal Recording ID
        """
        if self.id is None:
            return ''
        return '{}{:06}R'.format(settings.PUBLISHER_CODE, self.id)

    def get_dict(self, with_releases=False, with_work=True):
        """Create a data structure that can be serialized as JSON.

        Args:
            with_releases (bool): add releases data (through tracks)
            with_work (bool): add work data

        Returns:
            dict: JSON-serializable data structure

        """
        j = {
            'id':
                self.id,
            'code':
                self.recording_id,
            'recording_title':
                self.complete_recording_title or self.work.title,
            'version_title':
                self.complete_version_title,
            'release_date':
                self.release_date.strftime('%Y%m%d') if self.release_date
                else None,
            'duration':
                str(self.duration).replace(':', '') if self.duration
                else None,
            'isrc':
                self.isrc,
            'recording_artist':
                self.artist.get_dict() if self.artist else None,
            'record_label':
                self.record_label.get_dict() if self.record_label else None,
        }
        if with_releases:
            j['tracks'] = []
            for track in self.tracks.all():
                d = track.release.get_dict()
                j['tracks'].append({
                    'release': d,
                    'cut_number': track.cut_number,
                })
        if with_work:
            j['works'] = [{'work': self.work.get_dict(with_recordings=False)}]
        return j


class Track(models.Model):
    """Track, a recording on a release."""

    class Meta:
        verbose_name = 'Track'
        unique_together = (('recording', 'release'), ('release', 'cut_number'))
        ordering = ('release', 'cut_number',)

    recording = models.ForeignKey(
        Recording, on_delete=models.PROTECT, related_name='tracks')
    release = models.ForeignKey(
        Release, on_delete=models.PROTECT, related_name='tracks')
    cut_number = models.PositiveSmallIntegerField(
        blank=True, null=True,
        validators=(MinValueValidator(1), MaxValueValidator(9999)))

    def get_dict(self):
        return {
            'cut_number': self.cut_number,
            'recording': self.recording.get_dict(
                with_releases=False, with_work=True)
        }


class CWRExport(models.Model):
    """Export in CWR format.

    Common Works Registration format is a standard format for registration of
    musical works world-wide. Exports are available in CWR 2.1 revision 8 and
    CWR 3.0 (experimental).

    Attributes:
        nwr_rev (django.db.models.CharField): choice field where user can
            select which version and type of CWR it is
        cwr (django.db.models.TextField): contents of CWR file
        year (django.db.models.CharField): 2-digit year format
        num_in_year (django.db.models.PositiveSmallIntegerField): \
        CWR sequential number in a year
        works (django.db.models.ManyToManyField): included works
        description (django.db.models.CharField): internal note

    """

    class Meta:
        verbose_name = 'CWR Export'
        verbose_name_plural = 'CWR Exports'
        ordering = ('-id',)

    nwr_rev = models.CharField(
        'CWR version/type', max_length=3, db_index=True, default='NWR',
        choices=(
            ('NWR', 'CWR 2.1: New work registrations'),
            ('REV', 'CWR 2.1: Revisions of registered works'),
            ('NW2', 'CWR 2.2: New work registrations'),
            ('RE2', 'CWR 2.2: Revisions of registered works'),
            ('WRK', 'CWR 3.0: Work registration'),
            ('ISR', 'CWR 3.0: ISWC request (EDI)'),
            ('WR1', 'CWR 3.1 DRAFT: Work registration'),
        ))
    cwr = models.TextField(blank=True, editable=False)
    year = models.CharField(
        max_length=2, db_index=True, editable=False, blank=True)
    num_in_year = models.PositiveSmallIntegerField(default=0)
    works = models.ManyToManyField(Work, related_name='cwr_exports')
    description = models.CharField('Internal Note', blank=True, max_length=60)

    @property
    def version(self):
        """Return CWR version."""
        if self.nwr_rev in ['WRK', 'ISR']:
            return '30'
        elif self.nwr_rev == 'WR1':
            return '31'
        elif self.nwr_rev in ['NW2', 'RE2']:
            return '22'
        return '21'

    @property
    def filename(self):
        """Return CWR file name.

        Returns:
            str: CWR file name
        """
        if self.version in ['30', '31']:
            return self.filename3
        return self.filename2

    @property
    def filename3(self):
        """Return proper CWR 3.x filename.

        Format is: CWYYnnnnSUB_REP_VM - m - r.EXT

        Returns:
            str: CWR file name
        """
        if self.version == '30':
            minor_version = '0-0'
        else:
            minor_version = '1-0'
        if self.nwr_rev == 'ISR':
            ext = 'ISR'
        else:
            ext = 'SUB'
        return 'CW{}{:04}{}_0000_V3-{}.{}'.format(
            self.year,
            self.num_in_year,
            settings.PUBLISHER_CODE,
            minor_version,
            ext)

    @property
    def filename2(self):
        """Return proper CWR 2.x filename.

        Returns:
            str: CWR file name
        """
        return 'CW{}{:04}{}_000.V{}'.format(
            self.year,
            self.num_in_year,
            settings.PUBLISHER_CODE,
            self.version)

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
        if self.version == '30':
            template = TEMPLATES_30.get(key)
        elif self.version == '31':
            template = TEMPLATES_31.get(key)
        else:
            if self.version == '22':
                tdict = TEMPLATES_22
            else:
                tdict = TEMPLATES_21
            if (
                    key == 'HDR' and
                    len(settings.PUBLISHER_IPI_NAME.lstrip('0')) > 9
            ):
                # CWR 2.1 revision 8 "hack" for 10+ digit IPI name numbers
                template = tdict.get('HDR_8')
            else:
                template = tdict.get(key)
        record.update({'settings': settings})
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
        if line:
            self.record_count += 1
            self.record_sequence += 1
        return line

    def yield_iswc_request_lines(self, works):
        """Yield lines for an ISR (ISWC request) in CWR 3.x"""

        for work in works:

            # ISR
            self.record_sequence = 0
            if work['iswc']:
                work['indicator'] = 'U'
            yield self.get_transaction_record('ISR', work)

            # WRI
            reported = set()
            for wiw in work['writers']:
                w = wiw['writer']
                if not w:
                    continue  # goes to OWR
                tup = (w['code'], wiw['writer_role']['code'])
                if tup in reported:
                    continue
                reported.add(tup)
                w.update({
                    'writer_role': wiw['writer_role']['code'],
                })
                yield self.get_transaction_record('WRI', w)

            self.transaction_count += 1

    def yield_publisher_lines(self, controlled_relative_share):
        """Yield SPU/SPT lines.

        Args:
            controlled_relative_share (Decimal): sum of manuscript shares \
            for controlled writers

        Yields:
              str: CWR record (row/line)
        """
        yield self.get_transaction_record(
            'SPU', {'share': controlled_relative_share})
        if controlled_relative_share:
            yield self.get_transaction_record(
                'SPT', {'share': controlled_relative_share})

    def yield_registration_lines(self, works):
        """Yield lines for CWR registrations (WRK in 3.x, NWR and REV in 2.x)

        Args:
            works (list): list of work dicts

        Yields:
            str: CWR record (row/line)
        """
        for work in works:

            # WRK
            self.record_sequence = 0
            if self.version == '22':
                if self.nwr_rev == 'NW2':
                    record_type = 'NWR'
                elif self.nwr_rev == 'RE2':
                    record_type = 'REV'
            else:
                record_type = self.nwr_rev

            d = {
                'record_type': record_type,
                'code': work['code'],
                'work_title': work['work_title'],
                'iswc': work['iswc'],
                'recorded_indicator': 'Y' if work['recordings'] else 'U',
                'version_type': (
                    'MOD   UNSUNS'
                    if work['version_type']['code'] == 'MOD' else
                    'ORI         ')
            }
            yield self.get_transaction_record('WRK', d)

            # SPU, SPT
            controlled_relative_share = Decimal(0)  # total pub share
            other_publisher_share = Decimal(0)  # used for co-publishing
            controlled_writer_ids = set()  # used for co-publishing
            copublished_writer_ids = set()  # used for co-publishing
            controlled_shares = defaultdict(Decimal)
            for wiw in work['writers']:
                if wiw['controlled']:
                    controlled_writer_ids.add(wiw['writer']['code'])
            for wiw in work['writers']:
                writer = wiw['writer']
                share = Decimal(wiw['relative_share'])
                if wiw['controlled']:
                    key = writer['code']
                    controlled_relative_share += share
                    controlled_shares[key] += share
                elif (writer and writer['code'] in controlled_writer_ids):
                    key = writer['code']
                    copublished_writer_ids.add(key)
                    other_publisher_share += share
                    controlled_shares[key] += share
            yield from self.yield_publisher_lines(controlled_relative_share)
            # OPU, co-publishing only
            if other_publisher_share:
                yield self.get_transaction_record(
                    'OPU', {'sequence': 2, 'share': other_publisher_share})
                yield self.get_transaction_record(
                    'OPT', {'share': other_publisher_share})

            # SWR, SWT, PWR
            for wiw in work['writers']:
                if not wiw['controlled']:
                    continue  # goes to OWR
                w = wiw['writer']
                agr = wiw['original_publishers'][0]['agreement']
                saan = agr['recipient_agreement_number'] if agr else None
                affiliations = w.get('affiliations', [])
                for aff in affiliations:
                    if aff['affiliation_type']['code'] == 'PR':
                        w['pr_society'] = aff['organization']['code']
                    elif aff['affiliation_type']['code'] == 'MR':
                        w['mr_society'] = aff['organization']['code']
                    elif aff['affiliation_type']['code'] == 'SR':
                        w['sr_society'] = aff['organization']['code']

                w.update({
                    'writer_role': wiw['writer_role']['code'],
                    'share': controlled_shares[w['code']],
                    'saan': saan,
                    'original_publishers': wiw['original_publishers']
                })
                yield self.get_transaction_record('SWR', w)
                if w['share']:
                    yield self.get_transaction_record('SWT', w)
                if w['share']:
                    yield self.get_transaction_record('MAN', w)
                w['publisher_sequence'] = 1
                yield self.get_transaction_record('PWR', w)
                if (self.version == '30' and other_publisher_share and w and
                        w['code'] in copublished_writer_ids):
                    w['publisher_sequence'] = 2
                    yield self.get_transaction_record(
                        'PWR', {
                            'code': w['code'],
                            'publisher_sequence': 2
                        })

            # OWR
            for wiw in work['writers']:
                if wiw['controlled']:
                    continue  # done in SWR
                writer = wiw['writer']
                if writer and writer['code'] in controlled_writer_ids:
                    continue  # co-publishing, already solved
                if writer:
                    w = wiw['writer']
                    affiliations = w.get('affiliations', [])
                    for aff in affiliations:
                        if aff['affiliation_type']['code'] == 'PR':
                            w['pr_society'] = aff['organization']['code']
                        elif aff['affiliation_type']['code'] == 'MR':
                            w['mr_society'] = aff['organization']['code']
                        elif aff['affiliation_type']['code'] == 'SR':
                            w['sr_society'] = aff['organization']['code']
                else:
                    w = {'writer_unknown_indicator': 'Y'}
                w.update({
                    'writer_role': wiw['writer_role']['code'] if wiw[
                        'writer_role']
                    else None,
                    'share': Decimal(wiw['relative_share'])
                })
                yield self.get_transaction_record('OWR', w)
                if w['share']:
                    yield self.get_transaction_record('OWT', w)
                if w['share']:
                    yield self.get_transaction_record('MAN', w)
                if self.version == '30' and other_publisher_share:
                    w['publisher_sequence'] = 2
                    yield self.get_transaction_record('PWR', w)

            # ALT
            alt_titles = set()
            for at in work['other_titles']:
                alt_titles.add(at['title'])
            for rec in work['recordings']:
                if rec['recording_title']:
                    alt_titles.add(rec['recording_title'])
                if rec['version_title']:
                    alt_titles.add(rec['version_title'])
            for alt_title in sorted(alt_titles):
                if alt_title == work['work_title']:
                    continue
                yield self.get_transaction_record('ALT', {
                    'alternate_title': alt_title
                })

            # VER
            if work['version_type']['code'] == 'MOD':
                yield self.get_transaction_record('OWK',
                                                  work['original_works'][0])

            # PER
            # artists can be recording and/or live, so let's see
            artists = {}
            for aiw in work['performing_artists']:
                artists.update({aiw['artist']['code']: aiw['artist']})
            for rec in work['recordings']:
                if not rec['recording_artist']:
                    continue
                artists.update({
                    rec['recording_artist']['code']: rec['recording_artist']
                })
            for artist in artists.values():
                yield self.get_transaction_record('PER', artist)

            # REC
            for rec in work['recordings']:
                if rec['recording_artist']:
                    rec['display_artist'] = '{} {}'.format(
                        rec['recording_artist']['first_name'] or '',
                        rec['recording_artist']['last_name'],
                    ).strip()[:60]
                if rec['isrc']:
                    rec['isrc_validity'] = 'Y'
                yield self.get_transaction_record('REC', rec)

            # ORN
            if work['origin']:
                yield self.get_transaction_record('ORN', {
                    'library': work['origin']['library']['name'],
                    'cd_identifier': work['origin']['cd_identifier'],
                })

            # XRF
            for xrf in work['cross_references']:
                yield self.get_transaction_record('XRF', xrf)
            self.transaction_count += 1

    def yield_lines(self):
        """Yield CWR transaction records (rows/lines) for works

        Args:
            works (query): :class:`.models.Work` query

        Yields:
            str: CWR record (row/line)
        """
        qs = self.works.order_by('id', )
        works = Work.objects.get_dict(qs)['works']

        self.record_count = self.record_sequence = self.transaction_count = 0

        yield self.get_record('HDR', {
            'creation_date': datetime.now(),
            'filename': self.filename,
            'publisher_ipi_name': settings.PUBLISHER_IPI_NAME,
            'publisher_name': settings.PUBLISHER_NAME,
            'publisher_code': settings.PUBLISHER_CODE,
        })

        if self.nwr_rev == 'NW2':
            yield self.get_record('GRH', {'transaction_type': 'NWR'})
        elif self.nwr_rev == 'RE2':    
            yield self.get_record('GRH', {'transaction_type': 'REV'})
        else:
            yield self.get_record('GRH', {'transaction_type': self.nwr_rev})

        if self.nwr_rev == 'ISR':
            lines = self.yield_iswc_request_lines(works)
        else:
            lines = self.yield_registration_lines(works)

        for line in lines:
            yield line

        yield self.get_record('GRT', {
            'transaction_count': self.transaction_count,
            'record_count': self.record_count + 2
        })
        yield self.get_record('TRL', {
            'transaction_count': self.transaction_count,
            'record_count': self.record_count + 4
        })

    def create_cwr(self):
        """Create CWR and save.
        """
        if self.cwr:
            return
        self.year = datetime.now().strftime('%y')
        nr = type(self).objects.filter(year=self.year)
        nr = nr.order_by('-num_in_year').first()
        if nr:
            self.num_in_year = nr.num_in_year + 1
        else:
            self.num_in_year = 1
        self.cwr = ''.join(self.yield_lines())
        self.save()
        Work.persist_work_ids(self.works)


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
        index_together = (('society_code', 'remote_work_id'),)

    TRANSACTION_STATUS_CHOICES = (
        ('CO', 'Conflict'),
        ('DU', 'Duplicate'),
        ('RA', 'Transaction Accepted'),
        ('AS', 'Registration Accepted'),
        ('AC', 'Registration Accepted with Changes'),
        ('SR', 'Registration Accepted - Ready for Payment'),
        ('CR', 'Registration Accepted with Changes - Ready for Payment'),
        ('RJ', 'Rejected'),
        ('NP', 'No Participation'),
        ('RC', 'Claim rejected'),
        ('NA', 'Rejected - No Society Agreement Number'),
        ('WA', 'Rejected - Wrong Society Agreement Number'),
    )

    work = models.ForeignKey(Work, on_delete=models.PROTECT)
    society_code = models.CharField(
        'Society', max_length=3, choices=settings.SOCIETIES)
    date = models.DateField()
    status = models.CharField(max_length=2, choices=TRANSACTION_STATUS_CHOICES)
    remote_work_id = models.CharField(
        'Remote work ID', max_length=20, blank=True, db_index=True)

    def get_dict(self):
        """
        Return dictionary with external work IDs.

        Returns:
            dict: JSON-serializable data structure
        """
        # if not self.remote_work_id:
        #     return None
        j = {
            'organization': {
                'code': self.society_code,
                'name': self.get_society_code_display().split(',')[0],
            },
            'identifier': self.remote_work_id,
        }
        return j


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
    cwr = models.TextField(blank=True, editable=False)

    def __str__(self):
        return self.filename


class DataImport(models.Model):
    """Importing basic work data from a CSV file.

    This class just acts as log, the actual logic is in :mod:`.data_import`.
    """

    class Meta:
        verbose_name = 'Data Import'
        ordering = ('-date', '-id')

    filename = models.CharField(max_length=60, editable=False)
    report = models.TextField(editable=False)
    date = models.DateTimeField(auto_now_add=True, editable=False)

    def __str__(self):
        return self.filename
