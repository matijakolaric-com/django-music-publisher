"""Tests for :mod:`music_publisher`.

Please note that all these tests are functional
(integration) tests, not unit tests.

Attributes:
    CONTENT (str): CWR ACK file contents
"""

from datetime import datetime
from decimal import Decimal
from io import StringIO

from django.contrib.admin.options import IS_POPUP_VAR
from django.contrib.auth.models import User
from django.core import exceptions
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.template import Context
from django.test import (
    SimpleTestCase, TestCase, TransactionTestCase, override_settings,
)
from django.urls import reverse

import music_publisher.models
from music_publisher.models import (
    AlternateTitle, Artist, CWRExport, CommercialRelease, Label, Library,
    LibraryRelease, Recording, Release, Work, Writer, WriterInWork,
)
from . import cwr_templates, validators


def get_data_from_response(response):
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

    fixtures = ['publishing_staff.json']
    testing_admins = [
        'artist', 'label', 'library', 'work', 'commercialrelease', 'writer',
        'recording', 'cwrexport', #'ackimport'
    ]

    @classmethod
    def create_original_work(cls):
        cls.original_work = Work.objects.create(
            title='The Work', iswc='T1234567893')
        WriterInWork.objects.create(work=cls.original_work,
            writer=cls.generally_controlled_writer, capacity='C ',
            relative_share=Decimal('50'), controlled=True)
        wiw = WriterInWork.objects.create(work=cls.original_work,
            writer=cls.other_writer, capacity='A ',
            relative_share=Decimal('25'), controlled=False)
        wiw = WriterInWork.objects.create(work=cls.original_work,
            writer=cls.controllable_writer, capacity='A ',
            relative_share=Decimal('25'), controlled=False)
        assert(wiw.get_agreement_dict() is None)
        AlternateTitle.objects.create(work=cls.original_work, suffix=True,
            title='Behind the Work')
        AlternateTitle.objects.create(work=cls.original_work, title='Work')
        Recording.objects.create(work=cls.original_work,
            record_label=cls.label, artist=cls.artist,
            isrc='US-S1Z-99-00001')

    @classmethod
    def create_modified_work(cls):
        cls.modified_work = Work.objects.create(
            title='The Modified Work', original_title='The Work')
        WriterInWork.objects.create(
            work=cls.modified_work,
            writer=cls.generally_controlled_writer,
            capacity='AR',
            relative_share=Decimal('100'),
            controlled=True,
            saan='SPECIAL',
            publisher_fee=Decimal('25')
        )
        WriterInWork.objects.create(
            work=cls.modified_work,
            writer=None,
            capacity='CA',
            relative_share=Decimal('0'),
            controlled=False
        )
        cls.modified_work.artists.add(cls.artist)
        AlternateTitle.objects.create(work=cls.modified_work, suffix=False,
            title='The Copy')
        AlternateTitle.objects.create(work=cls.modified_work, suffix=True,
            title='Behind the Modified Work')
        Recording.objects.create(work=cls.modified_work,
            isrc='US-S1Z-99-00002')

    @classmethod
    def create_copublished_work(cls):
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
        cls.generally_controlled_writer = Writer(first_name='John',
            last_name='Smith', ipi_name='00000000297', pr_society='52',
            ipi_base='I-123456789-3', sr_society='44',
            mr_society='44', generally_controlled=True, saan='A1B2C3',
            publisher_fee=Decimal('0.25'))
        cls.generally_controlled_writer.clean()
        cls.generally_controlled_writer.clean_fields()
        cls.generally_controlled_writer.save()
        cls.other_writer = Writer(first_name='Jane', last_name='Doe',
            ipi_name='395')
        cls.other_writer.clean()
        cls.other_writer.save()

        cls.writer_no_first_name = Writer(last_name='Jones')
        cls.writer_no_first_name.clean()
        cls.writer_no_first_name.save()
        cls.controllable_writer = Writer(first_name='Jack', last_name='Doe',
            ipi_name='493', pr_society='52', mr_society='44', sr_society='44')
        cls.controllable_writer.clean()
        cls.controllable_writer.save()

    @classmethod
    def create_cwr2_export(cls):
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

        cls.create_writers()
        cls.create_modified_work()
        cls.create_original_work()
        cls.create_copublished_work()
        cls.create_cwr2_export()
        cls.create_cwr3_export()

    def test_strings(self):
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

    def test_staff_user(self):

        self.client.force_login(self.staffuser)
        # General checks
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
            if 'first_name' in data:
                data['first_name'] += ' JR.'
            response = self.client.post(
                url, data=data, follow=False)
            self.assertEqual(response.status_code, 302)

    def test_cwr_previews(self):
        self.client.force_login(self.staffuser)
        for cwr_export in CWRExport.objects.all():
            url = reverse(
                'admin:music_publisher_cwrexport_change',
                args=(cwr_export.id,)) + '?preview=true'
            response = self.client.get(url, follow=False)
            self.assertEqual(response.status_code, 200)

    def test_cwr_downloads(self):
        self.client.force_login(self.staffuser)
        for cwr_export in CWRExport.objects.all():
            url = reverse(
                'admin:music_publisher_cwrexport_change',
                args=(cwr_export.id,)) + '?download=true'
            response = self.client.get(url, follow=False)
            self.assertEqual(response.status_code, 200)

    def test_json(self):
        self.client.force_login(self.staffuser)
        response = self.client.post(
        reverse('admin:music_publisher_work_changelist'),
        data={
            'action': 'create_json', 'select_across': 1,
            'index': 0, '_selected_action': self.original_work.id})
        self.assertEqual(response.status_code, 200)

    def test_label_change(self):
        self.client.force_login(self.staffuser)
        url = reverse('admin:music_publisher_label_change', args=(1,))
        response = self.client.post(url, {'name': 'NEW LABEL'}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Label.objects.get(pk=1).name, 'NEW LABEL')

    def test_library_change(self):
        self.client.force_login(self.staffuser)
        url = reverse('admin:music_publisher_library_change', args=(1,))
        response = self.client.post(url, {'name': 'NEW LIBRARY'}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Library.objects.get(pk=1).name, 'NEW LIBRARY')

    def test_artist_change(self):
        self.client.force_login(self.staffuser)
        url = reverse('admin:music_publisher_artist_change', args=(1,))
        response = self.client.post(url, {
            'last_name': 'DOVE',
            'first_name': 'JANE'
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Artist.objects.get(pk=1).last_name, 'DOVE')

    def test_commercialrelease_change(self):
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
        self.client.force_login(self.staffuser)
        url = reverse(
            'admin:music_publisher_work_change', args=(1,))
        response = self.client.get(url, follow=False)
        data = get_data_from_response(response)
        data['writerinwork_set-0-capacity'] = ''
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            b'Must be set for a controlled writer.',
            response.content)

    def test_controlled_but_no_writer(self):
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

    def test_not_controlled_extra_saan(self):
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
        self.client.force_login(self.staffuser)
        url = reverse('admin:music_publisher_work_change', args=(2,))
        response = self.client.get(url, follow=False)
        data = get_data_from_response(response)
        data['writerinwork_set-0-capacity'] = 'AR'
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            b'Not allowed in original works.',
            response.content)

    def test_missing_capacity(self):
        self.client.force_login(self.staffuser)
        url = reverse('admin:music_publisher_work_change', args=(1,))
        response = self.client.get(url, follow=False)
        data = get_data_from_response(response)
        data['writerinwork_set-0-capacity'] = 'CA'
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            b'At least one must be Arranger, Adaptor or Translator.',
            response.content)

    def test_none_controlled(self):
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
        self.client.force_login(self.staffuser)
        url = reverse('admin:music_publisher_work_change', args=(1,))
        response = self.client.get(url, follow=False)
        data = get_data_from_response(response)
        data['writerinwork_set-0-relative_share'] = '60'
        data['writerinwork_set-1-relative_share'] = '60'
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            b'Sum of relative shares must be 100%.',
            response.content)

    def test_wrong_capacity_in_copublishing_modification(self):
        self.client.force_login(self.staffuser)
        url = reverse('admin:music_publisher_work_change', args=(1,))
        response = self.client.get(url, follow=False)
        data = get_data_from_response(response)
        data['writerinwork_set-1-writer'] = self.controllable_writer.id
        data['writerinwork_set-0-writer'] = self.controllable_writer.id
        data['writerinwork_set-0-writer'] = self.controllable_writer.id
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Must be same as in controlled line for this writer.',
            response.content)

    def test_altitle_sufix_too_long(self):
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
        """Must be together, ack import is used in filters."""
        self.client.force_login(self.staffuser)
        mock = StringIO()
        mock.write(ACK_CONTENT)
        mock.seek(0)
        mockfile = InMemoryUploadedFile(mock, 'acknowledgement_file',
            'CX180001000_FOO.V22', 'text', 0, None)
        url = reverse('admin:music_publisher_ackimport_add')
        response = self.client.get(url)
        data = get_data_from_response(response)
        data.update({'acknowledgement_file': mockfile})
        response = self.client.post(url, data, follow=False)
        self.assertEqual(response.status_code, 200)
        ackimport = music_publisher.models.ACKImport.objects.first()
        self.assertIsNone(ackimport)
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
        url = reverse(
            'admin:music_publisher_ackimport_change', args=(ackimport.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        self.client.force_login(self.audituser)
        base_url = reverse('admin:music_publisher_work_changelist')
        url = base_url + '?in_cwr=Y&ack_society=21&has_iswc=Y&has_rec=Y'
        response = self.client.get(url, follow=False)
        self.assertEqual(response.status_code, 200)
        url = base_url + '?in_cwr=N&ack_status=RA&has_iswc=N&has_rec=N'
        response = self.client.get(url, follow=False)
        self.assertEqual(response.status_code, 200)

    def test_recording_filters(self):
        self.client.force_login(self.audituser)
        base_url = reverse('admin:music_publisher_recording_changelist')
        url = base_url + '?has_isrc=Y'
        response = self.client.get(url, follow=False)
        self.assertEqual(response.status_code, 200)
        url = base_url + '?has_isrc=N'
        response = self.client.get(url, follow=False)
        self.assertEqual(response.status_code, 200)

    def test_search(self):
        """Must be together, ack import is used in filters."""
        self.client.force_login(self.staffuser)
        base_url = reverse('admin:music_publisher_work_changelist')
        url = base_url + '?q=01'
        response = self.client.get(url, follow=False)
        self.assertEqual(response.status_code, 200)

    def test_simple_save(self):
        self.client.force_login(self.staffuser)
        url = reverse('admin:music_publisher_work_change', args=(1,))
        response = self.client.get(url, follow=False)
        data = get_data_from_response(response)
        data['title'] = 'THE NEW TITLE'
        response = self.client.post(url, data, follow=False)
        self.assertEqual(response.status_code, 302)

    def test_create_cwr_wizard(self):
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

    RECORD_TYPES = [
        'ALT', 'GRH', 'GRT', 'HDR', 'WRK', 'OPU', 'OPT', 'ORN', 'OWR', 'PER',
        'PWR', 'REC', 'SPT', 'SPU', 'SWR', 'SWT', 'TRL', 'OWK']

    def test_templates(self):
        self.assertIsInstance(cwr_templates.TEMPLATES_21, dict)
        for i, key in enumerate(self.RECORD_TYPES):
            self.assertIn(key, cwr_templates.TEMPLATES_21)
            template = cwr_templates.TEMPLATES_21[key]
            d = {
                'transaction_sequence': i,
                'record_sequence': None,
                'first_name': None,
                'pr_society': '10',
                'share': Decimal('0.5')}
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
                'share': Decimal('0.5')}
            self.assertIsInstance(template.render(Context(d)).upper(), str)


class ValidatorsTest(TestCase):

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
        validator = validators.CWRFieldValidator('work_title')
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
        validator = validators.CWRFieldValidator('last_name')
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
        self.assertIsNone(release.get_dict())
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
            release = release,
            recording = rec,
            cut_number = 1
        )
        track.clean_fields()
        track.clean()

        music_publisher.models.Track.objects.create(
            release = release2,
            recording = rec2,
            cut_number = 2
        )

        # normalized dict
        music_publisher.models.WorkManager().get_dict(
            qs=music_publisher.models.Work.objects.all())

        # cwr uses denormalized dict
        cwr = music_publisher.models.CWRExport(nwr_rev='NWR')
        cwr.save()
        cwr.works.add(work)
        cwr.create_cwr()
        self.assertEqual(cwr.cwr.encode()[0:64], CWR_1)

        # test also CWR 3.0 WRK
        cwr = music_publisher.models.CWRExport(nwr_rev='WRK')
        cwr.save()
        cwr.works.add(work)
        cwr.create_cwr()

        # test also CWR 3.0 ISR
        cwr = music_publisher.models.CWRExport(nwr_rev='ISR')
        cwr.save()
        cwr.works.add(work)
        cwr.create_cwr()

        # raises error because this writer is controlled in a work
        writer.pr_society = None
        writer.generally_controlled = False
        writer.publisher_fee = None
        writer.saan = None
        with self.assertRaises(exceptions.ValidationError):
            writer.clean()


ACK_CONTENT = """HDRSO000000021BMI                                          01.102018060715153220180607
GRHACK0000102.100020180607
ACK0000000000000000201805160910510000100000000NWRONE                                                         MK000001            123                 20180607AS
ACK0000000100000000201805160910510000100000001NWRTWO                                                         DMP000002                               20180607RA
ACK0000000200000000201805160910510000100000002NWRTHREE                                                       00000000000003                          20180607RA
ACK0000000300000000201805160910510000100000003NWRTHREE                                                       00000000000004                          20180607NP
ACK0000000400000000201805160910510000100000004NWRX                                                           0000000000000X                          20180607NP
TRL000010000008000000839"""

CWR_1 = b'HDR09000000020TEST PUBLISHER                               01.10'


#
#
# class IntegrationTest(TransactionTestCase):
#     """All integration tests in a single class.
#     """
#
#     reset_sequences = True
#     fixtures = ['publishing_staff.json']
#
#     def setUp(self):
#         """Set up the initial data.
#         """
#
#         self.user = User(
#             username='user', is_superuser=False, is_staff=True)
#         self.user.set_password('password')
#         self.user.save()
#         self.user.groups.add(1)
#
#
#     def get(self, path, re_post=None):
#         """A helper method that simulates opening of view and then simulates
#             manual changes and save.
#         """
#         response = self.client.get(path)
#         if response.status_code != 200:
#             return response
#         adminform = response.context_data.get('adminform')
#         if not re_post:
#             return response
#         data = {}
#         for sc in response.context:
#             for d in sc:
#                 if 'widget' in sc:
#                     if (sc['widget'].get('type') == 'select' and
#                             sc['widget']['selected'] is False):
#                         continue
#                     data[sc['widget']['name']] = sc['widget']['value']
#         if adminform:
#             data.update(adminform.form.initial)
#         if isinstance(re_post, dict):
#             data.update(re_post)
#         for key, value in data.items():
#             if value is None:
#                 data[key] = ''
#             else:
#                 data[key] = value
#         response = self.client.post(path, data)
#         return response
#
#     def test_admin_login(self):
#         """Basic navigation tests."""
#
#         response = self.get(reverse('admin:index'))
#         self.assertEqual(response.status_code, 302)
#         location = reverse('admin:login') + '?next=' + reverse('admin:index')
#         self.assertEqual(
#             response._headers.get('location'), (
#                 'Location',
#                 location))
#         response = self.get(location, re_post={
#             'username': 'user', 'password': 'wrongpassword'})
#         self.assertEqual(response.status_code, 200)
#         self.assertIn('errornote', response.content.decode())
#         response = self.get(location, re_post={
#             'username': 'user', 'password': 'password'})
#         self.assertEqual(response.status_code, 302)
#         self.assertEqual(
#             response._headers.get('location'), (
#                 'Location',
#                 reverse('admin:index')))
#
#     def test_1_indices(self):
#         self.client.force_login(self.user)
#         response = self.get(reverse('admin:index'))
#         self.assertEqual(response.status_code, 200)
#         response = self.get(
#             reverse('admin:app_list', args=('music_publisher',)))
#         self.assertEqual(response.status_code, 200)
#
#
#     def test_2_works(self):
#         self.client.force_login(self.user)
#         response = self.get(reverse('admin:music_publisher_work_changelist',))
#         self.assertEqual(response.status_code, 200)
#         response = self.get(
#             reverse('admin:music_publisher_label_add'),
#             re_post={
#                 'name': 'Label',
#             })
#         self.assertEqual(response.status_code, 302)
#         label = music_publisher.models.Label.objects.first()
#         response = self.get(reverse('admin:music_publisher_label_changelist',))
#         self.assertEqual(response.status_code, 200)
#
#         response = self.get(
#             reverse('admin:music_publisher_library_add'),
#             re_post={
#                 'name': 'Library',
#             })
#         self.assertEqual(response.status_code, 302)
#         library = music_publisher.models.Library.objects.first()
#         response = self.get(reverse('admin:music_publisher_library_changelist',))
#         self.assertEqual(response.status_code, 200)
#
#         response = self.get(
#             reverse('admin:music_publisher_writer_add'),
#             re_post={
#                 'last_name': 'Lošija',
#                 'ipi_name': 'X',
#                 'ipi_base': '1000000000'
#             })
#         self.assertEqual(response.status_code, 200)
#         self.assertIn('Name contains invalid', response.content.decode())
#         self.assertIn('Value must be numeric.', response.content.decode())
#         self.assertIn('I-NNNNNNNNN-C format', response.content.decode())
#         response = self.get(
#             reverse('admin:music_publisher_writer_add'),
#             re_post={
#                 'first_name': 'VERY',
#                 'last_name': 'COOL',
#                 'ipi_name': '100',
#                 'ipi_base': 'I-123456789-0'
#             })
#         self.assertEqual(response.status_code, 200)
#         self.assertIn('Not a valid IPI name', response.content.decode())
#         self.assertIn('Not valid:', response.content.decode())
#         response = self.get(
#             reverse('admin:music_publisher_writer_add'),
#             re_post={
#                 'first_name': 'VERY',
#                 'last_name': 'COOL',
#                 'ipi_name': '199',
#                 'ipi_base': 'I-123456789-3'
#             })
#         self.assertEqual(response.status_code, 302)
#         writer = music_publisher.models.Writer.objects.all().first()
#         self.assertFalse(writer._can_be_controlled)
#         response = self.get(
#             reverse('admin:music_publisher_writer_change', args=(
#                 writer.id,)),
#             re_post={
#                 'pr_society': '52'
#             })
#         self.assertEqual(response.status_code, 302)
#         writer = music_publisher.models.Writer.objects.all().first()
#         response = self.get(
#             reverse('admin:music_publisher_writer_add'),
#             re_post={
#                 'first_name': 'YANKEE',
#                 'last_name': 'DOODLE',
#                 'generally_controlled': 1,
#             })
#         self.assertEqual(response.status_code, 200)
#         self.assertIn('Unsufficient data for a', response.content.decode())
#         self.assertIn('This field is required.', response.content.decode())
#         response = self.get(
#             reverse('admin:music_publisher_writer_add'),
#             re_post={
#                 'first_name': 'YANKEE',
#                 'last_name': 'DOODLE',
#                 'ipi_name': '297',
#                 'pr_society': '010',
#                 'saan': 'DREAM',
#                 'publisher_fee': '100'
#             })
#         self.assertEqual(response.status_code, 200)
#         self.assertIn('Only for a general agreemen', response.content.decode())
#         response = self.get(
#             reverse('admin:music_publisher_writer_add'),
#             re_post={
#                 'first_name': 'YANKEE',
#                 'last_name': 'DOODLE',
#                 'ipi_name': '297',
#                 'pr_society': '10',
#                 'generally_controlled': 1,
#                 'saan': 'DREAM',
#                 'publisher_fee': '100'
#             })
#         self.assertEqual(response.status_code, 302)
#         writer2 = music_publisher.models.Writer.objects.filter(
#             pr_society='10').first()
#         response = self.get(
#             reverse('admin:music_publisher_writer_add'),
#             re_post={
#                 'last_name': 'THIRD',
#                 'ipi_name': '395',
#                 'pr_society': '10',
#             })
#         self.assertEqual(response.status_code, 302)
#         writer3 = music_publisher.models.Writer.objects.filter(
#             last_name='THIRD').first()
#         response = self.get(
#             reverse('admin:music_publisher_writer_add'),
#             re_post={
#                 'last_name': 'OTHER',
#             })
#         self.assertEqual(response.status_code, 302)
#         writer4 = music_publisher.models.Writer.objects.filter(
#             last_name='OTHER').first()
#         self.get(reverse('admin:music_publisher_writer_changelist'))
#         self.assertTrue(writer._can_be_controlled)
#         response = self.get(
#             reverse('admin:music_publisher_commercialrelease_add'),
#             re_post={
#                 'release_title': 'VERY COOL',
#                 'ean': '199',
#             })
#         self.assertEqual(response.status_code, 200)
#         self.assertIn('does not match EAN13 format', response.content.decode())
#         response = self.get(
#             reverse('admin:music_publisher_commercialrelease_add'),
#             re_post={
#                 'ean': '1234567890123',
#             })
#         self.assertEqual(response.status_code, 200)
#         self.assertIn('Invalid EAN.', response.content.decode())
#         response = self.get(
#             reverse('admin:music_publisher_libraryrelease_add'),
#             re_post={
#                 'cd_identifier': 'C00L',
#                 'ean': '1234567890123',
#             })
#         self.assertEqual(response.status_code, 200)
#         self.assertIn(
#             'Required if other release data is set.',
#             response.content.decode())
#         response = self.get(
#             reverse('admin:music_publisher_commercialrelease_add'),
#             re_post={
#                 'release_title': 'VERY COOL',
#             })
#         self.assertEqual(response.status_code, 302)
#         release = music_publisher.models.CommercialRelease.objects.all().first()
#         self.assertEqual(str(release), 'VERY COOL')
#         response = self.get(
#             reverse('admin:music_publisher_commercialrelease_change', args=(
#                 release.id,)),
#             re_post={
#                 'release_date': '2018-01-01',
#                 'ean': '4006381333931',
#             })
#         self.assertEqual(response.status_code, 302)
#         release = music_publisher.models.CommercialRelease.objects.all().first()
#         response = self.get(
#             reverse('admin:music_publisher_commercialrelease_changelist'))
#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(str(release), 'VERY COOL')
#         response = self.get(
#             reverse('admin:music_publisher_artist_add'),
#             re_post={
#                 'first_name': 'VERY',
#                 'last_name': 'VERY COOL',
#                 'isni': '1234567890123',
#             })
#         self.assertEqual(response.status_code, 200)
#         response = self.get(
#             reverse('admin:music_publisher_artist_add'),
#             re_post={
#                 'last_name': 'VERY COOL',
#                 'isni': '12345678SD23',
#             })
#         self.assertEqual(response.status_code, 200)
#         response = self.get(
#             reverse('admin:music_publisher_artist_add',),
#             re_post={
#                 'first_name': 'VERY',
#                 'last_name': 'VERY COOL',
#                 'isni': '1X',
#             })
#         artist = music_publisher.models.Artist.objects.all().first()
#         self.assertEqual(response.status_code, 302)
#         response = self.get(
#             reverse('admin:music_publisher_artist_changelist'))
#         self.assertEqual(response.status_code, 200)
#
#         response = self.get(
#             reverse('admin:music_publisher_work_add'),
#             re_post={
#                 'title': 'LOŠ NASLOV',
#                 'iswc': 'ADC',
#                 'writerinwork_set-0-writer': writer.id,
#                 'writerinwork_set-0-capacity': 'XX',
#                 'writerinwork_set-0-relative_share': '100',
#                 'writerinwork_set-0-controlled': '1',
#                 'writerinwork_set-0-saan': '1LJ4V4',
#                 'writerinwork_set-0-publisher_fee': '25',
#             })
#         self.assertEqual(response.status_code, 200)
#         self.assertIn('Title contains invalid', response.content.decode())
#         self.assertIn('match TNNNNNNNNNC', response.content.decode())
#         response = self.get(
#             reverse('admin:music_publisher_work_add'),
#             re_post={
#                 'title': 'GOOD TITLE',
#                 'iswc': 'T1234567893',
#                 'writerinwork_set-0-writer': writer.id,
#                 'writerinwork_set-0-capacity': 'CA',
#                 'writerinwork_set-0-relative_share': '50',
#                 'writerinwork_set-0-controlled': '',
#                 'writerinwork_set-0-saan': '',
#                 'writerinwork_set-0-publisher_fee': '',
#                 'writerinwork_set-1-writer': writer.id,
#                 'writerinwork_set-1-capacity': 'CA',
#                 'writerinwork_set-1-relative_share': '50',
#                 'writerinwork_set-1-controlled': '',
#                 'writerinwork_set-1-saan': '',
#                 'writerinwork_set-1-publisher_fee': '',
#                 'recordings-TOTAL_FORMS': 1,
#                 'recordings-0-isrc': 'USX1X12345',
#             })
#         self.assertEqual(response.status_code, 200)
#         self.assertIn('must be controlled', response.content.decode())
#         self.assertIn('not match ISRC', response.content.decode())
#         response = self.get(
#             reverse('admin:music_publisher_work_add'),
#             re_post={
#                 'title': 'GOOD TITLE',
#                 'iswc': 'T1234567894',
#                 'alternatetitle_set-TOTAL_FORMS': 2,
#                 'alternatetitle_set-0-title': 'BETTER TITLE',
#                 'alternatetitle_set-1-suffix': '1',
#                 'alternatetitle_set-1-title':
#                     'WITH SUFFIX THAT IS WAY TOO LONG FOR THIS '
#                     'ALTERNATE TITLE',
#                 'writerinwork_set-TOTAL_FORMS': 5,
#                 'writerinwork_set-0-writer': writer.id,
#                 'writerinwork_set-0-capacity': 'CA',
#                 'writerinwork_set-0-relative_share': '25',
#                 'writerinwork_set-0-controlled': '1',
#                 'writerinwork_set-0-saan': '1LJ4V4',
#                 'writerinwork_set-0-publisher_fee': '25',
#                 'writerinwork_set-1-writer': writer2.id,
#                 'writerinwork_set-1-capacity': 'CA',
#                 'writerinwork_set-1-relative_share': '11.66',
#                 'writerinwork_set-1-controlled': '1',
#                 'writerinwork_set-2-writer': writer3.id,
#                 'writerinwork_set-2-capacity': 'A ',
#                 'writerinwork_set-2-relative_share': '33.33',
#                 'writerinwork_set-2-controlled': '1',
#                 'writerinwork_set-2-saan': '1LJ4V4',
#                 'writerinwork_set-2-publisher_fee': '25',
#                 'writerinwork_set-3-writer': writer.id,
#                 'writerinwork_set-3-capacity': 'CA',
#                 'writerinwork_set-3-relative_share': '25',
#                 'writerinwork_set-4-writer': writer3.id,
#                 'writerinwork_set-4-relative_share': '5',
#                 'recordings-TOTAL_FORMS': 1,
#                 'recordings-0-artist': artist.id,
#                 'recordings-0-isrc': 'USX1X1234567',
#                 'recordings-0-duration': '01:23',
#                 'recordings-0-release_date': '2018-01-31',
#             })
#         self.assertEqual(response.status_code, 200)
#         response = self.get(
#             reverse('admin:music_publisher_work_add'),
#             re_post={
#                 'title': 'GOOD TITLE',
#                 'iswc': 'T1234567894',
#                 'alternatetitle_set-TOTAL_FORMS': 2,
#                 'alternatetitle_set-0-title': 'BETTER TITLE',
#                 'alternatetitle_set-1-suffix': '1',
#                 'alternatetitle_set-1-title': 'WITH SUFFIX',
#                 'writerinwork_set-TOTAL_FORMS': 5,
#                 'writerinwork_set-0-writer': writer.id,
#                 'writerinwork_set-0-capacity': 'CA',
#                 'writerinwork_set-0-relative_share': '25',
#                 'writerinwork_set-0-controlled': '1',
#                 'writerinwork_set-0-saan': '1LJ4V4',
#                 'writerinwork_set-0-publisher_fee': '25',
#                 'writerinwork_set-1-writer': writer2.id,
#                 'writerinwork_set-1-capacity': 'CA',
#                 'writerinwork_set-1-relative_share': '11.66',
#                 'writerinwork_set-1-controlled': '1',
#                 'writerinwork_set-2-writer': writer3.id,
#                 'writerinwork_set-2-capacity': 'A ',
#                 'writerinwork_set-2-relative_share': '33.33',
#                 'writerinwork_set-2-controlled': '1',
#                 'writerinwork_set-2-saan': '1LJ4V4',
#                 'writerinwork_set-2-publisher_fee': '25',
#                 'writerinwork_set-3-writer': writer.id,
#                 'writerinwork_set-3-capacity': 'CA',
#                 'writerinwork_set-3-relative_share': '25',
#                 'writerinwork_set-4-writer': writer3.id,
#                 'writerinwork_set-4-relative_share': '5',
#                 'recordings-TOTAL_FORMS': 2,
#                 'recordings-0-artist': artist.id,
#                 'recordings-0-isrc': 'USX1X1234567',
#                 'recordings-0-duration': '01:23',
#                 'recordings-0-release_date': '2018-01-31',
#                 'recordings-1-record_label': label.id,
#
#             })
#         self.assertEqual(response.status_code, 302)
#         work = music_publisher.models.Work.objects.all().first()
#         self.assertEqual(str(work.alternatetitle_set.last()), 'BETTER TITLE')
#         response = self.get(
#             reverse('admin:music_publisher_work_add'),
#             re_post={
#                 'title': 'MODIFICATION1',
#                 'original_title': 'ORIGINAL',
#                 'writerinwork_set-TOTAL_FORMS': 4,
#                 'writerinwork_set-0-writer': writer.id,
#                 'writerinwork_set-0-capacity': 'CA',
#                 'writerinwork_set-0-relative_share': '25',
#                 'writerinwork_set-0-controlled': '1',
#                 'writerinwork_set-0-saan': '1LJ4V4',
#                 'writerinwork_set-0-publisher_fee': '25',
#                 'writerinwork_set-1-writer': writer.id,
#                 'writerinwork_set-1-capacity': 'CA',
#                 'writerinwork_set-1-relative_share': '25',
#                 'writerinwork_set-2-writer': writer3.id,
#                 'writerinwork_set-2-relative_share': '25',
#                 'writerinwork_set-3-relative_share': '25',
#                 'artistinwork_set-TOTAL_FORMS': 1,
#                 'artistinwork_set-0-artist': artist.id,
#             })
#         self.assertEqual(response.status_code, 200)
#         self.assertIn('one writer must be Arranger', response.content.decode())
#         response = self.get(
#             reverse('admin:music_publisher_work_add'),
#             re_post={
#                 'title': 'MODIFICATION2',
#                 'original_title': 'ORIGINAL',
#                 'writerinwork_set-TOTAL_FORMS': 4,
#                 'writerinwork_set-0-writer': writer.id,
#                 'writerinwork_set-0-capacity': 'CA',
#                 'writerinwork_set-0-relative_share': '25',
#                 'writerinwork_set-0-controlled': '1',
#                 'writerinwork_set-0-saan': '1LJ4V4',
#                 'writerinwork_set-0-publisher_fee': '25',
#                 'writerinwork_set-1-writer': writer.id,
#                 'writerinwork_set-1-capacity': 'AR',
#                 'writerinwork_set-1-relative_share': '25',
#                 'writerinwork_set-2-writer': writer3.id,
#                 'writerinwork_set-2-relative_share': '25',
#                 'writerinwork_set-3-relative_share': '25',
#                 'artistinwork_set-TOTAL_FORMS': 1,
#                 'artistinwork_set-0-artist': artist.id,
#             })
#         self.assertEqual(response.status_code, 200)
#         self.assertIn('same as in controlled', response.content.decode())
#         response = self.get(
#             reverse('admin:music_publisher_work_add'),
#             re_post={
#                 'title': 'MODIFICATION',
#                 'original_title': 'ORIGINAL',
#                 'writerinwork_set-TOTAL_FORMS': 4,
#                 'writerinwork_set-0-writer': writer.id,
#                 'writerinwork_set-0-capacity': 'AR',
#                 'writerinwork_set-0-relative_share': '25',
#                 'writerinwork_set-0-controlled': '1',
#                 'writerinwork_set-0-saan': '1LJ4V4',
#                 'writerinwork_set-0-publisher_fee': '25',
#                 'writerinwork_set-1-writer': writer.id,
#                 'writerinwork_set-1-capacity': 'AR',
#                 'writerinwork_set-1-relative_share': '25',
#                 'writerinwork_set-2-writer': writer3.id,
#                 'writerinwork_set-2-relative_share': '25',
#                 'writerinwork_set-2-capacity': 'CA',
#                 'writerinwork_set-3-relative_share': '25',
#                 'artistinwork_set-TOTAL_FORMS': 1,
#                 'artistinwork_set-0-artist': artist.id,
#
#             })
#         self.assertEqual(response.status_code, 302)
#         work2 = music_publisher.models.Work.objects.filter(title='MODIFICATION').first()
#         response = self.get(
#             reverse('admin:music_publisher_work_add'),
#             re_post={
#                 'title': 'NO COMPOSER TITLE',
#                 'writerinwork_set-0-writer': writer.id,
#                 'writerinwork_set-0-capacity': 'A ',
#                 'writerinwork_set-0-relative_share': '100',
#                 'writerinwork_set-0-controlled': '1',
#                 'writerinwork_set-0-saan': '1LJ4V4',
#                 'writerinwork_set-0-publisher_fee': '25',
#             })
#         self.assertEqual(response.status_code, 200)
#         response = self.get(
#             reverse('admin:music_publisher_work_add'),
#             re_post={
#                 'title': 'OVER 100 PERCENT',
#                 'writerinwork_set-0-writer': writer.id,
#                 'writerinwork_set-0-capacity': 'CA',
#                 'writerinwork_set-0-relative_share': '101',
#                 'writerinwork_set-0-controlled': '1',
#                 'writerinwork_set-0-saan': '1LJ4V4',
#                 'writerinwork_set-0-publisher_fee': '25',
#             })
#         self.assertEqual(response.status_code, 200)
#         response = self.get(
#             reverse('admin:music_publisher_work_add'),
#             re_post={
#                 'title': 'ORIGINAL WITH AN ARRANGER',
#                 'writerinwork_set-TOTAL_FORMS': 2,
#                 'writerinwork_set-0-writer': writer.id,
#                 'writerinwork_set-0-capacity': 'CA',
#                 'writerinwork_set-0-relative_share': '0',
#                 'writerinwork_set-1-writer': writer2.id,
#                 'writerinwork_set-1-capacity': 'AR',
#                 'writerinwork_set-1-relative_share': '100',
#                 'writerinwork_set-1-controlled': '1',
#             })
#         self.assertEqual(response.status_code, 200)
#         self.assertIn('Not allowed in original', response.content.decode())
#         response = self.get(
#             reverse('admin:music_publisher_work_changelist'))
#         response = self.get(
#             reverse('admin:music_publisher_work_change', args=(work.id,)))
#         PREFIX = settings.MUSIC_PUBLISHER_SETTINGS['work_id_prefix']
#         settings.MUSIC_PUBLISHER_SETTINGS['work_id_prefix'] = ''
#         response = self.get(
#             reverse('admin:music_publisher_cwrexport_add'),
#             re_post={'nwr_rev': 'NWR', 'works': [work.id, work2.id]})
#         settings.MUSIC_PUBLISHER_SETTINGS['work_id_prefix'] = PREFIX
#         cwr_export = music_publisher.models.CWRExport.objects.all().first()
#         response = self.get(
#             reverse('admin:music_publisher_cwrexport_add'),
#             re_post={'nwr_rev': 'WRK', 'works': [work.id, work2.id]})
#         response = self.get(
#             reverse(
#                 'admin:music_publisher_cwrexport_change',
#                 args=(cwr_export.id,)),
#             re_post={'nwr_rev': 'REV', 'works': [work.id, work2.id]})
#         cwr_exports = music_publisher.models.CWRExport.objects.all()
#         for cwr_export in cwr_exports:
#             response = self.get(
#                 '{}?download=1'.format(
#                     reverse(
#                         'admin:music_publisher_work_change',
#                         args=(cwr_export.id,))))
#             self.assertEqual(response.status_code, 200)
#             response = self.client.post(
#                 reverse('admin:music_publisher_work_changelist'),
#                 data={
#                     'action': 'create_cwr', 'select_across': 1,
#                     'index': 0, '_selected_action': work.id})
#             response = self.get(
#                 reverse('admin:music_publisher_cwrexport_changelist'))
#
#             self.assertEqual(response.status_code, 200)
#             response = self.get(reverse(
#                 'admin:music_publisher_cwrexport_change', args=(cwr_export.id,)))
#             self.assertEqual(response.status_code, 200)
#             response = self.client.get(reverse(
#                 'admin:music_publisher_cwrexport_change',
#                 args=(cwr_export.id,)) + '?download=true',)
#             self.assertEqual(response.status_code, 200)
#             response = self.client.get(reverse(
#                 'admin:music_publisher_cwrexport_change',
#                 args=(cwr_export.id,)) + '?preview=true',)
#             self.assertEqual(response.status_code, 200)
#
#         response = self.get(
#             reverse('admin:music_publisher_work_changelist',) +
#             '?has_iswc=N&has_rec=Y&in_cwr=Y')
#         self.assertEqual(response.status_code, 200)
#         self.get(
#             reverse('admin:music_publisher_work_changelist',) +
#             '?has_iswc=Y&has_rec=N&in_cwr=N&q=01')
#         self.get(
#             reverse('admin:music_publisher_work_changelist',) +
#             '?ack_society=021')
#         self.assertEqual(response.status_code, 200)
#         response = self.get(
#             reverse('admin:music_publisher_artist_changelist') + '?_popup=1')
#         self.assertEqual(response.status_code, 200)
#         response = self.get(
#             reverse('admin:music_publisher_commercialrelease_changelist'))
#         self.assertEqual(response.status_code, 200)
#         response = self.get(
#             reverse('admin:music_publisher_commercialrelease_add'))
#         self.assertEqual(response.status_code, 200)
#         response = self.get(
#             reverse('admin:music_publisher_commercialrelease_add') + '?_popup=1')
#         self.assertEqual(response.status_code, 200)
#         response = self.get(
#             reverse('admin:music_publisher_libraryrelease_add'))
#         self.assertEqual(response.status_code, 200)
#         response = self.get(
#             reverse('admin:music_publisher_libraryrelease_add') + '?_popup=1',
#             re_post={
#                 'library': library.id,
#                 'cd_identifier': 'CD0001',
#             }
#         )
#         self.assertEqual(response.status_code, 200)
#         response = self.get(
#             reverse('admin:music_publisher_libraryrelease_changelist'))
#         self.assertEqual(response.status_code, 200)
#         response = self.get(
#             reverse('admin:music_publisher_work_add') + '?_popup=1')
#         self.assertEqual(response.status_code, 200)
#         response = self.get(
#             reverse('admin:music_publisher_work_add'),
#             re_post={
#                 'title': 'LIBRARY',
#                 'library_release': music_publisher.models.LibraryRelease.objects.first().id,
#                 'writerinwork_set-TOTAL_FORMS': 1,
#                 'writerinwork_set-0-writer': writer.id,
#                 'writerinwork_set-0-capacity': 'CA',
#                 'writerinwork_set-0-relative_share': '100',
#                 'writerinwork_set-0-controlled': '1',
#                 'writerinwork_set-0-saan': '1LJ4V4',
#                 'writerinwork_set-0-publisher_fee': '25',
#             })
#         self.assertEqual(response.status_code, 302)
#         response = self.get(
#             reverse('admin:music_publisher_work_changelist'))
#         self.assertEqual(response.status_code, 200)
#         response = self.get(
#             reverse('admin:music_publisher_recording_changelist') +
#             '?has_isrc=N')
#         self.assertEqual(response.status_code, 200)
#         response = self.get(
#             reverse('admin:music_publisher_recording_changelist') +
#             '?has_isrc=Y')
#         self.assertEqual(response.status_code, 200)
#         mock = StringIO()
#         mock.write(ACK_CONTENT)
#         mock.seek(0)
#         mockfile = InMemoryUploadedFile(
#             mock, 'acknowledgement_file', 'CW180001000_FOO.V21',
#             'text', 0, None)
#         response = self.get(
#             reverse('admin:music_publisher_ackimport_add'),
#             re_post={'acknowledgement_file': mockfile})
#         self.assertEqual(response.status_code, 302)
#         # ackimport = music_publisher.models.ACKImport.objects.first()
#         # # open and repost
#         # mock.seek(0)
#         # mockfile = InMemoryUploadedFile(
#         #     mock, 'acknowledgement_file', 'CW180001000_FOO.V21',
#         #     'text', 0, None)
#         # response = self.get(reverse(
#         #     'admin:music_publisher_ackimport_change', args=(ackimport.id,)),
#         #     re_post={'acknowledgement_file': mockfile})
#         # self.assertEqual(response.status_code, 302)
#         # # second pass, same thing
#         # mock.seek(0)
#         # mockfile = InMemoryUploadedFile(
#         #     mock, 'acknowledgement_file', 'CW180001000_FOO.V21',
#         #     'text', 0, None)
#         # response = self.get(
#         #     reverse('admin:music_publisher_ackimport_add'),
#         #     re_post={'acknowledgement_file': mockfile})
#         # self.assertEqual(response.status_code, 302)
#         # # incorrect filename
#         # mock.seek(0)
#         # mockfile = InMemoryUploadedFile(
#         #     mock, 'acknowledgement_file', 'CW180001000_FOO.V22',
#         #     'text', 0, None)
#         # response = self.get(
#         #     reverse('admin:music_publisher_ackimport_add'),
#         #     re_post={'acknowledgement_file': mockfile})
#         # self.assertEqual(response.status_code, 200)
#         # # incorrect header
#         # mock.seek(3)
#         # mockfile = InMemoryUploadedFile(
#         #     mock, 'acknowledgement_file', 'CW180001000_FOO.V21',
#         #     'text', 0, None)
#         # response = self.get(
#         #     reverse('admin:music_publisher_ackimport_add'),
#         #     re_post={'acknowledgement_file': mockfile})
#         # self.assertEqual(response.status_code, 200)
#         # Removing needed data from controlled writer
#         response = self.get(
#             reverse('admin:music_publisher_writer_change', args=(
#                 writer.id,)),
#             re_post={
#                 'pr_society': ''
#             })
#         self.assertEqual(response.status_code, 200)
#         self.assertIn('controlled in at least', response.content.decode())
#         response = self.get(
#             reverse('admin:music_publisher_work_change', args=(work.id,)),
#             re_post={
#                 'title': 'GOOD TITLE',
#                 'iswc': 'T1234567894',
#                 'alternatetitle_set-TOTAL_FORMS': 1,
#                 'alternatetitle_set-0-title': 'BETTER TITLE',
#                 'writerinwork_set-TOTAL_FORMS': 2,
#                 'writerinwork_set-0-writer': '',
#                 'writerinwork_set-0-capacity': 'CA',
#                 'writerinwork_set-0-relative_share': '50',
#                 'writerinwork_set-0-controlled': '1',
#                 'writerinwork_set-0-saan': '1LJ4V4',
#                 'writerinwork_set-0-publisher_fee': '25',
#                 'writerinwork_set-1-writer': writer4.id,
#                 'writerinwork_set-1-capacity': 'CA',
#                 'writerinwork_set-1-relative_share': '50',
#                 'writerinwork_set-1-controlled': '1',
#                 'recordings-TOTAL_FORMS': 1,
#                 'recordings-0-artist': artist.id,
#                 'recordings-0-isrc': 'USX1X1234567',
#                 'recordings-0-duration': '01:23',
#                 'recordings-0-release_date': '2018-01-31',
#             })
#         self.assertEqual(response.status_code, 200)
#         self.assertIn('Must be set for', response.content.decode())
#         response = self.get(
#             reverse('admin:music_publisher_work_change', args=(work.id,)),
#             re_post={
#                 'title': 'GOOD TITLE',
#                 'iswc': 'T1234567894',
#                 'alternatetitle_set-TOTAL_FORMS': 1,
#                 'alternatetitle_set-0-title': 'BETTER TITLE',
#                 'writerinwork_set-TOTAL_FORMS': 3,
#                 'writerinwork_set-0-writer': writer.id,
#                 'writerinwork_set-0-capacity': 'CA',
#                 'writerinwork_set-0-relative_share': '50',
#                 'writerinwork_set-0-controlled': '1',
#                 'writerinwork_set-0-saan': '1LJ4V4',
#                 'writerinwork_set-0-publisher_fee': '25',
#                 'writerinwork_set-1-writer': writer2.id,
#                 'writerinwork_set-1-capacity': 'CA',
#                 'writerinwork_set-1-relative_share': '25',
#                 'writerinwork_set-1-controlled': '',
#                 'writerinwork_set-2-writer': writer4.id,
#                 'writerinwork_set-2-saan': '1LJ4V4',
#                 'writerinwork_set-2-publisher_fee': '25',
#                 'recordings-TOTAL_FORMS': 1,
#                 'recordings-0-artist': artist.id,
#                 'recordings-0-isrc': 'USX1X1234567',
#                 'recordings-0-duration': '01:23',
#                 'recordings-0-release_date': '2018-01-31',
#             })
#         self.assertEqual(response.status_code, 200)
#         self.assertIn('Must be set for', response.content.decode())
#         # JSON must be at the end, so the export is complete
#         response = self.client.post(
#             reverse('admin:music_publisher_work_changelist'),
#             data={
#                 'action': 'create_json', 'select_across': 1,
#                 'index': 0, '_selected_action': work.id})
#         response = self.client.post(
#             reverse('admin:music_publisher_work_changelist'),
#             data={
#                 'action': 'create_normalized_json', 'select_across': 1,
#                 'index': 0, '_selected_action': work.id})
#         self.assertEqual(str(music_publisher.models.WorkAcknowledgement.objects.first()), 'RA')
#         # Moved to the end, after the ACK file has been imported
#         self.get(
#             reverse('admin:music_publisher_work_changelist',) +
#             '?ack_society=21&ack_status=AS')
# #
# #     def test_3_works(self):
# #         self.client.force_login(self.user)
# #         response = self.get(reverse('admin:music_publisher_work_changelist',))
# #         self.assertEqual(response.status_code, 200)
# #         response = self.get(
# #             reverse('admin:music_publisher_writer_add'),
# #             re_post={
# #                 'last_name': 'Lošija',
# #                 'ipi_name': 'X',
# #                 'ipi_base': '1000000000'
# #             })
# #         self.assertEqual(response.status_code, 200)
# #         self.assertIn('Name contains invalid', response.content.decode())
# #         self.assertIn('Value must be numeric.', response.content.decode())
# #         self.assertIn('I-NNNNNNNNN-C format', response.content.decode())
# #         response = self.get(
# #             reverse('admin:music_publisher_writer_add'),
# #             re_post={
# #                 'first_name': 'VERY',
# #                 'last_name': 'COOL',
# #                 'ipi_name': '100',
# #                 'ipi_base': 'I-123456789-0'
# #             })
# #         self.assertEqual(response.status_code, 200)
# #         self.assertIn('Not a valid IPI name', response.content.decode())
# #         self.assertIn('Not valid:', response.content.decode())
# #         response = self.get(
# #             reverse('admin:music_publisher_writer_add'),
# #             re_post={
# #                 'first_name': 'VERY',
# #                 'last_name': 'COOL',
# #                 'ipi_name': '199',
# #                 'ipi_base': 'I-123456789-3'
# #             })
# #         self.assertEqual(response.status_code, 302)
# #         writer = Writer.objects.all().first()
# #         self.assertFalse(writer._can_be_controlled)
# #         response = self.get(
# #             reverse('admin:music_publisher_writer_change', args=(
# #                 writer.id,)),
# #             re_post={
# #                 'pr_society': '52'
# #             })
# #         self.assertEqual(response.status_code, 302)
# #         writer = Writer.objects.all().first()
# #         response = self.get(
# #             reverse('admin:music_publisher_writer_add'),
# #             re_post={
# #                 'first_name': 'YANKEE',
# #                 'last_name': 'DOODLE',
# #                 'generally_controlled': 1,
# #             })
# #         self.assertEqual(response.status_code, 200)
# #         self.assertIn('Unsufficient data for a', response.content.decode())
# #         self.assertIn('This field is required.', response.content.decode())
# #         response = self.get(
# #             reverse('admin:music_publisher_writer_add'),
# #             re_post={
# #                 'first_name': 'YANKEE',
# #                 'last_name': 'DOODLE',
# #                 'ipi_name': '297',
# #                 'pr_society': '010',
# #                 'saan': 'DREAM',
# #                 'publisher_fee': '100'
# #             })
# #         self.assertEqual(response.status_code, 200)
# #         self.assertIn('Only for a general agreemen', response.content.decode())
# #         response = self.get(
# #             reverse('admin:music_publisher_writer_add'),
# #             re_post={
# #                 'first_name': 'YANKEE',
# #                 'last_name': 'DOODLE',
# #                 'ipi_name': '297',
# #                 'pr_society': '10',
# #                 'generally_controlled': 1,
# #                 'saan': 'DREAM',
# #                 'publisher_fee': '100'
# #             })
# #         self.assertEqual(response.status_code, 302)
# #         writer2 = Writer.objects.filter(pr_society='10').first()
# #         response = self.get(
# #             reverse('admin:music_publisher_writer_add'),
# #             re_post={
# #                 'last_name': 'THIRD',
# #                 'ipi_name': '395',
# #                 'pr_society': '10',
# #             })
# #         self.assertEqual(response.status_code, 302)
# #         writer3 = Writer.objects.filter(last_name='THIRD').first()
# #         response = self.get(
# #             reverse('admin:music_publisher_writer_add'),
# #             re_post={
# #                 'last_name': 'OTHER',
# #             })
# #         self.assertEqual(response.status_code, 302)
# #         writer4 = Writer.objects.filter(last_name='OTHER').first()
# #         response = self.get(
# #             reverse('admin:music_publisher_writer_changelist'))
# #         self.assertTrue(writer._can_be_controlled)
# #         response = self.get(
# #             reverse('admin:music_publisher_commercialrelease_add'),
# #             re_post={
# #                 'album_title': 'VERY COOL',
# #                 'ean': '199',
# #             })
# #         self.assertEqual(response.status_code, 200)
# #         self.assertIn('does not match EAN13 format', response.content.decode())
# #         response = self.get(
# #             reverse('admin:music_publisher_commercialrelease_add'),
# #             re_post={
# #                 'ean': '1234567890123',
# #             })
# #         self.assertEqual(response.status_code, 200)
# #         self.assertIn('Invalid EAN.', response.content.decode())
# #         response = self.get(
# #             reverse('admin:music_publisher_libraryrelease_add'),
# #             re_post={
# #                 'cd_identifier': 'C00L',
# #                 'ean': '1234567890123',
# #             })
# #         self.assertEqual(response.status_code, 200)
# #         self.assertIn(
# #             'Required if other release data is set.',
# #             response.content.decode())
# #         response = self.get(
# #             reverse('admin:music_publisher_commercialrelease_add'),
# #             re_post={
# #                 'release_title': 'VERY COOL',
# #             })
# #         self.assertEqual(response.status_code, 302)
# #         release = CommercialRelease.objects.all().first()
# #         self.assertEqual(str(release), 'VERY COOL')
# #         response = self.get(
# #             reverse('admin:music_publisher_release_change', args=(
# #                 release.id,)),
# #             re_post={
# #                 'release_date': '2018-01-01',
# #                 'ean': '4006381333931',
# #             })
# #         self.assertEqual(response.status_code, 302)
# #         release = CommercialRelease.objects.all().first()
# #         response = self.get(
# #             reverse('admin:music_publisher_release_changelist'))
# #         self.assertEqual(response.status_code, 200)
# #         self.assertEqual(str(release), 'VERY COOL')
# #         response = self.get(
# #             reverse('admin:music_publisher_artist_add'),
# #             re_post={
# #                 'first_name': 'VERY',
# #                 'last_name': 'VERY COOL',
# #                 'isni': '1234567890123',
# #             })
# #         self.assertEqual(response.status_code, 200)
# #         response = self.get(
# #             reverse('admin:music_publisher_artist_add'),
# #             re_post={
# #                 'last_name': 'VERY COOL',
# #                 'isni': '12345678SD23',
# #             })
# #         self.assertEqual(response.status_code, 200)
# #         response = self.get(
# #             reverse('admin:music_publisher_artist_add',),
# #             re_post={
# #                 'first_name': 'VERY',
# #                 'last_name': 'VERY COOL',
# #                 'isni': '1X',
# #             })
# #         self.assertEqual(response.status_code, 302)
# #         artist = Artist.objects.all().first()
# #         response = self.get(
# #             reverse('admin:music_publisher_artist_changelist'))
# #         self.assertEqual(response.status_code, 200)
# #
# #         response = self.get(
# #             reverse('admin:music_publisher_work_add'),
# #             re_post={
# #                 'title': 'LOŠ NASLOV',
# #                 'iswc': 'ADC',
# #                 'writerinwork_set-0-writer': writer.id,
# #                 'writerinwork_set-0-capacity': 'XX',
# #                 'writerinwork_set-0-relative_share': '100',
# #                 'writerinwork_set-0-controlled': '1',
# #                 'writerinwork_set-0-saan': '1LJ4V4',
# #                 'writerinwork_set-0-publisher_fee': '25',
# #             })
# #         self.assertEqual(response.status_code, 200)
# #         self.assertIn('Title contains invalid', response.content.decode())
# #         self.assertIn('match TNNNNNNNNNC', response.content.decode())
# #         response = self.get(
# #             reverse('admin:music_publisher_work_add'),
# #             re_post={
# #                 'title': 'GOOD TITLE',
# #                 'iswc': 'T1234567893',
# #                 'writerinwork_set-0-writer': writer.id,
# #                 'writerinwork_set-0-capacity': 'CA',
# #                 'writerinwork_set-0-relative_share': '50',
# #                 'writerinwork_set-0-controlled': '',
# #                 'writerinwork_set-0-saan': '',
# #                 'writerinwork_set-0-publisher_fee': '',
# #                 'writerinwork_set-1-writer': writer.id,
# #                 'writerinwork_set-1-capacity': 'CA',
# #                 'writerinwork_set-1-relative_share': '50',
# #                 'writerinwork_set-1-controlled': '',
# #                 'writerinwork_set-1-saan': '',
# #                 'writerinwork_set-1-publisher_fee': '',
# #                 'recordings-TOTAL_FORMS': 1,
# #                 'recordings-0-isrc': 'USX1X12345',
# #             })
# #         self.assertEqual(response.status_code, 200)
# #         self.assertIn('must be controlled', response.content.decode())
# #         self.assertIn('not match ISRC', response.content.decode())
# #         response = self.get(
# #             reverse('admin:music_publisher_work_add'),
# #             re_post={
# #                 'title': 'GOOD TITLE',
# #                 'iswc': 'T1234567894',
# #                 'alternatetitle_set-TOTAL_FORMS': 2,
# #                 'alternatetitle_set-0-title': 'BETTER TITLE',
# #                 'alternatetitle_set-1-suffix': '1',
# #                 'alternatetitle_set-1-title': 'WITH SUFFIX',
# #                 'writerinwork_set-TOTAL_FORMS': 5,
# #                 'writerinwork_set-0-writer': writer.id,
# #                 'writerinwork_set-0-capacity': 'CA',
# #                 'writerinwork_set-0-relative_share': '25',
# #                 'writerinwork_set-0-controlled': '1',
# #                 'writerinwork_set-0-saan': '1LJ4V4',
# #                 'writerinwork_set-0-publisher_fee': '25',
# #                 'writerinwork_set-1-writer': writer2.id,
# #                 'writerinwork_set-1-capacity': 'CA',
# #                 'writerinwork_set-1-relative_share': '11.66',
# #                 'writerinwork_set-1-controlled': '1',
# #                 'writerinwork_set-2-writer': writer3.id,
# #                 'writerinwork_set-2-capacity': 'A ',
# #                 'writerinwork_set-2-relative_share': '33.33',
# #                 'writerinwork_set-2-controlled': '1',
# #                 'writerinwork_set-2-saan': '1LJ4V4',
# #                 'writerinwork_set-2-publisher_fee': '25',
# #                 'writerinwork_set-3-writer': writer.id,
# #                 'writerinwork_set-3-capacity': 'CA',
# #                 'writerinwork_set-3-relative_share': '25',
# #                 'writerinwork_set-4-writer': writer3.id,
# #                 'writerinwork_set-4-relative_share': '5',
# #                 'recordings-TOTAL_FORMS': 1,
# #                 'recordings-0-artist': artist.id,
# #                 'recordings-0-isrc': 'USX1X1234567',
# #                 'recordings-0-duration': '01:23',
# #                 'recordings-0-release_date': '2018-01-31',
# #             })
# #         self.assertEqual(response.status_code, 302)
# #         # work = Work.objects.all().first()
# #         # response = self.get(
# #         #     reverse('admin:music_publisher_cwrexport_add'),
# #         #     re_post={'nwr_rev': 'NWR', 'works': [work.id]})
# #         # response = self.client.post(
# #         #     reverse('admin:music_publisher_work_changelist'),
# #         #     data={
# #         #         'action': 'create_normalized_json', 'select_across': 1,
# #         #         'index': 0, '_selected_action': work.id})
# #
# # PATH = os.path.join(
# #     os.path.dirname(__file__), 'cwrexample.txt')
# # CWR_CONTENT = open(PATH, 'rb').read().decode()
