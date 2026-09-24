"""
All the code related to importing data from external files.

Currently, only works (with writers, artists, library data and ISRCs) are
imported. (ISRCs will be used for importing recording data the in future.)

"""

import csv
import re
from collections import defaultdict, OrderedDict
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.forms import inlineformset_factory
from django.utils.text import slugify

from .societies import SOCIETIES
from .models import (
    Work,
    Artist,
    ArtistInWork,
    Writer,
    WriterInWork,
    AlternateTitle,
    Library,
    LibraryRelease,
    Recording,
    WorkAcknowledgement,
)
from .forms import WriterInWorkFormSet
from django.utils.timezone import now


class DataImporter(object):
    """ """

    FLAT_FIELDS = [
        "work_id",
        "work_title",
        "iswc",
        "original_title",
        "library",
        "cd_identifier",
        "tags",
    ]
    ARTIST_FIELDS = ["last", "first", "isni"]
    SHARE_FIELDS = [
        "share",
        "manuscript_share",
        "pr_share",
        "mr_share",
        "sr_share",
        "publisher_pr_share",
        "publisher_mr_share",
        "publisher_sr_share",
    ]
    WRITER_FIELDS = [
        "last",
        "first",
        "ipi",
        "pro",
        "mro",
        "sro",
        "role",
        "controlled",
        "saan",
        "account_number",
        "publisher_name",
        "publisher_ipi",
        "publisher_pro",
        "publisher_mro",
        "publisher_sro",
    ] + SHARE_FIELDS
    RECORDING_FIELDS = [
        "id",
        "recording_title",
        "version_title",
        "release_date",
        "duration",
        "isrc",
        # "artist_last",
        # "artist_first",
        # "artist_isni",
        "record_label",
    ]
    REFERENCE_FIELDS = ["id", "cmo"]

    def __init__(self, filelike, user=None):
        self.user = user
        self.user_id = self.user.id if self.user else None
        self.reader = csv.DictReader(filelike)
        self.report = ""
        self.unknown_keys = set()

    def log(self, obj, message, change=False):
        """Helper function for logging history."""
        if not self.user_id:
            return
        from django.contrib.admin.models import LogEntry, ADDITION, CHANGE
        from django.contrib.admin.options import get_content_type_for_model

        if change:
            action_flag = CHANGE
        else:
            action_flag = ADDITION
        LogEntry.objects.log_action(
            self.user_id,
            get_content_type_for_model(obj).id,
            obj.id,
            str(obj),
            action_flag,
            message,
        )

    @staticmethod
    def get_clean_key(value, tup, name):
        """Try to match either key or value from a user input mess."""
        key_match = re.match(r"^([0-9]+|[A-Z]+)", value)
        if not key_match:
            raise ValueError('Bad value: "{}" for "{}".'.format(value, name))
        key = key_match.group(0)
        if key.upper() in [t[0].strip() for t in tup]:
            return key
        else:
            raise ValueError(
                'Unknown value: "{}" for "{}".'.format(value, name)
            )

    def process_writer_value(self, key, key_elements, value):
        field = key_elements[2] if len(key_elements) >= 3 else None
        if field not in self.WRITER_FIELDS:
            raise AttributeError('Unknown column: "{}".'.format(key))
        if field == "role":
            return (
                self.get_clean_key(
                    value.ljust(2), WriterInWork.ROLES, "writer role"
                ).ljust(2),
                False,
            )
        if field == "pro":
            return (
                self.get_clean_key(
                    value, SOCIETIES + [("99", "NO SOCIETY")], "society"
                ),
                False,
            )
        if field in self.SHARE_FIELDS:
            amount = (
                Decimal(value[:-1])
                if isinstance(value, str) and value[-1:] == "%"
                else Decimal(value) * 100
            )
            return amount.quantize(Decimal("0.01")), False
        if field == "controlled":
            return self._clean_controlled(value)
        return value, False

    @staticmethod
    def _clean_controlled(value):
        if not isinstance(value, str):
            return bool(value), False
        value = value[0].upper() if value else ""
        return value not in ["N", "F"], value == "G"

    def unflatten_writer_record(self, out_dict, clean_key, key, value):
        key_elements = clean_key.split("_", 2)
        if len(key_elements) < 3 or key_elements[2] not in self.WRITER_FIELDS:
            self.unknown_keys.add(key)
            return
        value, general_agreement = self.process_writer_value(
            key, key_elements, value
        )
        if general_agreement:
            out_dict["writers"][key_elements[1]]["general_agreement"] = True
        out_dict["writers"][key_elements[1]][key_elements[2]] = value

    def unflatten_record(self, out_dict, key, value):
        if value is None:
            return
        if isinstance(value, str):
            value = value.strip()
        clean_key = slugify(key).replace("-", "_")
        prefix = clean_key.split("_")[0]
        if value == "":
            return
        if clean_key in self.FLAT_FIELDS:
            out_dict[clean_key] = value
            return
        if prefix == "alt":
            self._unflatten_alt_title(out_dict, clean_key, key, value)
            return
        if prefix == "writer":
            self.unflatten_writer_record(out_dict, clean_key, key, value)
            return
        if prefix in ("artist", "recording", "reference"):
            self._unflatten_related(out_dict, clean_key, key, value, prefix)
            return
        self.unknown_keys.add(key)

    def _unflatten_alt_title(self, out_dict, clean_key, key, value):
        elements = clean_key.rsplit("_", 1)
        if len(elements) < 2 or elements[0] != "alt_title":
            self.unknown_keys.add(key)
        else:
            out_dict["alt_titles"].append(value)

    def _unflatten_related(self, out_dict, clean_key, key, value, prefix):
        elements = clean_key.split("_", 2)
        fields = getattr(self, prefix.upper() + "_FIELDS")
        if len(elements) < 3 or elements[2] not in fields:
            self.unknown_keys.add(key)
            return
        out_dict[prefix + "s"][elements[1]][elements[2]] = value

    def unflatten(self, in_dict):
        """Create a well-structured dictionary with cleaner values."""
        out_dict = {
            "alt_titles": [],
            "writers": defaultdict(OrderedDict),
            "artists": defaultdict(OrderedDict),
            "recordings": defaultdict(OrderedDict),
            "references": defaultdict(OrderedDict),
        }
        for key, value in in_dict.items():
            self.unflatten_record(out_dict, key, value)
        return out_dict

    def get_writers(self, writer_dict):
        """Yield Writer objects, create if needed."""
        for value in writer_dict.values():
            details = self._writer_details(value)
            if not details["present"]:
                yield None
                continue
            yield self._get_or_create_writer(details)

    @staticmethod
    def _writer_details(value):
        general = value.get("general_agreement", False)
        ipi = value.get("ipi")
        return {
            "present": any(
                [
                    value.get("last", ""),
                    value.get("first", ""),
                    ipi,
                    value.get("pro"),
                    value.get("saan") if general else None,
                    general,
                    value.get("account_number"),
                ]
            ),
            "last": value.get("last", ""),
            "first": value.get("first", ""),
            "ipi": ipi,
            "ipi_unset": ipi == "00000000000",
            "pro": value.get("pro"),
            "general": general,
            "saan": value.get("saan") if general else None,
            "account_number": value.get("account_number"),
        }

    def _get_or_create_writer(self, details):
        lookup = Writer(
            last_name=details["last"],
            first_name=details["first"],
            ipi_name=details["ipi"],
            pr_society=details["pro"],
            generally_controlled=details["general"],
            saan=details["saan"],
            account_number=details["account_number"],
        )
        lookup.clean_fields()
        lookup.clean()
        writer = Writer.objects.filter(
            last_name__iexact=lookup.last_name,
            first_name__iexact=lookup.first_name,
            ipi_name=None if details["ipi_unset"] else lookup.ipi_name,
        ).first()
        if writer:
            return self._validate_existing_writer(
                writer, lookup, details["saan"]
            )
        try:
            lookup.save()
            self.log(lookup, "Added during import.")
        except IntegrityError:
            raise ValueError(
                "A writer with this IPI already exists in the database, but is "
                "not exactly the same as one provided in the importing data: "
                "{}".format(lookup)
            )
        return lookup

    def _validate_existing_writer(self, writer, lookup, saan):
        if lookup.generally_controlled and not writer.generally_controlled:
            writer.saan = saan
            writer.generally_controlled = True
            writer.save()
            self.log(
                writer, "General agreement set during import.", change=True
            )
        if lookup.generally_controlled and writer.generally_controlled:
            if writer.saan != lookup.saan:
                raise ValueError(
                    'Two different general agreement numbers for: "{}".'.format(
                        writer
                    )
                )
        if writer.pr_society != lookup.pr_society:
            raise ValueError(
                'Writer exists with different PRO: "{}".'.format(writer)
            )
        return writer

    def get_artists(self, artist_dict):
        """Yield Artist objects, create if needed."""
        for value in artist_dict.values():
            lookup_artist = Artist(
                last_name=value.get("last", ""),
                first_name=value.get("first", ""),
                isni=value.get("isni", None),
            )
            lookup_artist.clean_fields()
            lookup_artist.clean()
            artist = Artist.objects.filter(
                last_name__iexact=lookup_artist.last_name,
                first_name__iexact=lookup_artist.first_name,
                isni=lookup_artist.isni,
            ).first()
            if not artist:
                artist = lookup_artist
                try:
                    artist.save()
                    self.log(artist, "Added during import.")
                except IntegrityError:
                    raise ValueError(
                        "An artist with this ISNI already "
                        "exists in the database, but is not exactly the same "
                        "as one provided in the importing data: {}".format(
                            artist
                        )
                    )
            yield artist

    def get_library_release(self, library_name, cd_identifier):
        """Yield LibraryRelease objects, create if needed."""
        lookup_library = Library(name=library_name)
        lookup_library.clean_fields()
        library = Library.objects.filter(
            name__iexact=lookup_library.name
        ).first()
        if not library:
            library = lookup_library
            library.save()
            self.log(library, "Added during import.")
        lookup_library_release = LibraryRelease(
            library_id=library.id, cd_identifier=cd_identifier
        )
        library_release = LibraryRelease.objects.filter(
            library_id=lookup_library_release.library_id,
            cd_identifier__iexact=lookup_library_release.cd_identifier,
        ).first()
        if not library_release:
            library_release = lookup_library_release
            library_release.save()
            self.log(library_release, "Added during import.")
        return library_release

    def process_row(self, row):
        """Process one row from the incoming data."""
        if not any(value.strip() for value in row.values()):
            return
        row_dict = self.unflatten(row)
        writers = self.get_writers(row_dict["writers"])
        artists = self.get_artists(row_dict["artists"])
        work = self._create_work(row_dict)
        self.log(work, "Added during import.")
        self._save_artists(work, artists)
        wiws = self._save_writers(work, row_dict["writers"], writers)
        self._validate_writers(work, wiws)
        self._save_related_records(work, row_dict)
        yield work

    def _create_work(self, row_dict):
        library = row_dict.get("library")
        cd_identifier = row_dict.get("cd_identifier")
        if bool(library) != bool(cd_identifier):
            raise ValueError(
                "Library and CD Identifier fields must both be either present or empty."
            )
        library_release = (
            self.get_library_release(library, cd_identifier)
            if library
            else None
        )
        work = Work(
            work_id=row_dict.get("work_id"),
            title=row_dict.get("work_title", ""),
            iswc=row_dict.get("iswc"),
            original_title=row_dict.get("original_title", ""),
            library_release=library_release,
        )
        work.clean_fields()
        work.clean()
        try:
            work.save()
        except IntegrityError:
            raise ValidationError(
                f'Work "{work.title}", '
                + (f'ID "{work.work_id}", ' if work.work_id else "")
                + (f'ISWC "{work.iswc}", ' if work.iswc else "")
                + "clashes with an existing work. Data imports can only be used "
                "for adding new works."
            )
        tags = row_dict.get("tags")
        if tags:
            work.tags.add(
                *[tag.strip() for tag in tags.split(",") if tag.strip()]
            )
        return work

    def _save_artists(self, work, artists):
        for artist in set(artists):
            ArtistInWork(artist=artist, work=work).save()

    def _save_writers(self, work, writer_dict, writers):
        wiws = []
        for values in writer_dict.values():
            writer = next(writers)
            saan = values.get("saan")
            if writer and saan == writer.saan:
                saan = None
            share = values.get("manuscript_share") or values.get("share")
            if not share:
                share = values.get("pr_share", 0) + values.get(
                    "publisher_pr_share", 0
                )
            wiw = WriterInWork(
                writer=writer,
                work=work,
                relative_share=share,
                capacity=values.get("role", ""),
                controlled=values.get("controlled", False),
                saan=saan,
            )
            wiw.clean_fields()
            wiw.clean()
            wiw.save()
            wiws.append(wiw)
        return wiws

    def _validate_writers(self, work, wiws):
        factory_fields = [
            "work",
            "writer",
            "capacity",
            "relative_share",
            "controlled",
            "saan",
        ]
        factory = inlineformset_factory(
            Work,
            WriterInWork,
            formset=WriterInWorkFormSet,
            fields=factory_fields,
            extra=len(wiws),
        )
        formset = factory()
        for i, form in enumerate(formset.forms):
            wiw = wiws[i]
            data = {
                "writer": wiw.writer_id,
                "work": wiw.work_id,
                "capacity": wiw.capacity,
                "relative_share": wiw.relative_share,
                "controlled": wiw.controlled,
                "saan": wiw.saan,
            }
            form.initial = form.cleaned_data = data
            form.full_clean()
            form.is_bound = True
        formset.clean()

    def _save_related_records(self, work, row_dict):
        for alt_title in row_dict["alt_titles"]:
            at = AlternateTitle(work=work, title=alt_title)
            at.clean_fields()
            at.clean()
            at.save()
        for recording in row_dict["recordings"].values():
            recording = Recording(
                work=work,
                isrc=recording.get("isrc"),
                duration=recording.get("duration"),
                release_date=recording.get("release_date"),
                recording_title=recording.get("recording_title", ""),
                version_title=recording.get("version_title", ""),
            )
            recording.clean_fields()
            recording.clean()
            recording.save()
            self.log(recording, "Added during import.")
        for reference in row_dict["references"].values():
            society_code = self.get_clean_key(
                reference.get("cmo", "") or "", SOCIETIES, "reference cmo"
            )
            workack = WorkAcknowledgement(
                work=work,
                remote_work_id=reference.get("id"),
                society_code=society_code,
                status="AS",
                date=now(),
            )
            workack.clean_fields()
            workack.clean()
            workack.save()
            self.log(workack, "Added during import.")

    def run(self):
        """Run the import."""
        for row in self.reader:
            yield from self.process_row(row)
