"""Concrete models.

They mostly inherit from classes in :mod:`.base`.

"""

import base64
import uuid
from collections import defaultdict
from datetime import datetime
from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.template import Context
from django.urls import reverse
from django.utils import timezone
from django.utils.duration import duration_string

from .base import (
    ArtistBase,
    IPIBase,
    LabelBase,
    LibraryBase,
    PersonBase,
    ReleaseBase,
    TitleBase,
    WriterBase,
    upload_to,
)
from .cwr_templates import (
    TEMPLATES_21,
    TEMPLATES_22,
    TEMPLATES_30,
    TEMPLATES_31,
)
from .societies import SOCIETIES, SOCIETY_DICT
from .validators import CWRFieldValidator

WORLD_DICT = {"tis-a": "2WL", "tis-n": "2136", "name": "World"}


class Artist(ArtistBase):
    """Performing artist."""

    def get_dict(self):
        """Get the object in an internal dictionary format

        Returns:
            dict: internal dict format
        """
        return {
            "id": self.id,
            "code": self.artist_id,
            "last_name": self.last_name,
            "first_name": self.first_name or None,
            "isni": self.isni or None,
        }

    @property
    def artist_id(self):
        """Artist identifier

        Returns:
            str: Artist ID
        """
        return "A{:06d}".format(self.id)


class Label(LabelBase):
    """Music Label."""

    class Meta:
        verbose_name = "Music Label"

    def __str__(self):
        return self.name.upper()

    @property
    def label_id(self):
        """Label identifier

        Returns:
            str: Label ID
        """
        return "LA{:06d}".format(self.id)

    def get_dict(self):
        """Get the object in an internal dictionary format

        Returns:
            dict: internal dict format
        """
        return {
            "id": self.id,
            "code": self.label_id,
            "name": self.name,
        }


class Library(LibraryBase):
    """Music Library."""

    class Meta:
        verbose_name = "Music Library"
        verbose_name_plural = "Music Libraries"
        ordering = ("name",)

    # name = models.CharField(
    #     max_length=60, unique=True,
    #     validators=(CWRFieldValidator('library'),))

    def __str__(self):
        return self.name.upper()

    @property
    def library_id(self):
        """Library identifier

        Returns:
            str: Library ID
        """
        return "LI{:06d}".format(self.id)

    def get_dict(self):
        """Get the object in an internal dictionary format

        Returns:
            dict: internal dict format
        """
        return {
            "id": self.id,
            "code": self.library_id,
            "name": self.name,
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
        verbose_name = "Release"

    library = models.ForeignKey(
        Library, null=True, blank=True, on_delete=models.PROTECT
    )
    release_label = models.ForeignKey(
        Label,
        verbose_name="Release (album) label",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
    )
    artist = models.ForeignKey(
        Artist,
        verbose_name="Display Artist",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        help_text="Leave empty if a compilation by different artists.",
    )
    recordings = models.ManyToManyField("Recording", through="Track")

    def __str__(self):
        if self.cd_identifier:
            if self.release_title:
                return "{}: {} ({})".format(
                    self.cd_identifier,
                    self.release_title.upper(),
                    self.library,
                )
            else:
                return "{} ({})".format(self.cd_identifier, self.library)
        else:
            if self.release_label:
                return "{} ({})".format(
                    (self.release_title or "<no title>").upper(),
                    self.release_label,
                )
            return (self.release_title or "<no title>").upper()

    @property
    def release_id(self):
        """Release identifier.

        Returns:
            str: Release ID
        """
        return "RE{:06d}".format(self.id)

    def get_dict(self, with_tracks=False):
        """Get the object in an internal dictionary format

        Args:
            with_tracks (bool): add track data to the output

        Returns:
            dict: internal dict format

        """
        title = self.release_title or None
        date = (
            self.release_date.strftime("%Y%m%d") if self.release_date else None
        )
        label = self.release_label.get_dict() if self.release_label else None
        artist = self.artist.get_dict() if self.artist else None
        d = {
            "id": self.id,
            "code": self.release_id,
            "title": title,
            "date": date,
            "label": label,
            "artist": artist,
            "ean": self.ean,
        }
        if with_tracks:
            d["tracks"] = [track.get_dict() for track in self.tracks.all()]
        return d


class LibraryReleaseManager(models.Manager):
    """Manager for a proxy class :class:`.models.LibraryRelease`"""

    def get_queryset(self):
        """Return only library releases

        Returns:
            django.db.models.query.QuerySet: Queryset with instances of \
            :class:`.models.LibraryRelease`
        """
        return (
            super()
            .get_queryset()
            .filter(cd_identifier__isnull=False, library__isnull=False)
        )

    def get_dict(self, qs):
        """Get the object in an internal dictionary format

        Args:
            qs (django.db.models.query.QuerySet)

        Returns:
            dict: internal dict format
        """
        return {
            "releases": [release.get_dict(with_tracks=True) for release in qs]
        }


class LibraryRelease(Release):
    """Proxy class for Library Releases (AKA Library CDs)

    Attributes:
        objects (LibraryReleaseManager): Database Manager
    """

    class Meta:
        proxy = True
        verbose_name = "Library Release"
        verbose_name_plural = "Library Releases"

    objects = LibraryReleaseManager()

    def clean(self):
        """Make sure that release title is required if one of the other \
        "non-library" fields is present.

        Raises:
            ValidationError: If not compliant.
        """
        title_required = self.ean or self.release_date or self.release_label
        if title_required and not self.release_title:
            raise ValidationError(
                {"release_title": "Required if other release data is set."}
            )

    def get_origin_dict(self):
        """Get the object in an internal dictionary format.

        This is used for work origin, not release data.

        Returns:
            dict: internal dict format
        """
        return {
            "origin_type": {"code": "LIB", "name": "Library Work"},
            "cd_identifier": self.cd_identifier,
            "library": self.library.get_dict(),
        }


class CommercialReleaseManager(models.Manager):
    """Manager for a proxy class :class:`.models.CommercialRelease`"""

    def get_queryset(self):
        """Return only commercial releases

        Returns:
            django.db.models.query.QuerySet: Queryset with instances of \
            :class:`.models.CommercialRelease`
        """
        return (
            super()
            .get_queryset()
            .filter(cd_identifier__isnull=True, library__isnull=True)
        )

    def get_dict(self, qs):
        """Get the object in an internal dictionary format

        Args:
            qs (django.db.models.query.QuerySet)

        Returns:
            dict: internal dict format
        """
        return {
            "releases": [release.get_dict(with_tracks=True) for release in qs]
        }


class CommercialRelease(Release):
    """Proxy class for Commercial Releases

    Attributes:
        objects (CommercialReleaseManager): Database Manager
    """

    class Meta:
        proxy = True
        verbose_name = "Commercial Release"
        verbose_name_plural = "Commercial Releases"

    objects = CommercialReleaseManager()


class PlaylistManager(models.Manager):
    """Manager for a proxy class :class:`.models.Playlist`"""

    def get_queryset(self):
        """Return only commercial releases

        Returns:
            django.db.models.query.QuerySet: Queryset with instances of \
            :class:`.models.CommercialRelease`
        """
        return (
            super()
            .get_queryset()
            .filter(cd_identifier__isnull=False, library__isnull=True)
        )

    def get_dict(self, qs):
        """Get the object in an internal dictionary format

        Args:
            qs (django.db.models.query.QuerySet)

        Returns:
            dict: internal dict format
        """
        return {
            "releases": [release.get_dict(with_tracks=True) for release in qs]
        }


class Playlist(Release):
    """Proxy class for Playlists

    Attributes:
        objects (CommercialReleaseManager): Database Manager
    """

    class Meta:
        proxy = True
        verbose_name = "Playlist"
        verbose_name_plural = "Playlists"

    objects = PlaylistManager()

    def __str__(self):
        return self.release_title or ""

    def clean(self, *args, **kwargs):
        if self.cd_identifier is None:
            self.cd_identifier = base64.urlsafe_b64encode(uuid.uuid4().bytes)
            self.cd_identifier = self.cd_identifier.decode().rstrip("=")[:15]
        return super().clean(*args, **kwargs)

    @property
    def secret_url(self):
        return reverse("secret_playlist", args=[self.cd_identifier])

    @property
    def secret_api_url(self):
        return reverse("playlist-detail", args=[self.cd_identifier])


class Writer(WriterBase):
    """Writers.

    Attributes:
        original_publishing_agreement (django.db.models.ForeignKey): \
        Foreign key to :class:`.models.OriginalPublishingAgreement`
    """

    class Meta:
        ordering = ("last_name", "first_name", "ipi_name", "-id")
        verbose_name = "Writer"
        verbose_name_plural = "Writers"

    def __str__(self):
        name = super().__str__()
        if self.generally_controlled:
            return name + " (*)"
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
                "This writer is controlled in at least one work. "
                + "Required fields are: Last name, IPI name and PR society. "
                + 'See "Writers" in the user manual.'
            )

    @property
    def writer_id(self):
        """
        Writer ID for CWR

        Returns:
            str: formatted writer ID
        """
        if self.id:
            return "W{:06d}".format(self.id)
        return ""

    def get_dict(self):
        """Create a data structure that can be serialized as JSON.

        Returns:
            dict: JSON-serializable data structure
        """

        d = {
            "id": self.id,
            "code": self.writer_id,
            "first_name": self.first_name or None,
            "last_name": self.last_name or None,
            "ipi_name_number": self.ipi_name or None,
            "ipi_base_number": self.ipi_base or None,
            "account_number": self.account_number,
            "affiliations": [],
        }
        if self.pr_society:
            d["affiliations"].append(
                {
                    "organization": {
                        "code": self.pr_society,
                        "name": self.get_pr_society_display().split(",")[0],
                    },
                    "affiliation_type": {
                        "code": "PR",
                        "name": "Performance Rights",
                    },
                    "territory": WORLD_DICT,
                }
            )
        if self.mr_society:
            d["affiliations"].append(
                {
                    "organization": {
                        "code": self.mr_society,
                        "name": self.get_mr_society_display().split(",")[0],
                    },
                    "affiliation_type": {
                        "code": "MR",
                        "name": "Mechanical Rights",
                    },
                    "territory": WORLD_DICT,
                }
            )
        if self.sr_society:
            d["affiliations"].append(
                {
                    "organization": {
                        "code": self.sr_society,
                        "name": self.get_sr_society_display().split(",")[0],
                    },
                    "affiliation_type": {
                        "code": "SR",
                        "name": "Synchronization Rights",
                    },
                    "territory": WORLD_DICT,
                }
            )
        return d


class WorkManager(models.Manager):
    """Manager for class :class:`.models.Work`"""

    def get_queryset(self):
        """
        Get an optimized queryset.

        Returns:
            django.db.models.query.QuerySet: Queryset with instances of \
            :class:`.models.Work`
        """
        return super().get_queryset().prefetch_related("writers")

    def get_dict_items(self, qs):
        """
        Yield dictionary items for works from the queryset

        Args:
            qs(django.db.models.query import QuerySet)

        Returns:
            dict: dictionary with works

        """
        qs = qs.prefetch_related("alternatetitle_set")
        qs = qs.prefetch_related("writerinwork_set__writer")
        qs = qs.prefetch_related("artistinwork_set__artist")
        qs = qs.prefetch_related("library_release__library")
        qs = qs.prefetch_related("recordings__record_label")
        qs = qs.prefetch_related("recordings__artist")
        qs = qs.prefetch_related("recordings__tracks__release__library")
        qs = qs.prefetch_related("recordings__tracks__release__release_label")
        qs = qs.prefetch_related("workacknowledgement_set")

        for work in qs:
            j = work.get_dict()
            yield j

    def get_dict(self, qs):
        """
        Return a dictionary with works from the queryset

        Args:
            qs(django.db.models.query import QuerySet)

        Returns:
            dict: dictionary with works

        """

        works = list(self.get_dict_items(qs))

        return {
            "works": works,
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
        verbose_name = "Musical Work"
        ordering = ("-id",)
        permissions = (
            ("can_process_royalties", "Can perform royalty calculations"),
        )

    @staticmethod
    def persist_work_ids(qs):
        qs = qs.prefetch_related("recordings")
        for work in qs.filter(_work_id__isnull=True):
            work.work_id = work.work_id
            work.save()
            for rec in work.recordings.all():
                if rec._recording_id is None:
                    rec.recording_id = rec.recording_id

    _work_id = models.CharField(
        "Work ID",
        max_length=14,
        blank=True,
        null=True,
        unique=True,
        editable=False,
        validators=(CWRFieldValidator("name"),),
    )
    iswc = models.CharField(
        "ISWC",
        max_length=15,
        blank=True,
        null=True,
        unique=True,
        validators=(CWRFieldValidator("iswc"),),
    )
    original_title = models.CharField(
        verbose_name="Title of original work",
        max_length=60,
        db_index=True,
        blank=True,
        help_text="Use only for modification of existing works.",
        validators=(CWRFieldValidator("title"),),
    )
    library_release = models.ForeignKey(
        "LibraryRelease",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="works",
        verbose_name="Library release",
    )
    last_change = models.DateTimeField(
        "Last Edited", editable=False, null=True
    )
    artists = models.ManyToManyField("Artist", through="ArtistInWork")
    writers = models.ManyToManyField(
        "Writer", through="WriterInWork", related_name="works"
    )

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
            return ""
        return "{}{:06}".format(
            settings.PUBLISHER_CODE,
            self.id,
        )

    @work_id.setter
    def work_id(self, value):
        if self._work_id is not None:
            raise NotImplementedError("work_id can not be changed")
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
        """Deal with various ways ISWC is written."""
        if self.iswc:
            # CWR 2.x holds ISWC in TNNNNNNNNNC format
            # CWR 3.0 holds ISWC in T-NNNNNNNNN-C format
            # sometimes it comes in T-NNN.NNN.NNN-C format
            self.iswc = self.iswc.replace("-", "").replace(".", "")
        return super().clean_fields(*args, **kwargs)

    def writer_last_names(self):
        writers = sorted(set(self.writers.all()), key=lambda w: w.last_name)
        return " / ".join(w.last_name.upper() for w in writers)

    def __str__(self):
        return "{}: {} ({})".format(
            self.work_id, self.title.upper(), self.writer_last_names()
        )

    @staticmethod
    def get_publisher_dict():
        """Create data structure for the publisher.

        Returns:
            dict: JSON-serializable data structure
        """
        j = {
            "id": 1,
            "code": settings.PUBLISHER_CODE,
            "name": settings.PUBLISHER_NAME,
            "ipi_name_number": settings.PUBLISHER_IPI_NAME,
            "ipi_base_number": settings.PUBLISHER_IPI_BASE,
            "affiliations": [
                {
                    "organization": {
                        "code": settings.PUBLISHER_SOCIETY_PR,
                        "name": SOCIETY_DICT.get(
                            settings.PUBLISHER_SOCIETY_PR, ""
                        ).split(",")[0],
                    },
                    "affiliation_type": {
                        "code": "PR",
                        "name": "Performance Rights",
                    },
                    "territory": WORLD_DICT,
                }
            ],
        }

        # append MR data to affiliations id needed
        if settings.PUBLISHER_SOCIETY_MR:
            j["affiliations"].append(
                {
                    "organization": {
                        "code": settings.PUBLISHER_SOCIETY_MR,
                        "name": SOCIETY_DICT.get(
                            settings.PUBLISHER_SOCIETY_MR, ""
                        ).split(",")[0],
                    },
                    "affiliation_type": {
                        "code": "MR",
                        "name": "Mechanical Rights",
                    },
                    "territory": WORLD_DICT,
                }
            )

        # append SR data to affiliations id needed
        if settings.PUBLISHER_SOCIETY_SR:
            j["affiliations"].append(
                {
                    "organization": {
                        "code": settings.PUBLISHER_SOCIETY_SR,
                        "name": SOCIETY_DICT.get(
                            settings.PUBLISHER_SOCIETY_SR, ""
                        ).split(",")[0],
                    },
                    "affiliation_type": {
                        "code": "SR",
                        "name": "Synchronization Rights",
                    },
                    "territory": WORLD_DICT,
                }
            )

        return j

    def get_dict(self, with_recordings=True):
        """Create a data structure that can be serialized as JSON.

        Normalize the structure if required.

        Returns:
            dict: JSON-serializable data structure
        """

        j = {
            "id": self.id,
            "code": self.work_id,
            "work_title": self.title,
            "last_change": self.last_change,
            "version_type": (
                {
                    "code": "MOD",
                    "name": "Modified Version of a musical work",
                }
                if self.original_title
                else {
                    "code": "ORI",
                    "name": "Original Work",
                }
            ),
            "iswc": self.iswc,
            "other_titles": [
                at.get_dict() for at in self.alternatetitle_set.all()
            ],
            "origin": (
                self.library_release.get_origin_dict()
                if self.library_release
                else None
            ),
            "writers": [],
            "performing_artists": [],
            "original_works": [],
            "cross_references": [],
        }

        if self.original_title:
            d = {"work_title": self.original_title}
            j["original_works"].append(d)

        # add data for (live) artists in work, normalize of required
        for aiw in self.artistinwork_set.all():
            d = aiw.get_dict()
            j["performing_artists"].append(d)

        # add data for writers in work, normalize of required
        for wiw in self.writerinwork_set.all():
            d = wiw.get_dict()
            j["writers"].append(d)

        if with_recordings:
            j["recordings"] = [
                recording.get_dict(with_releases=True)
                for recording in self.recordings.all()
            ]

        # add cross references, currently only society work ids from ACKs
        used_society_codes = []
        for wa in self.workacknowledgement_set.all():
            if not wa.remote_work_id:
                continue
            if wa.society_code in used_society_codes:
                continue
            used_society_codes.append(wa.society_code)
            d = wa.get_dict()
            j["cross_references"].append(d)

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
        help_text="Select if this title is only a suffix to the main title.",
    )

    class Meta:
        indexes = [
            models.Index(fields=["work_id", "title_type", "title"]),
        ]
        ordering = ("-suffix", "title_type", "title")
        verbose_name = "Alternate Title"

    def get_dict(self):
        """Create a data structure that can be serialized as JSON.

        Returns:
            dict: JSON-serializable data structure
        """
        return {
            "title": str(self),
            "title_type": {
                "code": self.title_type,
                "name": self.get_title_type_display(),
            },
        }

    def __str__(self):
        if self.suffix:
            return "{} {}".format(self.work.title, self.title)
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
        verbose_name = "Artist performing"
        verbose_name_plural = (
            "Artists performing (not mentioned in recordings section)"
        )
        indexes = [
            models.Index(fields=["work", "artist"]),
        ]
        ordering = ("artist__last_name", "artist__first_name")

    def __str__(self):
        return str(self.artist)

    def get_dict(self):
        """

        Returns:
            dict: taken from :meth:`models.Artist.get_dict`
        """
        return {"artist": self.artist.get_dict()}


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
        verbose_name = "Writer in Work"
        verbose_name_plural = "Writers in Work"
        indexes = [
            models.Index(fields=["work", "writer", "controlled"]),
        ]

        ordering = (
            "-controlled",
            "writer__last_name",
            "writer__first_name",
            "-id",
        )

    ROLES = (
        ("CA", "Composer&Lyricist"),
        ("C ", "Composer"),
        ("A ", "Lyricist"),
        ("AR", "Arranger"),
        ("AD", "Adaptor"),
        ("TR", "Translator"),
    )

    work = models.ForeignKey(Work, on_delete=models.CASCADE)
    writer = models.ForeignKey(
        Writer, on_delete=models.PROTECT, blank=True, null=True
    )
    saan = models.CharField(
        "Society-assigned specific agreement number",
        help_text="Use this field for specific agreements only."
        "For general agreements use the field in the Writer form.",
        max_length=14,
        blank=True,
        null=True,
        validators=(CWRFieldValidator("saan"),),
    )
    controlled = models.BooleanField(default=False)
    relative_share = models.DecimalField(
        "Manuscript share", max_digits=5, decimal_places=2
    )
    capacity = models.CharField(
        "Role", max_length=2, blank=True, choices=ROLES
    )
    publisher_fee = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text=(
            "Percentage of royalties kept by the publisher,\n"
            "in a specific agreement."
        ),
    )

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

        generally_controlled = self.writer and self.writer.generally_controlled
        if generally_controlled and not self.controlled:
            raise ValidationError(
                {
                    "controlled": (
                        "Must be set for a generally controlled writer."
                    )
                }
            )
        d = {}
        if self.controlled:
            if not self.capacity:
                d["capacity"] = "Must be set for a controlled writer."
            if not self.writer:
                d["writer"] = "Must be set for a controlled writer."
            else:
                if not self.writer._can_be_controlled:
                    d["writer"] = (
                        "IPI name and PR society must be set. "
                        'See "Writers" in the user manual'
                    )
        else:
            if self.saan:
                d["saan"] = "Must be empty if writer is not controlled."
            if self.publisher_fee:
                d["publisher_fee"] = (
                    "Must be empty if writer is not controlled."
                )
        if d:
            raise ValidationError(d)

    def get_agreement_dict(self):
        """Get agreement dictionary for this writer in work."""

        pub_pr_soc = settings.PUBLISHER_SOCIETY_PR
        pub_pr_name = SOCIETY_DICT.get(pub_pr_soc, "").split(",")[0]

        if not self.controlled or not self.writer:
            return None
        if self.writer.generally_controlled and not self.saan:
            # General
            return {
                "recipient_organization": {
                    "code": pub_pr_soc,
                    "name": pub_pr_name,
                },
                "recipient_agreement_number": self.writer.saan,
                "agreement_type": {
                    "code": "OG",
                    "name": "Original General",
                },
            }
        else:
            return {
                "recipient_organization": {
                    "code": pub_pr_soc,
                },
                "recipient_agreement_number": self.saan,
                "agreement_type": {
                    "code": "OS",
                    "name": "Original Specific",
                },
            }

    def get_dict(self):
        """Create a data structure that can be serialized as JSON.

        Returns:
            dict: JSON-serializable data structure
        """
        writer = self.writer.get_dict() if self.writer else None
        relative_share = str(self.relative_share / 100)
        role = (
            {
                "code": self.capacity.strip(),
                "name": self.get_capacity_display(),
            }
            if self.capacity
            else None
        )
        if self.controlled:
            ops = [
                {
                    "publisher": self.work.get_publisher_dict(),
                    "publisher_role": {
                        "code": "E",
                        "name": "Original publisher",
                    },
                    "agreement": self.get_agreement_dict(),
                }
            ]
        else:
            ops = []
        j = {
            "writer": writer,
            "controlled": self.controlled,
            "relative_share": relative_share,
            "writer_role": role,
            "original_publishers": ops,
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
        verbose_name = "Recording"
        verbose_name_plural = "Recordings"
        ordering = ("-id",)

    _recording_id = models.CharField(
        "Recording ID",
        max_length=14,
        blank=True,
        null=True,
        unique=True,
        editable=False,
        validators=(CWRFieldValidator("name"),),
    )
    recording_title = models.CharField(
        blank=True, max_length=60, validators=(CWRFieldValidator("title"),)
    )
    recording_title_suffix = models.BooleanField(
        default=False, help_text="A suffix to the WORK title."
    )
    version_title = models.CharField(
        blank=True, max_length=60, validators=(CWRFieldValidator("title"),)
    )
    version_title_suffix = models.BooleanField(
        default=False, help_text="A suffix to the RECORDING title."
    )
    release_date = models.DateField(blank=True, null=True)
    duration = models.DurationField(blank=True, null=True)
    isrc = models.CharField(
        "ISRC",
        max_length=15,
        blank=True,
        null=True,
        unique=True,
        validators=(CWRFieldValidator("isrc"),),
    )
    record_label = models.ForeignKey(
        Label,
        verbose_name="Record label",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
    )
    work = models.ForeignKey(
        Work, on_delete=models.CASCADE, related_name="recordings"
    )
    artist = models.ForeignKey(
        Artist,
        verbose_name="Recording Artist",
        related_name="recordings",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
    )

    releases = models.ManyToManyField(Release, through="Track")

    audio_file = models.FileField(
        upload_to=upload_to, max_length=255, blank=True
    )

    def clean_fields(self, *args, **kwargs):
        """
        ISRC cleaning, just removing dots and dashes.

        Args:
            *args: may be used in upstream
            **kwargs: may be used in upstream

        Returns:
            return from :meth:`django.db.models.Model.clean_fields`

        """
        empty = not any(
            [
                self.recording_title,
                self.version_title,
                self.release_date,
                self.isrc,
                self.duration,
                self.record_label,
                self.artist,
                self.audio_file,
            ]
        )
        if empty:
            raise ValidationError("No data left, please delete instead.")
        if self.isrc:
            # Removing all characters added for readability
            self.isrc = self.isrc.replace("-", "").replace(".", "")
        return super().clean_fields(*args, **kwargs)

    @property
    def complete_recording_title(self):
        """
        Return complete recording title.

        Returns:
            str
        """
        if self.recording_title_suffix:
            return "{} {}".format(
                self.work.title, self.recording_title
            ).strip()
        return self.recording_title

    @property
    def complete_version_title(self):
        """
        Return complete version title.

        Returns:
            str
        """
        if self.version_title_suffix:
            return "{} {}".format(
                self.complete_recording_title or self.work.title,
                self.version_title,
            ).strip()
        return self.version_title

    @property
    def title(self):
        """Generate title from various fields."""
        return (
            self.complete_version_title
            if self.version_title
            else (
                self.complete_recording_title
                if self.recording_title
                else self.work.title
            )
        )

    @property
    def recording_id(self):
        """Create Recording ID used in registrations

        Returns:
            str: Internal Recording ID
        """
        if self._recording_id:
            return self._recording_id
        if self.id is None:
            return ""
        return "{}{:06}R".format(
            settings.PUBLISHER_CODE,
            self.id,
        )

    @recording_id.setter
    def recording_id(self, value):
        if self._recording_id is not None:
            raise NotImplementedError("recording_id can not be changed")
        if value:
            self._recording_id = value

    def __str__(self):
        """Return the most precise type of title"""
        if self.artist:
            return "{}: {} ({})".format(
                self.recording_id, self.title, self.artist
            )
        else:
            return "{}: {}".format(self.recording_id, self.title)

    def get_dict(self, with_releases=False, with_work=True):
        """Create a data structure that can be serialized as JSON.

        Args:
            with_releases (bool): add releases data (through tracks)
            with_work (bool): add work data

        Returns:
            dict: JSON-serializable data structure

        """
        recording_title = self.complete_recording_title or self.work.title
        date = (
            self.release_date.strftime("%Y%m%d") if self.release_date else None
        )
        duration = duration_string(self.duration) if self.duration else None
        artist = self.artist.get_dict() if self.artist else None
        label = self.record_label.get_dict() if self.record_label else None
        j = {
            "id": self.id,
            "code": self.recording_id,
            "recording_title": recording_title,
            "version_title": self.complete_version_title,
            "release_date": date,
            "duration": duration,
            "isrc": self.isrc,
            "recording_artist": artist,
            "record_label": label,
        }
        if with_releases:
            j["tracks"] = []
            for track in self.tracks.all():
                d = track.release.get_dict()
                j["tracks"].append(
                    {
                        "release": d,
                        "cut_number": track.cut_number,
                    }
                )
        if with_work:
            j["works"] = [{"work": self.work.get_dict(with_recordings=False)}]
        return j


class Track(models.Model):
    """Track, a recording on a release.

    Attributes:
        recording (django.db.models.ForeignKey): Recording
        release (django.db.models.ForeignKey): Release
        cut_number (django.db.models.PositiveSmallIntegerField): Cut Number

    """

    class Meta:
        verbose_name = "Track"
        indexes = [
            models.Index(fields=["recording", "release"]),
            models.Index(fields=["release", "cut_number"]),
        ]
        ordering = (
            "release",
            "cut_number",
        )

    recording = models.ForeignKey(
        Recording, on_delete=models.PROTECT, related_name="tracks"
    )
    release = models.ForeignKey(
        Release, on_delete=models.CASCADE, related_name="tracks"
    )
    cut_number = models.PositiveSmallIntegerField(
        blank=True,
        null=True,
        validators=(MinValueValidator(1), MaxValueValidator(9999)),
    )

    def get_dict(self):
        """Create a data structure that can be serialized as JSON.

        Returns:
            dict: JSON-serializable data structure

        """
        return {
            "cut_number": self.cut_number,
            "recording": self.recording.get_dict(
                with_releases=False, with_work=True
            ),
        }

    def __str__(self):
        return self.recording.title


class DeferCwrManager(models.Manager):
    """Manager for CWR Exports and ACK Imports.

    Defers :attr:`CWRExport.cwr` and :attr:`AckImport.cwr` fields.

    """

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.defer("cwr")
        return qs


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
        verbose_name = "CWR Export"
        verbose_name_plural = "CWR Exports"
        ordering = ("-id",)

    objects = DeferCwrManager()

    nwr_rev = models.CharField(
        "CWR version/type",
        max_length=3,
        db_index=True,
        default="NWR",
        choices=(
            ("NWR", "CWR 2.1: New work registrations"),
            ("REV", "CWR 2.1: Revisions of registered works"),
            ("NW2", "CWR 2.2: New work registrations"),
            ("RE2", "CWR 2.2: Revisions of registered works"),
            ("WRK", "CWR 3.0: Work registration"),
            ("ISR", "CWR 3.0: ISWC request (EDI)"),
            ("WR1", "CWR 3.1 DRAFT: Work registration"),
        ),
    )
    cwr = models.TextField(blank=True, editable=False)
    created_on = models.DateTimeField(editable=False, null=True)
    year = models.CharField(
        max_length=2, db_index=True, editable=False, blank=True
    )
    num_in_year = models.PositiveSmallIntegerField(default=0)
    works = models.ManyToManyField(Work, related_name="cwr_exports")
    description = models.CharField("Internal Note", blank=True, max_length=60)

    publisher_code = None
    agreement_pr = settings.PUBLISHING_AGREEMENT_PUBLISHER_PR
    agreement_mr = settings.PUBLISHING_AGREEMENT_PUBLISHER_MR
    agreement_sr = settings.PUBLISHING_AGREEMENT_PUBLISHER_SR

    @property
    def version(self):
        """Return CWR version."""
        if self.nwr_rev in ["WRK", "ISR"]:
            return "30"
        elif self.nwr_rev == "WR1":
            return "31"
        elif self.nwr_rev in ["NW2", "RE2"]:
            return "22"
        return "21"

    @property
    def filename(self):
        """Return CWR file name.

        Returns:
            str: CWR file name
        """
        if self.version in ["30", "31"]:
            return self.filename3
        return self.filename2

    @property
    def filename3(self):
        """Return proper CWR 3.x filename.

        Format is: CWYYnnnnSUB_REP_VM - m - r.EXT

        Returns:
            str: CWR file name
        """
        if self.version == "30":
            minor_version = "0-0"
        else:
            minor_version = "1-0"
        if self.nwr_rev == "ISR":
            ext = "ISR"
        else:
            ext = "SUB"
        return "CW{}{:04}{}_0000_V3-{}.{}".format(
            self.year,
            self.num_in_year,
            self.publisher_code or settings.PUBLISHER_CODE,
            minor_version,
            ext,
        )

    @property
    def filename2(self):
        """Return proper CWR 2.x filename.

        Returns:
            str: CWR file name
        """
        return "CW{}{:04}{}_000.V{}".format(
            self.year,
            self.num_in_year,
            self.publisher_code or settings.PUBLISHER_CODE,
            self.version,
        )

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
        if self.version == "30":
            template = TEMPLATES_30.get(key)
        elif self.version == "31":
            template = TEMPLATES_31.get(key)
        else:
            if self.version == "22":
                tdict = TEMPLATES_22
            else:
                tdict = TEMPLATES_21
            if key == "HDR" and len(record["ipi_name_number"].lstrip("0")) > 9:
                # CWR 2.1 revision 8 "hack" for 10+ digit IPI name numbers
                template = tdict.get("HDR_8")
            else:
                template = tdict.get(key)
        record.update({"settings": settings})
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
        record["transaction_sequence"] = self.transaction_count
        record["record_sequence"] = self.record_sequence
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
            if work["iswc"]:
                work["indicator"] = "U"
            yield self.get_transaction_record("ISR", work)

            # WRI
            reported = set()
            for wiw in work["writers"]:
                w = wiw["writer"]
                if not w:
                    continue  # goes to OWR
                tup = (w["code"], wiw["writer_role"]["code"])
                if tup in reported:
                    continue
                reported.add(tup)
                w.update(
                    {
                        "writer_role": wiw["writer_role"]["code"],
                    }
                )
                yield self.get_transaction_record("WRI", w)

            self.transaction_count += 1

    def yield_publisher_lines(self, publisher, controlled_relative_share):
        """Yield SPU/SPT lines.

        Args:
            publisher (dict): dictionary with publisher data
            controlled_relative_share (Decimal): sum of manuscript shares \
            for controlled writers

        Yields:
              str: CWR record (row/line)
        """
        affiliations = publisher.get("affiliations", [])
        for aff in affiliations:
            if aff["affiliation_type"]["code"] == "PR":
                publisher["pr_society"] = aff["organization"]["code"]
            elif aff["affiliation_type"]["code"] == "MR":
                publisher["mr_society"] = aff["organization"]["code"]
            elif aff["affiliation_type"]["code"] == "SR":
                publisher["sr_society"] = aff["organization"]["code"]

        pr_share = controlled_relative_share * self.agreement_pr
        mr_share = controlled_relative_share * self.agreement_mr
        sr_share = controlled_relative_share * self.agreement_sr
        yield self.get_transaction_record(
            "SPU",
            {
                "chain_sequence": 1,
                "name": publisher.get("name"),
                "code": "P000001",
                "ipi_name_number": publisher.get("ipi_name_number"),
                "ipi_base_number": publisher.get("ipi_base_number"),
                "pr_society": publisher.get("pr_society"),
                "mr_society": publisher.get("mr_society"),
                "sr_society": publisher.get("sr_society"),
                "pr_share": pr_share,
                "mr_share": mr_share,
                "sr_share": sr_share,
            },
        )
        if controlled_relative_share:
            yield self.get_transaction_record(
                "SPT",
                {
                    "code": "P000001",
                    "pr_share": pr_share,
                    "mr_share": mr_share,
                    "sr_share": sr_share,
                    "pr_society": publisher.get("pr_society"),
                    "mr_society": publisher.get("mr_society"),
                    "sr_society": publisher.get("sr_society"),
                },
            )

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
            if self.version == "22":
                if self.nwr_rev == "NW2":
                    record_type = "NWR"
                elif self.nwr_rev == "RE2":
                    record_type = "REV"
            else:
                record_type = self.nwr_rev
            indicator = "Y" if work["recordings"] else "U"
            version_type = (
                "MOD   UNSUNS"
                if work["version_type"]["code"] == "MOD"
                else "ORI         "
            )
            d = {
                "record_type": record_type,
                "code": work["code"],
                "work_title": work["work_title"],
                "iswc": work["iswc"],
                "recorded_indicator": indicator,
                "version_type": version_type,
            }
            yield self.get_transaction_record("WRK", d)
            yield from self.get_party_lines(work)
            yield from self.get_other_lines(work)
            self.transaction_count += 1

    def yield_other_publisher_lines(self, other_publisher_share):
        if other_publisher_share:
            pr_share = other_publisher_share * self.agreement_pr
            mr_share = other_publisher_share * self.agreement_mr
            sr_share = other_publisher_share * self.agreement_sr
            yield self.get_transaction_record(
                "OPU",
                {
                    "sequence": 2,
                    "pr_share": pr_share,
                    "mr_share": mr_share,
                    "sr_share": sr_share,
                },
            )
            yield self.get_transaction_record(
                "OPT",
                {
                    "pr_share": pr_share,
                    "mr_share": mr_share,
                    "sr_share": sr_share,
                },
            )

    def calculate_publisher_shares(self, work):
        controlled_relative_share = Decimal(0)  # total pub share
        other_publisher_share = Decimal(0)  # used for co-publishing
        controlled_writer_ids = set()  # used for co-publishing
        copublished_writer_ids = set()  # used for co-publishing
        controlled_shares = defaultdict(Decimal)
        for wiw in work["writers"]:
            if wiw["controlled"]:
                controlled_writer_ids.add(wiw["writer"]["code"])
        for wiw in work["writers"]:
            writer = wiw["writer"]
            share = Decimal(wiw["relative_share"])
            if wiw["controlled"]:
                key = writer["code"]
                controlled_relative_share += share
                controlled_shares[key] += share
            elif writer and writer["code"] in controlled_writer_ids:
                key = writer["code"]
                copublished_writer_ids.add(key)
                other_publisher_share += share
                controlled_shares[key] += share
        return (
            controlled_relative_share,
            other_publisher_share,
            controlled_shares,
            controlled_writer_ids,
            copublished_writer_ids,
        )

    def yield_controlled_writer_lines(
        self,
        work,
        publisher,
        controlled_shares,
        copublished_writer_ids,
        other_publisher_share,
    ):
        for wiw in work["writers"]:
            if not wiw["controlled"]:
                continue  # goes to OWR
            w = wiw["writer"]
            agr = wiw["original_publishers"][0]["agreement"]
            saan = agr["recipient_agreement_number"] if agr else None
            affiliations = w.get("affiliations", [])
            for aff in affiliations:
                if aff["affiliation_type"]["code"] == "PR":
                    w["pr_society"] = aff["organization"]["code"]
                elif aff["affiliation_type"]["code"] == "MR":
                    w["mr_society"] = aff["organization"]["code"]
                elif aff["affiliation_type"]["code"] == "SR":
                    w["sr_society"] = aff["organization"]["code"]
            share = controlled_shares[w["code"]]
            pr_share = share * (1 - self.agreement_pr)
            mr_share = share * (1 - self.agreement_mr)
            sr_share = share * (1 - self.agreement_sr)
            w.update(
                {
                    "writer_role": wiw["writer_role"]["code"],
                    "share": share,
                    "pr_share": pr_share,
                    "mr_share": mr_share,
                    "sr_share": sr_share,
                    "saan": saan,
                    "original_publishers": wiw["original_publishers"],
                }
            )
            yield self.get_transaction_record("SWR", w)
            if share:
                yield self.get_transaction_record("SWT", w)
            if share:
                yield self.get_transaction_record("MAN", w)
            w["publisher_sequence"] = 1
            w["publisher_code"] = "P000001"
            w["publisher_name"] = publisher["name"]
            yield self.get_transaction_record("PWR", w)
            copublished = (
                self.version in ["30", "31"]
                and other_publisher_share
                and w
                and w["code"] in copublished_writer_ids
            )
            if copublished:
                w["publisher_sequence"] = 2
                yield self.get_transaction_record(
                    "PWR", {"code": w["code"], "publisher_sequence": 2}
                )

    def yield_other_writer_lines(
        self, work, controlled_writer_ids, other_publisher_share
    ):
        for wiw in work["writers"]:
            if wiw["controlled"]:
                continue  # done in SWR
            writer = wiw["writer"]
            if writer and writer["code"] in controlled_writer_ids:
                continue  # co-publishing, already solved
            if writer:
                w = wiw["writer"]
                affiliations = w.get("affiliations", [])
                for aff in affiliations:
                    if aff["affiliation_type"]["code"] == "PR":
                        w["pr_society"] = aff["organization"]["code"]
                    elif aff["affiliation_type"]["code"] == "MR":
                        w["mr_society"] = aff["organization"]["code"]
                    elif aff["affiliation_type"]["code"] == "SR":
                        w["sr_society"] = aff["organization"]["code"]
            else:
                w = {"writer_unknown_indicator": "Y"}
            share = Decimal(wiw["relative_share"])
            w.update(
                {
                    "writer_role": (
                        wiw["writer_role"]["code"]
                        if wiw["writer_role"]
                        else None
                    ),
                    "share": share,
                    "pr_share": share,
                    "mr_share": share,
                    "sr_share": share,
                }
            )
            yield self.get_transaction_record("OWR", w)
            if w["share"]:
                yield self.get_transaction_record("OWT", w)
            if w["share"]:
                yield self.get_transaction_record("MAN", w)
            if self.version in ["30", "31"] and other_publisher_share:
                w["publisher_sequence"] = 2
                yield self.get_transaction_record("PWR", w)

    def get_party_lines(self, work):
        """Yield SPU, SPT, OPU, SWR, SWT, OPT and PWR lines

        Args:
            work: musical work

        Yields:
            str: CWR record (row/line)
        """

        # SPU, SPT
        (
            controlled_relative_share,
            other_publisher_share,
            controlled_shares,
            controlled_writer_ids,
            copublished_writer_ids,
        ) = self.calculate_publisher_shares(work)
        publisher = work["writers"][0]["original_publishers"][0]["publisher"]
        yield from self.yield_publisher_lines(
            publisher, controlled_relative_share
        )
        yield from self.yield_other_publisher_lines(other_publisher_share)

        # SWR, SWT, PWR

        yield from self.yield_controlled_writer_lines(
            work,
            publisher,
            controlled_shares,
            copublished_writer_ids,
            other_publisher_share,
        )

        # OWR

        yield from self.yield_other_writer_lines(
            work, controlled_writer_ids, other_publisher_share
        )

    def get_alt_lines(self, work):
        alt_titles = set()
        for at in work["other_titles"]:
            alt_titles.add((at["title"], at["title_type"]["code"]))
        for rec in work["recordings"]:
            if rec["recording_title"]:
                alt_titles.add((rec["recording_title"], "AT"))
            if rec["version_title"]:
                alt_titles.add((rec["version_title"], "AT"))
        for alt_title, title_type in sorted(alt_titles, key=lambda x: x[0]):
            if alt_title == work["work_title"]:
                continue
            yield self.get_transaction_record(
                "ALT", {"alternate_title": alt_title, "title_type": title_type}
            )

    def get_per_lines(self, work):
        artists = {}
        for aiw in work["performing_artists"]:
            artists.update({aiw["artist"]["code"]: aiw["artist"]})
        for rec in work["recordings"]:
            if not rec["recording_artist"]:
                continue
            artists.update(
                {rec["recording_artist"]["code"]: rec["recording_artist"]}
            )
        for artist in artists.values():
            yield self.get_transaction_record("PER", artist)

    def get_rec_lines(self, work):
        for rec in work["recordings"]:
            if rec["recording_artist"]:
                rec["display_artist"] = "{} {}".format(
                    rec["recording_artist"]["first_name"] or "",
                    rec["recording_artist"]["last_name"],
                ).strip()[:60]
            if rec["isrc"]:
                rec["isrc_validity"] = "Y"
            if rec["duration"]:
                rec["duration"] = rec["duration"].replace(":", "")[0:6]
            empty = not any(
                [
                    rec["release_date"],
                    rec["duration"],
                    rec["isrc"],
                ]
            )
            if self.version in ["21", "22"] and empty:
                continue
            yield self.get_transaction_record("REC", rec)

    def get_other_lines(self, work):
        """Yield ALT and subsequent lines

        Args:
            work: musical work

        Yields:
            str: CWR record (row/line)
        """

        # ALT
        yield from self.get_alt_lines(work)

        # VER
        if work["version_type"]["code"] == "MOD":
            yield self.get_transaction_record("OWK", work["original_works"][0])

        # PER

        yield from self.get_per_lines(work)

        # REC

        yield from self.get_rec_lines(work)

        # ORN
        if work["origin"]:
            yield self.get_transaction_record(
                "ORN",
                {
                    "library": work["origin"]["library"]["name"],
                    "cd_identifier": work["origin"]["cd_identifier"],
                },
            )

        # XRF
        for xrf in work["cross_references"]:
            yield self.get_transaction_record("XRF", xrf)

    def get_header(self):
        """Construct CWR HDR record."""
        return self.get_record(
            "HDR",
            {
                "creation_date": datetime.now(),
                "filename": self.filename,
                "ipi_name_number": settings.PUBLISHER_IPI_NAME,
                "name": settings.PUBLISHER_NAME,
                "code": settings.PUBLISHER_CODE,
            },
        )

    def yield_lines(self, works):
        """Yield CWR transaction records (rows/lines) for works

        Args:
            works (query): :class:`.models.Work` query

        Yields:
            str: CWR record (row/line)
        """

        self.record_count = self.record_sequence = self.transaction_count = 0

        yield self.get_header()

        if self.nwr_rev == "NW2":
            yield self.get_record("GRH", {"transaction_type": "NWR"})
        elif self.nwr_rev == "RE2":
            yield self.get_record("GRH", {"transaction_type": "REV"})
        else:
            yield self.get_record("GRH", {"transaction_type": self.nwr_rev})

        if self.nwr_rev == "ISR":
            lines = self.yield_iswc_request_lines(works)
        else:
            lines = self.yield_registration_lines(works)

        for line in lines:
            yield line

        yield self.get_record(
            "GRT",
            {
                "transaction_count": self.transaction_count,
                "record_count": self.record_count + 2,
            },
        )
        yield self.get_record(
            "TRL",
            {
                "transaction_count": self.transaction_count,
                "record_count": self.record_count + 4,
            },
        )

    def create_cwr(self, publisher_code=None):
        """Create CWR and save."""
        now = timezone.now()
        if publisher_code is None:
            publisher_code = settings.PUBLISHER_CODE
        self.publisher_code = publisher_code
        if self.cwr:
            return
        self.created_on = now
        self.year = now.strftime("%y")
        nr = type(self).objects.filter(year=self.year)
        nr = nr.order_by("-num_in_year").first()
        if nr:
            self.num_in_year = nr.num_in_year + 1
        else:
            self.num_in_year = 1
        qs = self.works.order_by(
            "id",
        )
        works = Work.objects.get_dict(qs)["works"]
        self.cwr = "".join(self.yield_lines(works))
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
        verbose_name = "Registration Acknowledgement"
        ordering = ("-date", "-id")
        indexes = [
            models.Index(fields=["society_code", "remote_work_id"]),
        ]

    TRANSACTION_STATUS_CHOICES = (
        ("CO", "Conflict"),
        ("DU", "Duplicate"),
        ("RA", "Transaction Accepted"),
        ("AS", "Registration Accepted"),
        ("AC", "Registration Accepted with Changes"),
        ("SR", "Registration Accepted - Ready for Payment"),
        ("CR", "Registration Accepted with Changes - Ready for Payment"),
        ("RJ", "Rejected"),
        ("NP", "No Participation"),
        ("RC", "Claim rejected"),
        ("NA", "Rejected - No Society Agreement Number"),
        ("WA", "Rejected - Wrong Society Agreement Number"),
    )

    work = models.ForeignKey(Work, on_delete=models.PROTECT)
    society_code = models.CharField("Society", max_length=3, choices=SOCIETIES)
    date = models.DateField()
    status = models.CharField(max_length=2, choices=TRANSACTION_STATUS_CHOICES)
    remote_work_id = models.CharField(
        "Remote work ID", max_length=20, blank=True, db_index=True
    )

    def get_dict(self):
        """
        Return dictionary with external work IDs.

        Returns:
            dict: JSON-serializable data structure
        """
        # if not self.remote_work_id:
        #     return None
        j = {
            "organization": {
                "code": self.society_code,
                "name": self.get_society_code_display().split(",")[0],
            },
            "identifier": self.remote_work_id,
        }
        return j


class ACKImport(models.Model):
    """CWR acknowledgement file import.

    Attributes:
        filename (django.db.models.CharField): Description
        society_code (models.CharField): 3-digit society code,
            please note that ``choices`` is not set.
        society_name (models.CharField): Society name,
            used if society code is missing.
        date (django.db.models.DateField): Acknowledgement date
        report (django.db.models.CharField): Basically a log
        cwr (django.db.models.TextField): contents of CWR file
    """

    class Meta:
        verbose_name = "CWR ACK Import"
        ordering = ("-date", "-id")

    objects = DeferCwrManager()

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
        verbose_name = "Data Import"
        ordering = ("-date", "-id")

    filename = models.CharField(max_length=60, editable=False)
    report = models.TextField(editable=False)
    date = models.DateTimeField(auto_now_add=True, editable=False)

    def __str__(self):
        return self.filename


def smart_str_conversion(value):
    """Convert to Title Case only if UPPER CASE."""
    if value.isupper():
        return value.title()
    return value


FORCE_CASE_CHOICES = {
    "upper": str.upper,
    "title": str.title,
    "smart": smart_str_conversion,
}


@receiver(pre_save)
def change_case(sender, instance, **kwargs):
    """Change case of CharFields from :mod:`music_publisher`."""
    force_case = FORCE_CASE_CHOICES.get(settings.OPTION_FORCE_CASE)
    if not force_case:
        return
    if sender._meta.app_label != "music_publisher":
        return
    for field in instance._meta.get_fields():
        if isinstance(field, models.CharField):
            value = getattr(instance, field.name)
            convertible = (
                isinstance(value, str)
                and field.editable
                and field.choices is None
                and ("name" in field.name or "title" in field.name)
            )
            if convertible:
                value = force_case(value)
                setattr(instance, field.name, value)
