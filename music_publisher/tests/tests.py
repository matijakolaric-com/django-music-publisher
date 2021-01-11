"""
Tests for :mod:`music_publisher`.

This software has almost full test coverage. The only exceptions are
instances of :class:`Exception` being caught during data imports.
(User idiocy is boundless.)

Most of the tests are functional end-to-end tests. While they test that
code works, they don't always test that it works as expected.

Still, it must be noted that exports are tested against provided
templates (made in a different software, not using the same code beyond
Python standard library).

More precise tests would be better.
"""

from datetime import datetime
from decimal import Decimal
from io import StringIO

from django.contrib.admin.models import LogEntry
from django.contrib.admin.options import IS_POPUP_VAR
from django.contrib.auth.models import User
from django.core import exceptions
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.template import Context
from django.test import (
    override_settings, SimpleTestCase, TestCase, TransactionTestCase)
from django.urls import reverse

import music_publisher.models
from music_publisher import cwr_templates, data_import, validators
from music_publisher.models import (AlternateTitle, Artist, CommercialRelease,
    CWRExport, Label, Library, LibraryRelease, Recording, Release, Track, Work,
    Writer, WriterInWork, WorkAcknowledgement)

def get_data_from_response(response):
    """Helper for extracting data from HTTP response in a way that can be
    fed back into POST that works with Django Admin."""
    adminform = response.context_data.get('adminform')
    data = {}
    for sc in response.context:
        for d in sc:
            if 'widget' in sc:
                if sc['widget'].get('type') == 'checkbox':
                    data[sc['widget']['name']] = \
                        sc['widget']['attrs'].get('checked')
                    continue
                if (sc['widget'].get('type') == 'select' and
                        sc['widget']['selected'] is False):
                    continue
                data[sc['widget']['name']] = sc['widget']['value']
    if adminform:
        data.update(adminform.form.initial)
    for key, value in data.items():
        if value is None:
            data[key] = ''
        else:
            data[key] = value
    return data


@override_settings(
    SECURE_SSL_REDIRECT=False,
    PUBLISHER_NAME='TEST PUBLISHER',
    PUBLISHER_CODE='MK',
    PUBLISHER_IPI_NAME='0000000199',
    PUBLISHER_SOCIETY_PR='10',
    PUBLISHER_SOCIETY_MR='34',
    PUBLISHER_SOCIETY_SR=None,
    REQUIRE_SAAN=False,
    REQUIRE_PUBLISHER_FEE=False)
class DataImportTest(TestCase):
    """Functional test for data import from CSV files."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.superuser = User.objects.create_superuser(
            'superuser', '', 'password')
        cls.obj = Artist(last_name='Artist One')

    def test_data_import(self):
        with open(TEST_DATA_IMPORT_FILENAME) as csvfile:
            di = data_import.DataImporter(csvfile)
            di.run()

    def test_log(self):
        """Test logging during import."""

        """This does nothing, as user is unknown."""
        di = data_import.DataImporter([], user=None)
        di.log(data_import.ADDITION, None, 'no message')
        self.assertEqual(LogEntry.objects.count(), 0)

        """This logs."""
        di = data_import.DataImporter([], user=self.superuser)
        di.log(data_import.ADDITION, self.obj, 'test message')
        self.assertEqual(LogEntry.objects.count(), 1)
        le = LogEntry.objects.first()
        self.assertEqual(str(le), 'Added “ARTIST ONE”.')
        self.assertEqual(le.change_message, 'test message')

    def test_unknown_key_exceptions(self):
        """Test exceptions not tested in functional tests."""

        di = data_import.DataImporter([], user=None)

        # No key in dict
        with self.assertRaises(ValueError) as ve:
            di.get_clean_key('A', [], 'test')
        self.assertEqual(str(ve.exception), 'Unknown value: "A" for "test".')

        # Regex mismatch
        with self.assertRaises(ValueError) as ve:
            di.get_clean_key('-', [], 'test')
        self.assertEqual(str(ve.exception), 'Unknown value: "-" for "test".')

        with self.assertRaises(AttributeError) as ve:
            di.process_writer_value('a', ['Writer', '1', 'b'], 'X')
        self.assertEqual(str(ve.exception), 'Unknown column: "a".')

        value, general_agreement = di.process_writer_value(
            'a', ['writer', '1', 'controlled'], 1)
        self.assertEqual(value, True)

        value, general_agreement = di.process_writer_value(
            'a', ['writer', '2', 'controlled'], 0)
        self.assertEqual(value, False)

        with self.assertRaises(AttributeError) as ve:
            di.unflatten({'work_title': 'X', 'alt_work_title_1': 'Y'})
        self.assertEqual(
            str(ve.exception), 'Unknown column: "alt_work_title_1".')

        with self.assertRaises(AttributeError) as ve:
            di.unflatten({'work_title': 'X', 'alt_title': 'Y'})
        self.assertEqual(
            str(ve.exception), 'Unknown column: "alt_title".')

        with self.assertRaises(AttributeError) as ve:
            di.unflatten({'work_title': 'X', 'artist_1': 'Y'})
        self.assertEqual(
            str(ve.exception), 'Unknown column: "artist_1".')

        with self.assertRaises(AttributeError) as ve:
            di.unflatten({'work_title': 'X', 'artist_1_name': 'Y'})
        self.assertEqual(
            str(ve.exception), 'Unknown column: "artist_1_name".')

        with self.assertRaises(AttributeError) as ve:
            di.unflatten({'work_title': 'X', 'wtf_1': 'Y'})
        self.assertEqual(
            str(ve.exception), 'Unknown column: "wtf_1".')

        # mismatching general agreement numbers
        with self.assertRaises(ValueError) as ve:
            d = {
                '1': {
                    'first': 'X',
                    'last': 'Y',
                    'ipi': '199',
                    'pro': '10',
                    'general_agreement': True,
                    'saan': 'A',
                },
                '2': {
                    'first': 'X',
                    'last': 'Y',
                    'ipi': '199',
                    'pro': '10',
                    'general_agreement': True,
                    'saan': 'B',
                }
            }
            writers = list(di.get_writers(d))
        self.assertEqual(
            str(ve.exception),
            'Two different general agreement numbers for: "X Y (*)".')

        # mismatching PR societies
        with self.assertRaises(ValueError) as ve:
            d = {
                '1': {
                    'first': 'X',
                    'last': 'Y',
                    'ipi': '199',
                    'pro': '10',
                },
                '2': {
                    'first': 'X',
                    'last': 'Y',
                    'ipi': '199',
                    'pro': '52',
                }
            }
            writers = list(di.get_writers(d))
        self.assertEqual(
            str(ve.exception),
            'Writer exists with different PRO: "X Y (*)".')

        # integrity errrors
        with self.assertRaises(ValueError) as ve:
            d = {
                '1': {
                    'first': 'A',
                    'last': 'B',
                    'ipi': '199',
                    'pro': '10',
                },
                '2': {
                    'first': 'X',
                    'last': 'Y',
                    'ipi': '199',
                    'pro': '52',
                }
            }
            writers = list(di.get_writers(d))
        self.assertEqual(
            str(ve.exception),
            (
                'A writer with this IPI or general SAAN already exists in the '
                'database, but is not exactly the same as one provided in the '
                'importing data: A B'))

        f = StringIO("Work Title,Library\nX,Y")
        di = data_import.DataImporter(f, user=None)
        with self.assertRaises(ValueError) as ve:
            list(di.run())
        self.assertEqual(
            str(ve.exception),
            ('Library and CD Identifier fields must both be either '
                'present or empty.'))


@override_settings(
    SECURE_SSL_REDIRECT=False,
    PUBLISHER_NAME='TEST PUBLISHER',
    PUBLISHER_CODE='MK',
    PUBLISHER_IPI_NAME='0000000199',
    PUBLISHER_SOCIETY_PR='52',
    PUBLISHER_SOCIETY_MR='44',
    PUBLISHER_SOCIETY_SR='44',
    REQUIRE_SAAN=True,
    REQUIRE_PUBLISHER_FEE=True,
    PUBLISHING_AGREEMENT_PUBLISHER_PR=Decimal('0.333333'),
    PUBLISHING_AGREEMENT_PUBLISHER_MR=Decimal('0.5'),
    PUBLISHING_AGREEMENT_PUBLISHER_SR=Decimal('0.75'))
class AdminTest(TestCase):
    """Functional tests on the interface, and several related unit tests.

    Note that tests build one atop another, simulating typical work flow."""

    fixtures = ['publishing_staff.json']
    testing_admins = [
        'artist', 'label', 'library', 'work', 'commercialrelease', 'writer',
        'recording', 'cwrexport']

    @classmethod
    def create_original_work(cls):
        """
        Create original work, three writers, one controlled,
        with recording, alternate titles, included in a commercial release."""
        cls.original_work = Work.objects.create(
            title='The Work', iswc='T1234567893',
            library_release=cls.library_release)
        WriterInWork.objects.create(work=cls.original_work,
                                    writer=cls.generally_controlled_writer,
                                    capacity='C ',
                                    relative_share=Decimal('50'),
                                    controlled=True)
        WriterInWork.objects.create(work=cls.original_work,
                                    writer=cls.other_writer, capacity='A ',
                                    relative_share=Decimal('25'),
                                    controlled=False)
        wiw = WriterInWork.objects.create(work=cls.original_work,
                                          writer=cls.controllable_writer,
                                          capacity='A ',
                                          relative_share=Decimal('25'),
                                          controlled=False)
        assert (wiw.get_agreement_dict() is None)
        AlternateTitle.objects.create(work=cls.original_work, suffix=True,
                                      title='Behind the Work')
        AlternateTitle.objects.create(work=cls.original_work, title='Work')
        recording = Recording.objects.create(
            work=cls.original_work, record_label=cls.label, artist=cls.artist,
            isrc='JM-K40-14-00001')
        Track.objects.create(
            release=cls.commercial_release, recording=recording)

    @classmethod
    def create_modified_work(cls):
        """Create modified work, original writer plus arranger,
        with recording, alternate titles."""
        cls.modified_work = Work.objects.create(
            title='The Modified Work', original_title='The Work')
        WriterInWork.objects.create(
            work=cls.modified_work,
            writer=cls.generally_controlled_writer,
            capacity='AR',
            relative_share=Decimal('100'),
            controlled=True,
            saan='SPECIAL', publisher_fee=Decimal('25'))
        WriterInWork.objects.create(work=cls.modified_work, writer=None,
                                    capacity='CA', relative_share=Decimal('0'),
                                    controlled=False)
        cls.modified_work.artists.add(cls.artist)
        AlternateTitle.objects.create(work=cls.modified_work, suffix=False,
                                      title='The Copy')
        AlternateTitle.objects.create(work=cls.modified_work, suffix=True,
                                      title='Behind the Modified Work')
        Recording.objects.create(work=cls.modified_work,
                                 isrc='US-S1Z-99-00002')

    @classmethod
    def create_copublished_work(cls):
        """Create work, two writers, one co-published."""
        cls.copublished_work = Work.objects.create(title='Copublished')
        WriterInWork.objects.create(
            work=cls.copublished_work,
            writer=cls.generally_controlled_writer,
            capacity='CA',
            relative_share=Decimal('25'),
            controlled=True,
        )
        WriterInWork.objects.create(
            work=cls.copublished_work,
            writer=cls.controllable_writer,
            capacity='CA',
            relative_share=Decimal('25'),
            controlled=True,
            saan='SAAN',
            publisher_fee=Decimal('25')
        )
        WriterInWork.objects.create(
            work=cls.copublished_work,
            writer=cls.controllable_writer,
            capacity='CA',
            relative_share=Decimal('50'),
            controlled=False,
        )

    @classmethod
    def create_writers(cls):
        """Create four writers with different properties."""
        cls.generally_controlled_writer = Writer(
            first_name='John', last_name='Smith',
            ipi_name='00000000297', ipi_base='I-123456789-3',
            pr_society='52', sr_society='44', mr_society='44',
            generally_controlled=True, saan='A1B2C3',
            publisher_fee=Decimal('0.25'))
        cls.generally_controlled_writer.clean()
        cls.generally_controlled_writer.clean_fields()
        cls.generally_controlled_writer.save()

        cls.other_writer = Writer(
            first_name='Jane', last_name='Doe', ipi_name='395')
        cls.other_writer.clean()
        cls.other_writer.save()

        cls.writer_no_first_name = Writer(last_name='Jones')
        cls.writer_no_first_name.clean()
        cls.writer_no_first_name.save()

        # This one is controllable, but not yet affiliated, testing
        # "00000000000" hack
        cls.controllable_writer = Writer(
            first_name='Jack', last_name='Doe', ipi_name='00000000000')
        cls.controllable_writer.clean()
        cls.controllable_writer.save()
        # Later, he is affiliated.
        cls.controllable_writer.ipi_name = '493'
        cls.controllable_writer.pr_society = '52'
        cls.controllable_writer.mr_society = '44'
        cls.controllable_writer.sr_society = '44'
        cls.controllable_writer.clean()
        cls.controllable_writer.save()

    @classmethod
    def create_cwr2_export(cls):
        """Create a NWR and a REV CWR2 Export. """
        cls.cwr2_export = CWRExport.objects.create(
            description='Test NWR', nwr_rev='NWR')
        cls.cwr2_export.works.add(cls.original_work)
        cls.cwr2_export.works.add(cls.modified_work)
        cls.cwr2_export.create_cwr()
        rev = CWRExport.objects.create(
            description='Test REV', nwr_rev='REV')
        rev.works.add(cls.original_work)
        rev.works.add(cls.modified_work)
        rev.works.add(cls.copublished_work)
        rev.create_cwr()

    @classmethod
    def create_cwr3_export(cls):
        """Create a WRK and an ISR CWR3 Export. """
        cls.cwr3_export = CWRExport.objects.create(
            description='Test WRK', nwr_rev='WRK')
        cls.cwr3_export.works.add(cls.original_work)
        cls.cwr3_export.works.add(cls.modified_work)
        cls.cwr3_export.create_cwr()
        isr = CWRExport.objects.create(
            description='Test ISR', nwr_rev='ISR')
        isr.works.add(cls.original_work)
        isr.works.add(cls.modified_work)
        isr.works.add(cls.copublished_work)
        isr.create_cwr()

    @classmethod
    def setUpClass(cls):
        """Class setup.

        Creating users. Creating instances of classes of less importance:

        * label,
        * library,
        * artist,
        * releases,

        then calling the methods above.
        """
        super().setUpClass()
        cls.superuser = User.objects.create_superuser(
            'superuser', '', 'password')
        cls.staffuser = User.objects.create(
            username='staffuser', password='password', is_active=True,
            is_staff=True)
        cls.staffuser.groups.add(1)
        cls.audituser = User.objects.create(
            username='audituser', password='password', is_active=True,
            is_staff=True)
        cls.audituser.groups.add(2)
        cls.label = Label.objects.create(name='LABEL')
        cls.library = Library.objects.create(name='LIBRARY')
        cls.artist = Artist.objects.create(
            first_name='JOHN', last_name='DOE', isni='000000012146438X')
        cls.release = Release.objects.create(release_title='ALBUM')
        cls.library_release = Release.objects.create(
            release_title='LIBRELEASE', library_id=1, cd_identifier='XZY')
        cls.commercial_release = Release.objects.create(
            release_title='COMRELEASE')

        cls.create_writers()
        cls.create_modified_work()
        cls.create_original_work()
        cls.create_copublished_work()
        cls.create_cwr2_export()
        cls.create_cwr3_export()

    def test_strings(self):
        """Test __str__ methods for created objects."""
        self.assertEqual(
            str(self.original_work),
            'MK000002: THE WORK (DOE / DOE / SMITH)')
        self.assertEqual(
            str(self.generally_controlled_writer),
            'JOHN SMITH (*)')
        self.assertEqual(
            str(self.other_writer),
            'JANE DOE')
        self.assertEqual(
            str(self.writer_no_first_name),
            'JONES')
        self.assertEqual(
            str(self.original_work.writerinwork_set.first()),
            'JOHN SMITH (*)')
        self.assertEqual(
            str(self.modified_work.artistinwork_set.first()),
            'JOHN DOE')

    def test_unknown_user(self):
        """Several fast test to make sure that an unregistered user is blind.
        """
        for testing_admin in self.testing_admins:
            url = reverse(
                'admin:music_publisher_{}_changelist'.format(testing_admin))
            response = self.client.get(url, follow=False)
            self.assertEqual(response.status_code, 302)
            url = reverse(
                'admin:music_publisher_{}_add'.format(testing_admin))
            response = self.client.get(url, follow=False)
            self.assertEqual(response.status_code, 302)
            url = reverse(
                'admin:music_publisher_{}_change'.format(testing_admin),
                args=(1,))
            response = self.client.get(url, follow=False)
            self.assertEqual(response.status_code, 302)
            url = reverse('royalty_calculation')
            response = self.client.get(url, follow=False)
            self.assertEqual(response.status_code, 302)

    def test_super_user(self):
        """Testing index for superuser covers all the cases."""
        self.client.force_login(self.superuser)
        url = reverse('admin:index')
        response = self.client.get(url, follow=False)
        self.assertEqual(response.status_code, 200)

    def test_staff_user(self):
        """Test that a staff user can access some urls.

        Please note that most of the work is in other tests."""
        self.client.force_login(self.staffuser)
        # General checks
        url = reverse('admin:index')
        response = self.client.get(url, follow=False)
        self.assertEqual(response.status_code, 200)

        for testing_admin in self.testing_admins:
            url = reverse(
                'admin:music_publisher_{}_changelist'.format(testing_admin))
            response = self.client.get(url, follow=False)
            self.assertEqual(response.status_code, 200)
            url = reverse(
                'admin:music_publisher_{}_add'.format(testing_admin))
            response = self.client.get(url, follow=False)
            self.assertEqual(response.status_code, 200)
            url = reverse(
                'admin:music_publisher_{}_add'.format(testing_admin)
            ) + '?' + IS_POPUP_VAR + '=1'
            response = self.client.get(url, follow=False)
            self.assertEqual(response.status_code, 200)
            url = reverse(
                'admin:music_publisher_{}_change'.format(testing_admin),
                args=(1,))
            response = self.client.get(url, follow=False)
            self.assertEqual(response.status_code, 200)
            data = get_data_from_response(response)
            if testing_admin in ['cwrexport']:  # no change permission
                continue
            if 'first_name' in data:
                data['first_name'] += ' JR.'
            response = self.client.post(
                url, data=data, follow=False)
            self.assertEqual(response.status_code, 302)
        url = reverse('royalty_calculation')
        response = self.client.get(url, follow=False)
        self.assertEqual(response.status_code, 200)

    def test_cwr_previews(self):
        """Test that CWR preview works."""
        self.client.force_login(self.staffuser)
        for cwr_export in CWRExport.objects.all():
            url = reverse(
                'admin:music_publisher_cwrexport_change',
                args=(cwr_export.id,)) + '?preview=true'
            response = self.client.get(url, follow=False)
            self.assertEqual(response.status_code, 200)

    def test_cwr_downloads(self):
        """Test that the CWR file can be downloaded."""
        self.client.force_login(self.staffuser)
        for cwr_export in CWRExport.objects.all():
            url = reverse(
                'admin:music_publisher_cwrexport_change',
                args=(cwr_export.id,)) + '?download=true'
            response = self.client.get(url, follow=False)
            self.assertEqual(response.status_code, 200)

    def test_json(self):
        """Test that JSON export works."""
        self.client.force_login(self.staffuser)
        response = self.client.post(
            reverse('admin:music_publisher_work_changelist'),
            data={
                'action': 'create_json', 'select_across': 1,
                'index': 0, '_selected_action': self.original_work.id
            })
        self.assertEqual(response.status_code, 200)
        response = self.client.post(
            reverse('admin:music_publisher_libraryrelease_changelist'),
            data={
                'action': 'create_json', 'select_across': 1,
                'index': 0, '_selected_action': self.library_release.id
            })
        self.assertEqual(response.status_code, 200)
        response = self.client.post(
            reverse('admin:music_publisher_commercialrelease_changelist'),
            data={
                'action': 'create_json', 'select_across': 1,
                'index': 0, '_selected_action': self.library_release.id
            })
        self.assertEqual(response.status_code, 200)

    def test_cwr_nwr(self):
        """Test that CWR export works."""
        self.client.force_login(self.staffuser)
        response = self.client.post(
            reverse('admin:music_publisher_cwrexport_add'),
            data={
                'nwr_rev': 'NWR',
                'works': [
                    self.original_work.id,
                    self.modified_work.id,
                    self.copublished_work.id,
                ]
            })
        self.assertEqual(response.status_code, 302)
        cwr = CWRExport.objects.first().cwr
        self.assertIn('NWR0000000000000000THE MODIFIED WORK', cwr)
        self.assertIn('THE MODIFIED WORK BEHIND THE MODIFIED WORK', cwr)

    def test_csv(self):
        """Test that CSV export works."""
        self.client.force_login(self.staffuser)
        response = self.client.post(
            reverse('admin:music_publisher_work_changelist'),
            data={
                'action': 'create_csv', 'select_across': 1,
                'index': 0, '_selected_action': self.original_work.id
            })
        self.assertEqual(response.status_code, 200)

    def test_label_change(self):
        """Test that :class:`.models.Label` objects can be edited."""
        self.client.force_login(self.staffuser)
        url = reverse('admin:music_publisher_label_change', args=(1,))
        response = self.client.post(url, {'name': 'NEW LABEL'}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Label.objects.get(pk=1).name, 'NEW LABEL')

    def test_library_change(self):
        """Test that :class:`.models.Library` objects can be edited."""
        self.client.force_login(self.staffuser)
        url = reverse('admin:music_publisher_library_change', args=(1,))
        response = self.client.post(url, {'name': 'NEW LIBRARY'}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Library.objects.get(pk=1).name, 'NEW LIBRARY')

    def test_artist_change(self):
        """Test that :class:`.models.Artist` objects can be edited."""
        self.client.force_login(self.staffuser)
        url = reverse('admin:music_publisher_artist_change', args=(1,))
        response = self.client.post(url, {
            'last_name': 'DOVE',
            'first_name': 'JANE'
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Artist.objects.get(pk=1).last_name, 'DOVE')

    def test_commercialrelease_change(self):
        """Test that :class:`.models.CommercialRelease` can be edited."""
        self.client.force_login(self.staffuser)
        url = reverse(
            'admin:music_publisher_commercialrelease_change', args=(1,))
        response = self.client.post(
            url, {
                'release_title': 'NEW ALBUM',
                'ean': '4003994155486',
                'tracks-TOTAL_FORMS': 0,
                'tracks-INITIAL_FORMS': 0
            }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            CommercialRelease.objects.get(pk=1).release_title, 'NEW ALBUM')
        with self.assertRaises(LibraryRelease.DoesNotExist):
            LibraryRelease.objects.get(pk=1)

    def test_libraryrelease_change(self):
        """Test that :class:`.models.LibraryRelease` can be edited."""
        self.client.force_login(self.staffuser)
        url = reverse(
            'admin:music_publisher_libraryrelease_change', args=(2,)
        ) + '?' + IS_POPUP_VAR + '=1'
        response = self.client.post(
            url, {
                'release_title': 'LIB RELEASE',
                'library': '1',
                'cd_identifier': 'ABC',
            }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            LibraryRelease.objects.get(pk=2).release_title, 'LIB RELEASE')
        url = reverse(
            'admin:music_publisher_libraryrelease_change', args=(2,))
        response = self.client.post(
            url, {
                'release_title': 'LIBRARY RELEASE',
                'library': '1',
                'cd_identifier': 'ABC', 'tracks-TOTAL_FORMS': 0,
                'tracks-INITIAL_FORMS': 0
            }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            LibraryRelease.objects.get(pk=2).release_title,
            'LIBRARY RELEASE')
        with self.assertRaises(CommercialRelease.DoesNotExist):
            CommercialRelease.objects.get(pk=2)

    def test_audit_user(self):
        """Test that audit user can see, but not change things."""
        self.client.force_login(self.audituser)
        for testing_admin in self.testing_admins:
            url = reverse(
                'admin:music_publisher_{}_changelist'.format(testing_admin))
            response = self.client.get(url, follow=False)
            self.assertEqual(response.status_code, 200)
            url = reverse(
                'admin:music_publisher_{}_add'.format(testing_admin))
            response = self.client.get(url, follow=False)
            self.assertEqual(response.status_code, 403)

    def test_generally_controlled_not_controlled(self):
        """Test that a `controlled` flag must be set for a writer who is
        generally controlled."""
        self.client.force_login(self.staffuser)
        url = reverse(
            'admin:music_publisher_work_change', args=(1,))
        response = self.client.get(url, follow=False)
        data = get_data_from_response(response)
        data['writerinwork_set-0-controlled'] = False
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            b'Must be set for a generally controlled writer.',
            response.content)

    def test_generally_controlled_missing_capacity(self):
        """Test that if `controlled` flag is set, the `capacity` must be set
        as well."""
        self.client.force_login(self.staffuser)
        url = reverse(
            'admin:music_publisher_work_change', args=(1,))
        response = self.client.get(url, follow=False)
        data = get_data_from_response(response)
        data['writerinwork_set-0-capacity'] = ''
        data['writerinwork_set-0-capacity'] = ''
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            b'Must be set for a controlled writer.',
            response.content)

    def test_controlled_but_no_writer(self):
        """Test that a line without a writer can not have `controlled` set."""
        self.client.force_login(self.staffuser)
        url = reverse(
            'admin:music_publisher_work_change', args=(1,))
        response = self.client.get(url, follow=False)
        data = get_data_from_response(response)
        data['writerinwork_set-0-writer'] = ''
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            b'Must be set for a controlled writer.',
            response.content)

    def test_controlled_but_missing_data(self):
        """The requirements for a controlled writer are higher, make sure
        they are obeyed when setting a writer as controlled."""
        self.client.force_login(self.staffuser)
        url = reverse(
            'admin:music_publisher_work_change', args=(1,))
        response = self.client.get(url, follow=False)
        data = get_data_from_response(response)
        data['writerinwork_set-1-writer'] = self.other_writer.id
        data['writerinwork_set-1-controlled'] = True
        data['writerinwork_set-1-saan'] = 'WHATEVER'
        data['writerinwork_set-1-publisher_fee'] = '25.0'
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            b'IPI name and PR society must be set.',
            response.content)

    def test_controllable_and_controlled_but_missing_saan(self):
        """If SAAN is required, then it must be set in the Writer object,
        or in the WriterInWork object or both."""
        self.client.force_login(self.staffuser)
        url = reverse(
            'admin:music_publisher_work_change', args=(1,))
        response = self.client.get(url, follow=False)
        data = get_data_from_response(response)
        data['writerinwork_set-1-writer'] = self.controllable_writer.id
        data['writerinwork_set-1-controlled'] = True
        data['writerinwork_set-1-publisher_fee'] = '25.0'
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            b'Must be set. (controlled, no general agreement)',
            response.content)

    def test_controllable_and_controlled_but_missing_fee(self):
        """If `publisher_fee` is required, then it must be set in the Writer,
        or in the WriterInWork object or both."""
        self.client.force_login(self.staffuser)
        url = reverse(
            'admin:music_publisher_work_change', args=(1,))
        response = self.client.get(url, follow=False)
        data = get_data_from_response(response)
        data['writerinwork_set-1-writer'] = self.controllable_writer.id
        data['writerinwork_set-1-controlled'] = True
        data['writerinwork_set-1-saan'] = 'WHATEVER'
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            b'Must be set. (controlled, no general agreement)',
            response.content)

    def test_writer_switch(self):
        """Just replace one writer with another, just to test last change"""
        self.client.force_login(self.staffuser)
        url = reverse(
            'admin:music_publisher_work_change', args=(1,))
        # Make sure last_change is set by changing a value
        response = self.client.get(url, follow=False)
        data = get_data_from_response(response)
        data['writerinwork_set-1-writer'] = self.controllable_writer.id
        self.client.post(url, data)
        lc = Work.objects.filter(pk=1).first().last_change
        # Now modify it back and save
        data = get_data_from_response(response)
        data['writerinwork_set-1-writer'] = self.other_writer.id
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.assertGreater(Work.objects.filter(pk=1).first().last_change, lc)

    def test_not_controlled_extra_saan(self):
        """SAAN can not be set if a writer is not controlled."""
        self.client.force_login(self.staffuser)
        url = reverse(
            'admin:music_publisher_work_change', args=(1,))
        response = self.client.get(url, follow=False)
        data = get_data_from_response(response)
        data['writerinwork_set-1-writer'] = self.controllable_writer.id
        data['writerinwork_set-1-controlled'] = False
        data['writerinwork_set-1-saan'] = 'WHATEVER'
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            b'Must be empty if writer is not controlled.',
            response.content)

    def test_not_controlled_extra_fee(self):
        """Publisher fee can not be set if a writer is not controlled."""
        self.client.force_login(self.staffuser)
        url = reverse(
            'admin:music_publisher_work_change', args=(1,))
        response = self.client.get(url, follow=False)
        data = get_data_from_response(response)
        data['writerinwork_set-1-writer'] = self.controllable_writer.id
        data['writerinwork_set-1-controlled'] = False
        data['writerinwork_set-1-publisher_fee'] = '11.11'
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            b'Must be empty if writer is not controlled.',
            response.content)

    def test_bad_alt_title(self):
        """Test that alternate title can not have disallowed characters."""
        self.client.force_login(self.staffuser)
        url = reverse(
            'admin:music_publisher_work_change', args=(1,))
        response = self.client.get(url, follow=False)
        data = get_data_from_response(response)
        data['alternatetitle_set-1-title'] = 'LOŠ'
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            b'Title contains invalid characters.',
            response.content)

    def test_unallowed_capacity(self):
        """Some capacieties are allowed only in modifications."""
        self.client.force_login(self.staffuser)
        url = reverse('admin:music_publisher_work_change', args=(
            self.original_work.id,))
        response = self.client.get(url, follow=False)
        data = get_data_from_response(response)
        data['writerinwork_set-0-capacity'] = 'AR'
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            b'Not allowed in original works.',
            response.content)

    def test_missing_capacity(self):
        """At least one of the additional capacieties must be set for
        modifications."""
        self.client.force_login(self.staffuser)
        url = reverse('admin:music_publisher_work_change', args=(
            self.modified_work.id,))
        response = self.client.get(url, follow=False)
        data = get_data_from_response(response)
        data['writerinwork_set-0-capacity'] = 'CA'
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            b'At least one must be Arranger, Adaptor or Translator.',
            response.content)

    def test_none_controlled(self):
        """At least one Writer in Work line must be set as controlled."""
        self.client.force_login(self.staffuser)
        url = reverse('admin:music_publisher_work_change', args=(1,))
        response = self.client.get(url, follow=False)
        data = get_data_from_response(response)
        data['writerinwork_set-0-writer'] = self.controllable_writer.id
        data['writerinwork_set-0-controlled'] = False
        data['writerinwork_set-0-saan'] = ''
        data['writerinwork_set-0-publisher_fee'] = ''
        data['writerinwork_set-1-controlled'] = False
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            b'At least one writer must be controlled.',
            response.content)

    def test_wrong_sum_of_shares(self):
        """Sum of shares must be (roughly) 100%"""
        self.client.force_login(self.staffuser)
        url = reverse('admin:music_publisher_work_change', args=(1,))
        response = self.client.get(url, follow=False)
        data = get_data_from_response(response)
        data['writerinwork_set-0-relative_share'] = '60'
        data['writerinwork_set-1-relative_share'] = '60'
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            b'Sum of manuscript shares must be 100%.',
            response.content)

    def test_wrong_capacity_in_copublishing_modification(self):
        """Test the situation where one writer appears in two rows,
        once as controlled, once as not with different capacities."""
        self.client.force_login(self.staffuser)
        url = reverse('admin:music_publisher_work_change', args=(1,))
        response = self.client.get(url, follow=False)
        data = get_data_from_response(response)
        data['writerinwork_set-1-writer'] = self.controllable_writer.id
        data['writerinwork_set-0-writer'] = self.controllable_writer.id
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Must be same as in controlled line for this writer.',
                      response.content)

    def test_altitle_sufix_too_long(self):
        """A suffix plus the base title plus one space in between must be 60
        characters or less."""
        self.client.force_login(self.staffuser)
        url = reverse(
            'admin:music_publisher_work_change', args=(1,))
        response = self.client.get(url, follow=False)
        data = get_data_from_response(response)
        data['alternatetitle_set-1-title'] = 'A' * 55
        data['alternatetitle_set-1-suffix'] = True
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            b'Too long for suffix, work title plus suffix must be 59',
            response.content)

    def test_ack_import_and_work_filters(self):
        """Test acknowledgement import and then filters on the change view,
        as well as other related views.

        These tests must be together, ack import is used in filters.
        """

        self.client.force_login(self.staffuser)
        mock = StringIO()
        mock.write(ACK_CONTENT_21)

        """Upload the file that works, but with a wrong filename."""
        mock.seek(0)
        mockfile = InMemoryUploadedFile(
            mock, 'acknowledgement_file', 'CX180001000_FOO.V22',
            'text', 0, None)
        url = reverse('admin:music_publisher_ackimport_add')
        response = self.client.get(url)
        data = get_data_from_response(response)
        data.update({'acknowledgement_file': mockfile})
        response = self.client.post(url, data, follow=False)
        self.assertEqual(response.status_code, 200)

        ackimport = music_publisher.models.ACKImport.objects.first()
        self.assertIsNone(ackimport)

        """Upload the file that works."""
        mock.seek(0)
        mockfile = InMemoryUploadedFile(
            mock, 'acknowledgement_file', 'CW180001000_FOO.V21',
            'text', 0, None)
        url = reverse('admin:music_publisher_ackimport_add')
        response = self.client.get(url)
        data = get_data_from_response(response)
        data.update({'acknowledgement_file': mockfile, 'import_iswcs': 1})
        response = self.client.post(url, data, follow=False)
        self.assertEqual(response.status_code, 302)
        ackimport = music_publisher.models.ACKImport.objects.first()
        self.assertIsNotNone(ackimport)

        """And repeat the previous step, as duplicates are processed 
        differently."""
        mock.seek(0)
        mockfile = InMemoryUploadedFile(
            mock, 'acknowledgement_file', 'CW180001000_FOO.V21',
            'text', 0, None)
        url = reverse('admin:music_publisher_ackimport_add')
        response = self.client.get(url)
        data = get_data_from_response(response)
        data.update({'acknowledgement_file': mockfile})
        response = self.client.post(url, data, follow=False)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            music_publisher.models.ACKImport.objects.first().report, '')

        """This file has also ISWC codes."""
        mock = StringIO()
        mock.write(ACK_CONTENT_21_EXT)

        mock.seek(0)
        mockfile = InMemoryUploadedFile(
            mock, 'acknowledgement_file', 'CW180001000_FOO.V21',
            'text', 0, None)
        url = reverse('admin:music_publisher_ackimport_add')
        response = self.client.get(url)
        data = get_data_from_response(response)
        data.update({'acknowledgement_file': mockfile, 'import_iswcs': 1})
        # At this point, there is a different ISWC in one of the works
        with self.assertRaises(exceptions.ValidationError):
            self.client.post(url, data, follow=False)
        # Let's delete the one in the database and try again!
        mock.seek(0)
        self.original_work = Work.objects.get(id=self.original_work.id)
        self.original_work.iswc = None
        self.original_work.save()
        response = self.client.post(url, data, follow=False)
        self.assertEqual(response.status_code, 302)
        self.original_work = Work.objects.get(id=self.original_work.id)
        self.assertEqual(self.original_work.iswc, 'T9270264761')
        url = reverse(
            'admin:music_publisher_work_history',
            args=(self.original_work.id,))
        response = self.client.get(url)
        self.assertIn('staffuser'.encode(), response.content)

        """This file has bad ISWC codes."""
        mock = StringIO()
        mock.write(ACK_CONTENT_21_ERR)

        mock.seek(0)
        mockfile = InMemoryUploadedFile(
            mock, 'acknowledgement_file', 'CW180001000_FOO.V21',
            'text', 0, None)
        url = reverse('admin:music_publisher_ackimport_add')
        response = self.client.get(url)
        data = get_data_from_response(response)
        data.update({'acknowledgement_file': mockfile, 'import_iswcs': 1})
        response = self.client.post(url, data, follow=False)
        self.assertEqual(response.status_code, 302)

        """Test with a badly formatted file."""
        mock.seek(1)
        mockfile = InMemoryUploadedFile(
            mock, 'acknowledgement_file', 'CW180001000_FOO.V21',
            'text', 0, None)
        url = reverse('admin:music_publisher_ackimport_add')
        response = self.client.get(url)
        data = get_data_from_response(response)
        data.update({'acknowledgement_file': mockfile})
        response = self.client.post(url, data, follow=False)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Incorrect CWR header', response.content)

        """Test the change view and the CWR preview."""
        url = reverse(
            'admin:music_publisher_ackimport_change', args=(ackimport.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        url = reverse(
            'admin:music_publisher_ackimport_change', args=(ackimport.id,))
        response = self.client.get(url+'?preview=1')
        self.assertEqual(response.status_code, 200)

        """Test Work changelist filters."""
        self.client.force_login(self.audituser)
        base_url = reverse('admin:music_publisher_work_changelist')
        url = base_url + '?in_cwr=Y&ack_society=21&has_iswc=Y&has_rec=Y'
        response = self.client.get(url, follow=False)
        self.assertEqual(response.status_code, 200)
        url = base_url + '?in_cwr=N&ack_status=RA&has_iswc=N&has_rec=N'
        response = self.client.get(url, follow=False)
        self.assertEqual(response.status_code, 200)

        """Test dummy CWR ACK 3.0"""
        self.client.force_login(self.staffuser)
        mock = StringIO()
        mock.write(ACK_CONTENT_30)

        """Upload the file that works."""
        mock.seek(0)
        mockfile = InMemoryUploadedFile(
            mock, 'acknowledgement_file', 'CW180001000_FOO.V21',
            'text', 0, None)
        url = reverse('admin:music_publisher_ackimport_add')
        response = self.client.get(url)
        data = get_data_from_response(response)
        data.update({'acknowledgement_file': mockfile})
        response = self.client.post(url, data, follow=False)
        self.assertEqual(response.status_code, 302)
        ackimport = music_publisher.models.ACKImport.objects.first()
        self.assertIsNotNone(ackimport)

        """Test the change view and the CWR preview."""
        url = reverse(
            'admin:music_publisher_ackimport_change', args=(ackimport.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        url = reverse(
            'admin:music_publisher_ackimport_change', args=(ackimport.id,))
        response = self.client.get(url+'?preview=1')
        self.assertEqual(response.status_code, 200)

        """Upload the file that works."""
        mock.seek(0)
        mockfile = InMemoryUploadedFile(
            mock, 'acknowledgement_file', 'CW180001000_FOO.V21',
            'text', 0, None)
        url = reverse('admin:music_publisher_ackimport_add')
        response = self.client.get(url)
        data = get_data_from_response(response)
        data.update({'acknowledgement_file': mockfile})
        response = self.client.post(url, data, follow=False)
        self.assertEqual(response.status_code, 302)
        ackimport = music_publisher.models.ACKImport.objects.first()
        self.assertIsNotNone(ackimport)

        # required after acknowledgement imports because it lists
        # ack sources
        url = reverse('royalty_calculation')
        response = self.client.get(url, follow=False)
        self.assertEqual(response.status_code, 200)
        data = get_data_from_response(response)

    @override_settings(
        REQUIRE_SAAN=False, REQUIRE_PUBLISHER_FEE=False,
        PUBLISHING_AGREEMENT_PUBLISHER_SR=Decimal('1.0'))
    def test_data_import_and_royalty_calculations(self):
        """Test data import, ack import and royalty calculations.

        This is the normal process, work data is entered, then the registration
        follows and then it can be processed in royalty statements.

        This test also includes load testing, 200.000 rows must be imported
        in under 10-15 seconds, performed 4 times with different algos and
        ID types.
        """
        self.client.force_login(self.superuser)
        with open(TEST_DATA_IMPORT_FILENAME) as csvfile:
            mock = StringIO()
            mock.write(csvfile.read())
        mock.seek(0)
        mockfile = InMemoryUploadedFile(
            mock, 'acknowledgement_file', 'dataimport.csv',
            'text', 0, None)
        url = reverse('admin:music_publisher_dataimport_add')
        response = self.client.get(url)
        data = get_data_from_response(response)
        data.update({'data_file': mockfile})
        response = self.client.post(url, data, follow=False)
        self.assertEqual(response.status_code, 302)
        data_import = music_publisher.models.DataImport.objects.first()
        self.assertIsNotNone(data_import)
        self.assertIsNot(data_import.report, '')
        url = reverse('admin:music_publisher_dataimport_change',
                      args=(data_import.id,))
        response = self.client.get(url, follow=False)
        self.assertEqual(response.status_code, 200)

        self.client.force_login(self.staffuser)

        mock = StringIO()
        mock.write(ACK_CONTENT_21_EXT)
        mock.seek(0)
        mockfile = InMemoryUploadedFile(
            mock, 'acknowledgement_file', 'CW180001000_FOO.V21',
            'text', 0, None)
        url = reverse('admin:music_publisher_ackimport_add')
        response = self.client.get(url)
        data = get_data_from_response(response)
        data.update({'acknowledgement_file': mockfile})
        response = self.client.post(url, data, follow=False)
        self.assertEqual(response.status_code, 302)

        with open(TEST_ROYALTY_PROCESSING_FILENAME) as csvfile:
            mock = StringIO()
            mock.write(csvfile.read())
        mock.seek(0)
        mockfile = InMemoryUploadedFile(
            mock, 'statement_file', 'statement.csv',
            'text', 0, None)
        url = reverse('royalty_calculation')
        response = self.client.get(url)
        data = get_data_from_response(response)
        data.update({'in_file': mockfile})
        # Not enough data
        response = self.client.post(url, data, follow=False)
        self.assertFalse(hasattr(response, 'streaming_content'))

        # Enough data, fee, p
        mock.seek(0)
        data.update({
            'work_id_column': '1',
            'work_id_source': '52',
            'amount_column': '5',
        })
        response = self.client.post(url, data, follow=False)
        self.assertTrue(hasattr(response, 'streaming_content'))

        # Enough data, share, with rights column, ISWC
        mock.seek(0)
        data.update({
            'algo': 'share',
            'right_type_column': '3',
            'work_id_source': 'ISWC',
        })
        response = self.client.post(url, data, follow=False)
        self.assertTrue(hasattr(response, 'streaming_content'))

        # Enough data, share, with rights column, ISRC
        mock.seek(0)
        data.update({
            'work_id_source': 'ISRC',
        })
        response = self.client.post(url, data, follow=False)
        self.assertTrue(hasattr(response, 'streaming_content'))

        # Enough data, fee, sync
        mock.seek(0)
        data.update({
            'right_type_column': 's',
            'work_id_source': 'MK',
        })
        response = self.client.post(url, data, follow=False)
        self.assertTrue(hasattr(response, 'streaming_content'))

        # Enough data, fee, sync
        mock.seek(0)
        data.update({
            'right_type_column': 'm',
            'work_id_source': 'MK',
        })
        response = self.client.post(url, data, follow=False)
        self.assertTrue(hasattr(response, 'streaming_content'))

        # lets do one more thing here, copy work IDs to foreign work IDs.
        # to test the slowest use case, and fix work._work_id
        for i, work in enumerate(Work.objects.all()):
            work._work_id = work.work_id
            work.save()
            status = WorkAcknowledgement.TRANSACTION_STATUS_CHOICES[i % 12][0]
            society = ['52', '52', '52', '52', '44'][i % 5]
            WorkAcknowledgement(
                work=work, status=status, remote_work_id=work._work_id,
                society_code=society, date=datetime.now()).save()

        # 200K rows
        with open(TEST_ROYALTY_PROCESSING_LARGE_FILENAME) as csvfile:
            mock = StringIO()
            mock.write(csvfile.read())
        mockfile = InMemoryUploadedFile(
            mock, 'statement_file', 'statement.csv',
            'text', 0, None)
        url = reverse('royalty_calculation')
        response = self.client.get(url)
        data = get_data_from_response(response)

        # our ID
        mock.seek(0)
        data.update({
            'in_file': mockfile,
            'algo': 'share',
            'work_id_column': '0',
            'work_id_source': 'MK',
            'right_type_column': '4',
            'amount_column': '5',
        })
        time_before = datetime.now()
        response = self.client.post(url, data, follow=False)
        time_after = datetime.now()
        self.assertTrue(hasattr(response, 'streaming_content'))
        # The file must be processed in under 10 seconds
        self.assertLess((time_after - time_before).total_seconds(), 10)

        mock.seek(0)
        data.update({
            'algo': 'fee',
        })
        time_before = datetime.now()
        response = self.client.post(url, data, follow=False)
        time_after = datetime.now()
        self.assertTrue(hasattr(response, 'streaming_content'))
        # The file must be processed in under 10 seconds
        self.assertLess((time_after - time_before).total_seconds(), 10)

        mock.seek(0)
        data.update({
            'work_id_source': '52',
            'default_fee': '10.00',
        })
        time_before = datetime.now()
        response = self.client.post(url, data, follow=False)
        time_after = datetime.now()
        self.assertTrue(hasattr(response, 'streaming_content'))
        # The file must be processed in under 10 seconds
        self.assertLess((time_after - time_before).total_seconds(), 15)

        mock.seek(0)
        data.update({
            'algo': 'share',
            'work_id_column': '6',
            'work_id_source': 'ISRC',
        })
        time_before = datetime.now()
        response = self.client.post(url, data, follow=False)
        time_after = datetime.now()
        self.assertTrue(hasattr(response, 'streaming_content'))
        # The file must be processed in under 10 seconds
        self.assertLess((time_after - time_before).total_seconds(), 10)

    @override_settings(REQUIRE_SAAN=False, REQUIRE_PUBLISHER_FEE=False)
    def test_bad_data_import(self):
        """Test bad data import."""

        """Upload the completely bad file (CWR file in this case)."""
        self.client.force_login(self.superuser)
        with open(TEST_CWR2_FILENAME) as csvfile:
            mock = StringIO()
            mock.write(csvfile.read())
        mock.seek(0)
        mockfile = InMemoryUploadedFile(
            mock, 'acknowledgement_file', 'dataimport.csv',
            'text', 0, None)
        url = reverse('admin:music_publisher_dataimport_add')
        response = self.client.get(url)
        data = get_data_from_response(response)
        data.update({'data_file': mockfile})
        response = self.client.post(url, data, follow=False)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Unknown column', response.content)

    def test_recording_filters(self):
        """Test Work changelist filters."""

        self.client.force_login(self.audituser)
        base_url = reverse('admin:music_publisher_recording_changelist')
        url = base_url + '?has_isrc=Y'
        response = self.client.get(url, follow=False)
        self.assertEqual(response.status_code, 200)
        url = base_url + '?has_isrc=N'
        response = self.client.get(url, follow=False)
        self.assertEqual(response.status_code, 200)

    def test_search(self):
        """Test Work search."""

        self.client.force_login(self.staffuser)
        base_url = reverse('admin:music_publisher_work_changelist')
        url = base_url + '?q=01'
        response = self.client.get(url, follow=False)
        self.assertEqual(response.status_code, 200)

    def test_simple_save(self):
        """Test saving changed Work form."""
        self.client.force_login(self.staffuser)
        url = reverse('admin:music_publisher_work_change', args=(1,))
        response = self.client.get(url, follow=False)
        data = get_data_from_response(response)
        data['title'] = 'THE NEW TITLE'
        response = self.client.post(url, data, follow=False)
        self.assertEqual(response.status_code, 302)
        self.assertIsNotNone(Work.objects.filter(pk=1).first().last_change)

    def test_create_cwr_wizard(self):
        """Test if CWR creation action works as it should."""
        self.client.force_login(self.staffuser)
        url = reverse('admin:music_publisher_work_changelist')
        response = self.client.get(url, follow=False)
        data = get_data_from_response(response)
        data.update({
            'action': 'create_cwr', 'select_across': 1, 'index': 0,
            '_selected_action': 1
        })
        response = self.client.post(url, data, follow=False)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(b'error', response.content)

    @override_settings(PUBLISHER_CODE='')
    def test_create_cwr_wizard_no_publisher_code(self):
        """Publisher code is required for CWR generation, it must fail
        if attempted otherwise."""
        self.client.force_login(self.staffuser)
        url = reverse('admin:music_publisher_work_changelist')
        response = self.client.get(url, follow=False)
        data = get_data_from_response(response)
        data.update({
            'action': 'create_cwr', 'select_across': 1, 'index': 0,
            '_selected_action': 1
        })
        response = self.client.post(url, data, follow=False)
        self.assertEqual(response.status_code, 302)


class CWRTemplatesTest(SimpleTestCase):
    """A test related to CWR Templates."""
    RECORD_TYPES = [
        'ALT', 'GRH', 'GRT', 'HDR', 'WRK', 'OPU', 'OPT', 'ORN', 'OWR', 'PER',
        'PWR', 'REC', 'SPT', 'SPU', 'SWR', 'SWT', 'TRL', 'OWK']

    def test_templates(self):
        """Test CWR 2.1, 2.2 and 3.0 generation with empty values."""
        self.assertIsInstance(cwr_templates.TEMPLATES_21, dict)
        for i, key in enumerate(self.RECORD_TYPES):
            self.assertIn(key, cwr_templates.TEMPLATES_21)
            template = cwr_templates.TEMPLATES_21[key]
            d = {
                'transaction_sequence': i,
                'record_sequence': None,
                'first_name': None,
                'pr_society': '10',
                'share': Decimal('0.5')
            }
            self.assertIsInstance(template.render(Context(d)).upper(), str)
        self.assertIsInstance(cwr_templates.TEMPLATES_22, dict)
        for i, key in enumerate(self.RECORD_TYPES):
            self.assertIn(key, cwr_templates.TEMPLATES_22)
            template = cwr_templates.TEMPLATES_22[key]
            d = {
                'transaction_sequence': i,
                'record_sequence': None,
                'first_name': None,
                'pr_society': '10',
                'share': Decimal('0.5')
            }
            self.assertIsInstance(template.render(Context(d)).upper(), str)
        self.assertIsInstance(cwr_templates.TEMPLATES_30, dict)
        for i, key in enumerate(self.RECORD_TYPES):
            self.assertIn(key, cwr_templates.TEMPLATES_30)
            template = cwr_templates.TEMPLATES_30[key]
            d = {
                'transaction_sequence': i,
                'record_sequence': None,
                'first_name': None,
                'pr_society': '10',
                'share': Decimal('0.5')
            }
            self.assertIsInstance(template.render(Context(d)).upper(), str)


class ValidatorsTest(TestCase):
    """Test all validators.

    Note that validators are also validating settings."""

    @override_settings(PUBLISHER_NAME='Publisher, Inc.')
    def test_setting_publisher_name(self):
        with self.assertRaises(validators.ImproperlyConfigured):
            validators.validate_settings()

    @override_settings(PUBLISHER_CODE='Publisher')
    def test_setting_publisher_code(self):
        with self.assertRaises(validators.ImproperlyConfigured):
            validators.validate_settings()

    @override_settings(PUBLISHER_CODE='A,B')
    def test_setting_publisher_code_len(self):
        with self.assertRaises(validators.ImproperlyConfigured):
            validators.validate_settings()

    @override_settings(PUBLISHER_IPI_BASE='0000000199')
    def test_setting_publisher_ipi_base(self):
        with self.assertRaises(validators.ImproperlyConfigured):
            validators.validate_settings()

    @override_settings(PUBLISHER_IPI_NAME='0001000199')
    def test_setting_publisher_ipi_name(self):
        with self.assertRaises(validators.ImproperlyConfigured):
            validators.validate_settings()

    @override_settings(PUBLISHER_SOCIETY_MR='27')
    def test_setting_publisher_society(self):
        with self.assertRaises(validators.ImproperlyConfigured):
            validators.validate_settings()

    @override_settings(PUBLISHING_AGREEMENT_PUBLISHER_PR=Decimal('1.0'))
    def test_setting_publisher_agreement_pr(self):
        with self.assertRaises(validators.ImproperlyConfigured):
            validators.validate_settings()

    @override_settings(PUBLISHING_AGREEMENT_PUBLISHER_MR=Decimal('2.0'))
    def test_setting_publisher_agreement_mr(self):
        with self.assertRaises(validators.ImproperlyConfigured):
            validators.validate_settings()

    @override_settings(PUBLISHING_AGREEMENT_PUBLISHER_SR=Decimal('-1.0'))
    def test_setting_publisher_agreement_sr(self):
        with self.assertRaises(validators.ImproperlyConfigured):
            validators.validate_settings()

    def test_title(self):
        validator = validators.CWRFieldValidator('title')
        self.assertIsNone(validator('VALID TITLE'))
        with self.assertRaises(exceptions.ValidationError):
            validator('|Invalid')

    def test_isni(self):
        validator = validators.CWRFieldValidator('isni')
        self.assertIsNone(validator('000000000000001X'))
        with self.assertRaises(exceptions.ValidationError):
            validator('1X')
        with self.assertRaises(exceptions.ValidationError):
            validator('0000000000000010')

    def test_ean(self):
        validator = validators.CWRFieldValidator('ean')
        self.assertIsNone(validator('4006381333931'))
        with self.assertRaises(exceptions.ValidationError):
            validator('400638133393')
        with self.assertRaises(exceptions.ValidationError):
            validator('4006381333932')

    def test_iswc(self):
        validator = validators.CWRFieldValidator('iswc')
        self.assertIsNone(validator('T1234567894'))
        with self.assertRaises(exceptions.ValidationError):
            validator('I1234567894')
        with self.assertRaises(exceptions.ValidationError):
            validator('T1234567893')

    def test_isrc(self):
        validator = validators.CWRFieldValidator('isrc')
        self.assertIsNone(validator('USX1X1234567'))
        with self.assertRaises(exceptions.ValidationError):
            validator('USX1X123A567')

    def test_ipi_name(self):
        validator = validators.CWRFieldValidator('ipi_name')
        self.assertIsNone(validator('00000000199'))
        with self.assertRaises(exceptions.ValidationError):
            validator('0000000199')
        with self.assertRaises(exceptions.ValidationError):
            validator('00000000100')
        with self.assertRaises(exceptions.ValidationError):
            validator('0000000010A')

    def test_ipi_base(self):
        validator = validators.CWRFieldValidator('ipi_base')
        self.assertIsNone(validator('I-123456789-3'))
        with self.assertRaises(exceptions.ValidationError):
            validator('T-123456789-3')
        with self.assertRaises(exceptions.ValidationError):
            validator('I-123456789-4')

    def test_name(self):
        validator = validators.CWRFieldValidator('name')
        self.assertIsNone(validator('VALID NAME'))
        with self.assertRaises(exceptions.ValidationError):
            validator('NAME, INVALID')


@override_settings(
    PUBLISHER_NAME='TEST PUBLISHER',
    PUBLISHER_CODE='DMP',
    PUBLISHER_IPI_NAME='9000000020',
    PUBLISHER_SOCIETY_PR='52',
    PUBLISHER_SOCIETY_MR='44',
    PUBLISHER_SOCIETY_SR='44',
    REQUIRE_SAAN=True,
    REQUIRE_PUBLISHER_FEE=True,
    PUBLISHING_AGREEMENT_PUBLISHER_PR=Decimal('0.333333'),
    PUBLISHING_AGREEMENT_PUBLISHER_MR=Decimal('0.5'),
    PUBLISHING_AGREEMENT_PUBLISHER_SR=Decimal('0.75')
)
class ModelsSimpleTest(TransactionTestCase):
    """These tests are modifying objects directly."""
    reset_sequences = True

    def test_artist(self):
        artist = music_publisher.models.Artist(
            first_name='Matija', last_name='Kolarić')
        with self.assertRaises(exceptions.ValidationError):
            artist.clean_fields()
        artist = music_publisher.models.Artist(
            last_name='The Band', isni='1X')
        self.assertIsNone(artist.clean_fields())
        artist.save()
        self.assertEqual(str(artist), 'THE BAND')

    def test_commercial_release(self):
        label = music_publisher.models.Label(name='Music Label')
        label.save()
        self.assertEqual(str(label), 'MUSIC LABEL')
        release = music_publisher.models.CommercialRelease(
            release_title='Album', release_label=label)
        release.save()
        self.assertEqual(str(release), 'ALBUM (MUSIC LABEL)')
        release.release_label = None
        self.assertEqual(str(release), 'ALBUM')
        self.assertEqual(
            music_publisher.models.CommercialRelease.objects.count(), 1)

    def test_writer(self):
        writer = music_publisher.models.Writer(
            first_name='Matija', last_name='Kolarić')
        with self.assertRaises(exceptions.ValidationError):
            writer.clean_fields()
        writer = music_publisher.models.Writer(
            first_name='Matija', last_name='Kolaric', ipi_name='199',
            ipi_base='I-123.456.789-3', pr_society='10', saan='J44va',
            publisher_fee=50)
        self.assertEqual(str(writer), 'MATIJA KOLARIC')
        self.assertIsNone(writer.clean_fields())
        with self.assertRaises(exceptions.ValidationError):
            writer.clean()
        writer = music_publisher.models.Writer(
            first_name='Matija', last_name='Kolaric', ipi_name='199',
            generally_controlled=True)
        self.assertIsNone(writer.clean_fields())
        with self.assertRaises(exceptions.ValidationError):
            writer.clean()
        writer = music_publisher.models.Writer(
            first_name='Matija', last_name='Kolaric', ipi_name='199',
            ipi_base='I-123.456.789-3', pr_society='10',
            generally_controlled=True, saan='J44va', publisher_fee=50)
        self.assertIsNone(writer.clean_fields())
        self.assertIsNone(writer.clean())
        writer.save()
        self.assertEqual(str(writer), 'MATIJA KOLARIC (*)')

    def test_work(self):
        """A complex test where a complete Work objects with all related
        objects is created.

        """
        library = music_publisher.models.Library(name='Music Library')
        library.save()
        self.assertEqual(str(library), 'MUSIC LIBRARY')

        label = music_publisher.models.Label(name='Music Label')
        label.save()
        self.assertEqual(str(label), 'MUSIC LABEL')

        release = music_publisher.models.LibraryRelease(
            library=library, cd_identifier='ML001')
        release.save()
        self.assertEqual(str(release), 'ML001 (MUSIC LIBRARY)')
        self.assertIsNone(release.get_dict().get('title'))
        release.ean = '1X'
        with self.assertRaises(exceptions.ValidationError):
            release.clean()
        release.release_title = 'Test'
        self.assertEqual(str(release), 'ML001: TEST (MUSIC LIBRARY)')

        release.ean = None
        release.release_label = label
        release.clean_fields()
        release.clean()
        release.save()

        release2 = music_publisher.models.LibraryRelease(
            library=library, cd_identifier='ML002')
        release2.clean_fields()
        release2.clean()
        release2.save()

        work = music_publisher.models.Work(
            title='Muzički birtijaški crtići',
            library_release=release)
        with self.assertRaises(exceptions.ValidationError):
            work.clean_fields()
        work = music_publisher.models.Work(
            title='Music Pub Cartoons',
            iswc='T-123.456.789-4',
            original_title='Music Pub Cartoons',
            library_release=release)
        self.assertIsNone(work.clean_fields())
        self.assertEqual(str(work.work_id), '')
        self.assertTrue(work.is_modification())
        work.save()

        writer = music_publisher.models.Writer(
            first_name='Matija', last_name='Kolaric', ipi_name='199',
            ipi_base='I-123.456.789-3', pr_society='10',
            generally_controlled=True, saan='J44va', publisher_fee=50)
        writer.clean_fields()
        writer.clean()
        writer.save()

        writer2 = music_publisher.models.Writer(
            first_name='Ann', last_name='Other', ipi_name='297',
            pr_society='10')
        writer2.clean_fields()
        writer2.clean()
        writer2.save()

        music_publisher.models.WriterInWork.objects.create(
            work=work, writer=None, capacity='CA', relative_share=0,
            controlled=False)

        wiw = music_publisher.models.WriterInWork.objects.create(
            work=work, writer=writer, capacity='AR', relative_share=50,
            controlled=True)
        wiw.clean_fields()
        wiw.clean()

        self.assertEqual(str(wiw), 'MATIJA KOLARIC (*)')
        self.assertEqual(str(work), 'DMP000001: MUSIC PUB CARTOONS (KOLARIC)')

        music_publisher.models.WriterInWork.objects.create(
            work=work, writer=writer2, capacity='AD', relative_share=25,
            controlled=True)
        wiw = music_publisher.models.WriterInWork.objects.create(
            work=work, writer=writer2, capacity='AD', relative_share=25,
            controlled=False)
        wiw.clean_fields()
        wiw.clean()

        self.assertEqual(
            str(work), 'DMP000001: MUSIC PUB CARTOONS (KOLARIC / OTHER)')

        alt = work.alternatetitle_set.create(title='MPC Academy')
        self.assertEqual(str(alt), 'MPC ACADEMY')

        self.assertEqual(
            str(music_publisher.models.Recording().recording_id),
            '')

        rec = music_publisher.models.Recording.objects.create(
            work=work,
            recording_title='Work Recording',
            version_title='Work Recording feat. Testing',
            record_label=label
        )
        rec.clean_fields()
        rec.clean()

        rec2 = music_publisher.models.Recording.objects.create(
            work=work,
            recording_title='Suffix',
            recording_title_suffix=True,
            version_title='Co-suffix',
            version_title_suffix=True
        )
        rec.clean_fields()
        rec.clean()

        music_publisher.models.WorkAcknowledgement.objects.create(
            work=work,
            society_code='10',
            date=datetime.now(),
            status='RA'
        )

        music_publisher.models.WorkAcknowledgement.objects.create(
            work=work,
            society_code='51',
            remote_work_id='REMOTE1',
            date=datetime.now(),
            status='AS'
        )

        track = music_publisher.models.Track.objects.create(
            release=release,
            recording=rec,
            cut_number=1
        )
        track.clean_fields()
        track.clean()

        music_publisher.models.Track.objects.create(
            release=release2,
            recording=rec2,
            cut_number=2
        )

        # dict
        music_publisher.models.WorkManager().get_dict(
            qs=music_publisher.models.Work.objects.all())

        # test CWR 2.1 NWR
        TEST_CONTENT = open(TEST_CWR2_FILENAME, 'rb').read()
        cwr = music_publisher.models.CWRExport(nwr_rev='NWR')
        cwr.save()
        cwr.works.add(work)
        cwr.create_cwr()
        self.assertEqual(
            cwr.cwr.encode()[0:64], TEST_CONTENT[0:64])
        self.assertEqual(
            cwr.cwr.encode()[86:], TEST_CONTENT[86:])

        # test also CWR 3.0 WRK
        TEST_CONTENT = open(TEST_CWR3_FILENAME, 'rb').read()
        cwr = music_publisher.models.CWRExport(nwr_rev='WRK')
        cwr.save()
        cwr.works.add(work)
        cwr.create_cwr()
        self.assertEqual(
            cwr.cwr.encode()[0:65], TEST_CONTENT[0:65])
        self.assertEqual(
            cwr.cwr.encode()[167:], TEST_CONTENT[167:])
        # should just return when once created
        num = cwr.num_in_year
        cwr.create_cwr()
        self.assertEqual(cwr.num_in_year, num)

        # test also CWR 3.0 ISR
        TEST_CONTENT = open(TEST_ISR_FILENAME, 'rb').read()
        cwr = music_publisher.models.CWRExport(nwr_rev='ISR')
        cwr.save()
        cwr.works.add(work)
        cwr.create_cwr()
        self.assertEqual(
            cwr.cwr.encode()[0:65], TEST_CONTENT[0:65])
        self.assertEqual(
            cwr.cwr.encode()[167:], TEST_CONTENT[167:])

        # raises error because this writer is controlled in a work
        writer.pr_society = None
        writer.generally_controlled = False
        writer.publisher_fee = None
        writer.saan = None
        with self.assertRaises(exceptions.ValidationError):
            writer.clean()

       # test CWR 2.2 NWR
        cwr = music_publisher.models.CWRExport(nwr_rev='NW2')
        cwr.save()
        cwr.works.add(work)
        cwr.create_cwr()

       # test CWR 2.2 REV
        cwr = music_publisher.models.CWRExport(nwr_rev='RE2')
        cwr.save()
        cwr.works.add(work)
        cwr.create_cwr()

       # test CWR 3.1 WRK
        cwr = music_publisher.models.CWRExport(nwr_rev='WR1')
        cwr.save()
        cwr.works.add(work)
        cwr.create_cwr()


ACK_CONTENT_21 = """HDRSO000000021BMI                                          01.102018060715153220180607
GRHACK0000102.100020180607
ACK0000000000000000201805160910510000100000000NWRONE                                                         Z128                123                 20180607AS
ACK0000000100000000201805160910510000100000001NWRTWO                                                         Z127                                    20180607RA
ACK0000000200000000201805160910510000100000002NWRTHREE                                                       DMP000026                               20180607RA
ACK0000000300000000201805160910510000100000003NWRTHREE                                                       DMP000027                               20180607NP
ACK0000000400000000201805160910510000100000004NWRX                                                           DMP000025                               20180607NP
GRT000010000005000000007
TRL000010000005000000009"""


ACK_CONTENT_21_EXT = """HDRSO000000052PRS for Music                                01.102018060715153220180607
GRHACK0000102.100000000000
ACK0000000000000000202006031357150000100000000REVTHE MODIFIED WORK                                           MK000001            337739ES            20200603AS
REV0000000000000001THE MODIFIED WORK                                             MK000001      T927026487400000000            UNC000000Y      ORI                                                   N00000000000                                                   N
SPU000000000000000201MK       TEST PUBLISHER                                E 00000000000000000004              0520500004410000   10000 N
SPT0000000000000003MK             050001000010000I2136N001
SWR0000000000000004W000001  TESTIC                                       TESTO                          C 0000000000000000000005205000   00000   00000 N
SWT0000000000000005W000001  050000000000000I2136N001
PWR0000000000000006MK       TEST PUBLISHER                                                           W000001
ALT0000000000000007THE MODIFIED WORK 1                                         AT
ALT0000000000000008THE MODIFIED WORK 2                                         AT
ALT0000000000000009THE MODIFIED WORK 3                                         AT
ALT0000000000000010THE MODIFIED WORK 4                                         AT
REC000000000000001120200407                                                            000030                                                                                                                                                                        
REC000000000000001220170407                                                            000010                                                                                                                                                                        
REC000000000000001320170407                                                            000030                                                                                                                                                                        
REC000000000000001420170407                                                            000456                                                                                                                                                                        
ORN0000000000000015LIB                                                            MK001          0000TEST LIBRARY                                                                                                                                                                      0000
ACK0000000100000000202006031357150000100000001REVTHE WORK                                                    MK000002            337739DU            20200603AS
REV0000000100000001THE WORK                                                      MUM000002     T927026476100000000            UNC000000Y      ORI                                                   N00000000000                                                   N
SPU000000010000000201MK       TEST PUBLISHER                                E 00000000000000000004              0520500004410000   10000 N
SPT0000000100000003MK             050001000010000I2136N001
SWR0000000100000004W000001  TESTIC                                       TESTO                          C 0000000000000000000005205000   00000   00000 N
SWT0000000100000005W000001  050000000000000I2136N001
PWR0000000100000006MK       TEST PUBLISHER                                                           W000001
GRT000010000002000000025
TRL000010000002000000027"""

ACK_CONTENT_21_ERR = """HDRSO000000052PRS for Music                                01.102018060715153220180607
GRHACK0000102.100000000000
ACK0000000000000000202006031357150000100000000REVTHE MODIFIED WORK                                           MK000001            337739ES            20200603AS
REV0000000000000001THE MODIFIED WORK                                             MK000001      X927026487400000000            UNC000000Y      ORI                                                   N00000000000                                                   N
SPU000000000000000201MK       TEST PUBLISHER                                E 00000000000000000004              0520500004410000   10000 N
SPT0000000000000003MK             050001000010000I2136N001
SWR0000000000000004W000001  TESTIC                                       TESTO                          C 0000000000000000000005205000   00000   00000 N
SWT0000000000000005W000001  050000000000000I2136N001
PWR0000000000000006MK       TEST PUBLISHER                                                           W000001
ALT0000000000000007THE MODIFIED WORK 1                                         AT
ALT0000000000000008THE MODIFIED WORK 2                                         AT
ALT0000000000000009THE MODIFIED WORK 3                                         AT
ALT0000000000000010THE MODIFIED WORK 4                                         AT
REC000000000000001120200407                                                            000030                                                                                                                                                                        
REC000000000000001220170407                                                            000010                                                                                                                                                                        
REC000000000000001320170407                                                            000030                                                                                                                                                                        
REC000000000000001420170407                                                            000456                                                                                                                                                                        
ORN0000000000000015LIB                                                            MK001          0000TEST LIBRARY                                                                                                                                                                      0000
ACK0000000100000000202006031357150000100000001REVTHE WORK                                                    MK000002            337739DU            20200603AS
REV0000000100000001THE WORK                                                      MUM000002     T827026476100000000            UNC000000Y      ORI                                                   N00000000000                                                   N
SPU000000010000000201MK       TEST PUBLISHER                                E 00000000000000000004              0520500004410000   10000 N
SPT0000000100000003MK             050001000010000I2136N001
SWR0000000100000004W000001  TESTIC                                       TESTO                          C 0000000000000000000005205000   00000   00000 N
SWT0000000100000005W000001  050000000000000I2136N001
PWR0000000100000006MK       TEST PUBLISHER                                                           W000001
GRT000010000002000000025
TRL000010000002000000027"""

ACK_CONTENT_30 = """HDRSOBMI BMI                                          2018060715153220180607               3.0000
GRHACK0000102.100020180607
ACK0000000000000000201805160910510000100000000WRKONE                                                         MK000001            123                                     20180607AS
GRT000010000001000000003
TRL000010000001000000005"""

TEST_DATA_IMPORT_FILENAME = 'music_publisher/tests/dataimport.csv'
TEST_ROYALTY_PROCESSING_FILENAME = 'music_publisher/tests/royaltystatement.csv'
TEST_ROYALTY_PROCESSING_LARGE_FILENAME = 'music_publisher/tests/royaltystatement_200k_rows.csv'
TEST_CWR2_FILENAME = 'music_publisher/tests/CW210001DMP_000.V21'
TEST_CWR3_FILENAME = 'music_publisher/tests/CW210002DMP_0000_V3-0-0.SUB'
TEST_ISR_FILENAME = 'music_publisher/tests/CW210003DMP_0000_V3-0-0.ISR'