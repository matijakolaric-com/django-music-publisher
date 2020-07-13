"""
All the code related to importing data from external files.

Currently, only works (with writers, artists, library data and ISRCs) are
imported. (ISRCs will be used for importing recording data the in future.)

"""

import csv
import re
from collections import defaultdict, OrderedDict
from decimal import Decimal

from django.conf import settings
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE
from django.contrib.admin.options import get_content_type_for_model
from django.db import IntegrityError, transaction
from django.forms import inlineformset_factory
from django.utils.text import slugify

from .admin import WriterInWorkFormSet
from .models import (
    Work, Artist, ArtistInWork, Writer, WriterInWork,
    Library, LibraryRelease, Recording)


class DataImporter(object):
    """

    """
    FLAT_FIELDS = [
        'work_id', 'work_title', 'iswc', 'original_title',
        'library', 'cd_identifier']
    ARTIST_FIELDS = [
        'last', 'first', 'isni']
    WRITER_FIELDS = [
        'last', 'first', 'ipi', 'pro', 'role', 'share', 'controlled', 'saan']

    def __init__(self, filelike, user=None):
        self.user = user
        self.user_id = self.user.id if self.user else None
        self.reader = csv.DictReader(filelike)

    def log(self, action_flag, obj, message):
        """Helper function for logging history."""
        if not self.user_id:
            return
        LogEntry.objects.log_action(
            self.user_id, get_content_type_for_model(obj).id, obj.id, str(obj),
            action_flag, message)

    @staticmethod
    def get_clean_key(value, tup, name):
        """Try to match either key or value from a user input mess."""

        key_match = re.match(r'^([0-9]+|[A-Z]+)', value)
        if not key_match:
            raise ValueError(
                'Unknown value: "{}" for "{}".'.format(value, name))
        key = key_match.group(0)
        if key.upper() in [t[0] for t in tup]:
            return key
        else:
            raise ValueError(
                'Unknown value: "{}" for "{}".'.format(value, name))

    def process_writer_value(self, key, key_elements, value):
        """Clean a value for a writer and return it.

        If it is a 'controlled', then also calculate general agreement.
        Always return a tuple."""

        general_agreement = False
        if (len(key_elements) < 3 or
                key_elements[2] not in self.WRITER_FIELDS):
            raise AttributeError('Unknown column: "{}".'.format(key))
        if key_elements[2] == 'role':
            value = self.get_clean_key(
                value, WriterInWork.ROLES, 'writer role')
        elif key_elements[2] == 'pro':
            value = self.get_clean_key(value, settings.SOCIETIES, 'society')
        elif key_elements[2] == 'share':
            if isinstance(value, str) and value[-1] == '%':
                value = Decimal(value[0:-1])
            else:
                value = Decimal(value) * 100
            value = value.quantize(Decimal('0.01'))
        elif key_elements[2] == 'controlled':
            if isinstance(value, str):
                value = value[0].upper()
                if not value or value in ['N', 'F']:  # F for False
                    value = False
                else:
                    if value == 'G':
                        general_agreement = True
                    value = True
            else:
                value = bool(value)
        return value, general_agreement

    def unflatten(self, in_dict):
        """Create a well-structured dictionary with cleaner values."""
        out_dict = {
            'alt_titles': [],
            'writers': defaultdict(OrderedDict),
            'artists': defaultdict(OrderedDict),
            'recordings': defaultdict(OrderedDict),
        }
        for key, value in in_dict.items():
            if isinstance(value, str):
                value = value.strip()
            clean_key = slugify(key).replace('-', '_')
            prefix = clean_key.split('_')[0]
            if value == '':
                continue
            if clean_key in self.FLAT_FIELDS:
                out_dict[clean_key] = value
            elif prefix == 'alt':
                key_elements = clean_key.rsplit('_', 1)
                if len(key_elements) < 2 or key_elements[0] != 'alt_title':
                    raise AttributeError('Unknown column: "{}".'.format(key))
                out_dict['alt_titles'].append(value)
            elif prefix == 'writer':
                key_elements = clean_key.split('_', 2)
                value, general_agreement = self.process_writer_value(
                    key, key_elements, value)
                if general_agreement:
                    out_dict['writers'][key_elements[1]]['general_agreement'] \
                        = True
                out_dict['writers'][key_elements[1]][key_elements[2]] = value
            elif prefix == 'artist':
                key_elements = clean_key.split('_', 2)
                if (len(key_elements) < 3 or
                        key_elements[2] not in self.ARTIST_FIELDS):
                    raise AttributeError('Unknown column: "{}".'.format(key))
                out_dict['artists'][key_elements[1]][key_elements[2]] = value
            elif prefix == 'recording':
                key_elements = clean_key.split('_', 2)
                if (len(key_elements) == 3 and key_elements[2] == 'isrc'):
                    out_dict['recordings'][key_elements[1]] = value
            else:
                raise AttributeError('Unknown column: "{}".'.format(key))
        return out_dict

    def get_writers(self, writer_dict):
        for value in writer_dict.values():
            # variables used more than once or too complex
            general_agreement = value.get('general_agreement', False)
            saan = value.get('saan') if general_agreement else None
            pr_society = value.get('pro')
            last_name = value.get('last', '')
            first_name = value.get('first', '')
            ipi_name = value.get('ipi', None)
            # maybe writer is unknown
            if not any([
                    last_name, first_name, ipi_name, pr_society, saan,
                    general_agreement]):
                yield None
                continue
            # find this writer
            lookup_writer = Writer(
                last_name=last_name,
                first_name=first_name,
                ipi_name=ipi_name,
                pr_society=pr_society,
                generally_controlled=general_agreement,
                saan=saan)
            lookup_writer.clean_fields()
            lookup_writer.clean()
            writer = Writer.objects.filter(
                last_name=lookup_writer.last_name,
                first_name=lookup_writer.first_name,
                ipi_name=lookup_writer.ipi_name).first()
            if writer:
                # No existing general agreement for this writer
                if (lookup_writer.generally_controlled and
                        not writer.generally_controlled):
                    writer.saan = saan
                    writer.generally_controlled = True
                    writer.save()
                    self.log(
                        CHANGE, writer, 'General agreement set during import.')

                # Writer must be exactly same, except if marked "generally
                # controlled" in the database, and not in the file
                if (lookup_writer.generally_controlled and
                        writer.generally_controlled and
                        writer.saan != lookup_writer.saan):
                    raise ValueError(
                        'Two different general agreement numbers for: '
                        '"{}".'.format(writer))
                if writer.pr_society != lookup_writer.pr_society:
                    raise ValueError(
                        'Writer exists with different PRO: "{}".'.format(
                            writer
                        ))
            else:
                writer = lookup_writer
                try:
                    writer.save()
                    self.log(
                        ADDITION, writer, 'Added during import.')
                except IntegrityError:
                    raise ValueError(
                        'A writer with this IPI or general SAAN already '
                        'exists in the database, but is not exactly the same '
                        'as one provided in the importing data: {}'.format(
                            writer
                        ))
            yield writer

    def get_artists(self, artist_dict):
        for value in artist_dict.values():
            lookup_artist = Artist(
                last_name=value.get('last', ''),
                first_name=value.get('first', ''),
                isni=value.get('isni', None))
            lookup_artist.clean_fields()
            lookup_artist.clean()
            artist = Artist.objects.filter(
                last_name=lookup_artist.last_name,
                first_name=lookup_artist.first_name,
                isni=lookup_artist.isni
            ).first()
            if not artist:
                artist = lookup_artist
                artist.save()
                self.log(
                    ADDITION, artist, 'Added during import.')
            yield artist

    def get_library_release(self, library_name, cd_identifier):
        lookup_library = Library(name=library_name)
        lookup_library.clean_fields()
        library = Library.objects.filter(name=lookup_library.name).first()
        if not library:
            library = lookup_library
            library.save()
            self.log(
                ADDITION, library, 'Added during import.')
        lookup_library_release = LibraryRelease(
            library_id=library.id,
            cd_identifier=cd_identifier)
        library_release = LibraryRelease.objects.filter(
            library_id=lookup_library_release.library_id,
            cd_identifier=lookup_library_release.cd_identifier
        ).first()
        if not library_release:
            library_release = lookup_library_release
            library_release.save()
            self.log(
                ADDITION, library_release, 'Added during import.')
        return library_release

    def process_row(self, row):
        row_dict = self.unflatten(row)
        writers = self.get_writers(row_dict['writers'])
        artists = self.get_artists(row_dict['artists'])
        library = row_dict.get('library')
        cd_identifier = row_dict.get('cd_identifier')
        if bool(library) != bool(cd_identifier):
            raise ValueError(
                'Library and CD Identifier fields must both be either '
                'present or empty.')
        elif library:
            library_release = self.get_library_release(
                library, cd_identifier)
        else:
            library_release = None
        work = Work(
            work_id=row_dict.get('work_id', None),
            title=row_dict.get('work_title', ''),
            iswc=row_dict.get('iswc'),
            original_title=row_dict.get('original_title', ''),
            library_release=library_release)
        work.clean_fields()
        work.clean()
        work.save()
        self.log(
            ADDITION, work, 'Added during import.')
        for artist in set(artists):
            ArtistInWork(artist=artist, work=work).save()
        for isrc in row_dict['recordings'].values():
            recording = Recording(work=work, isrc=isrc)
            recording.clean_fields()
            recording.clean()
            recording.save()
            self.log(
                ADDITION, recording, 'Added during import.')
        wiws = []
        for w_dict in row_dict['writers'].values():
            writer = next(writers)
            saan = w_dict.get('saan')
            if writer and saan == writer.saan:
                saan = None
            wiw = WriterInWork(
                writer=writer, work=work,
                relative_share=w_dict.get('share'),
                capacity=w_dict.get('role'),
                controlled=w_dict.get('controlled'),
                saan=saan)
            wiw.clean_fields()
            wiw.clean()
            wiw.save()
            wiws.append(wiw)
        factory_fields = [
            'work', 'writer', 'capacity', 'relative_share', 'controlled',
            'saan']
        factory = inlineformset_factory(
            Work, WriterInWork, formset=WriterInWorkFormSet,
            fields=factory_fields, extra=len(wiws))
        formset = factory()
        for i, form in enumerate(formset.forms):
            wiw = wiws[i]
            data = {}
            data['writer'] = wiw.writer_id
            data['work'] = wiw.work_id
            data['capacity'] = wiw.capacity
            data['relative_share'] = wiw.relative_share
            data['controlled'] = wiw.controlled
            data['saan'] = wiw.saan
            form.initial = form.cleaned_data = data
            form.full_clean()
            form.is_bound = True
        formset.clean()
        yield work

    def run(self):
        """Run the import as atomic."""
        with transaction.atomic():
            for row in self.reader:
                yield from self.process_row(row)
