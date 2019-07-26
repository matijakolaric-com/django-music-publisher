"""Tests for :mod:`music_publisher`.

Please note that all these tests are functional
(integration) tests, not unit tests.

Attributes:
    CONTENT (str): CWR ACK file contents
"""

from . import const, cwr_templates, validators

import music_publisher.models
from django.template import Context
from django.core import exceptions

from django.test import TestCase, SimpleTestCase, TransactionTestCase

# from django.contrib.auth.models import User
# from django.core.files.uploadedfile import InMemoryUploadedFile
# from music_publisher.admin import *
# from music_publisher.models import *
# from io import StringIO
# import os


class ConstTest(SimpleTestCase):

    def test_const(self):
        self.assertIsInstance(const.SETTINGS, dict)
        self.assertIsInstance(const.SOCIETY_DICT, dict)
        for soc in const.SOCIETIES:
            self.assertIsInstance(soc, tuple)
            self.assertIsInstance(soc[0], str)
            self.assertNotEqual(soc[0], '0')
            self.assertTrue(soc[0].isnumeric())
        self.assertIn('publisher_id', const.SETTINGS)
        self.assertIn('publisher_name', const.SETTINGS)
        self.assertIn('publisher_ipi_name', const.SETTINGS)
        self.assertIn('publisher_pr_society', const.SETTINGS)
        for key in ['publisher_pr_society',
                    'publisher_mr_society',
                    'publisher_sr_society']:
            if key in const.SETTINGS:
                self.assertIn(const.SETTINGS[key], const.SOCIETY_DICT)


class CWRTemplatesTest(SimpleTestCase):

    RECORD_TYPES = [
        'ALT', 'GRH', 'GRT', 'HDR', 'NWR', 'OPU', 'ORN', 'OWR', 'PER', 'PWR',
        'REC', 'SPT', 'SPU', 'SWR', 'SWT', 'TRL', 'VER']

    def test_templates(self):
        self.assertIsInstance(cwr_templates.TEMPLATES_21, dict)
        for key in self.RECORD_TYPES:
            self.assertIn(key, cwr_templates.TEMPLATES_21)
            template = cwr_templates.TEMPLATES_21[key]
            self.assertIsInstance(template.render(Context({})).upper(), str)


class ValidatorsTest(SimpleTestCase):

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
            validator('000000000000011')

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


class ModelsSimpleTest(TransactionTestCase):

    reset_sequences = True

    def test_artist(self):
        artist = music_publisher.models.Artist(
            first_name='Matija', last_name='Kolarić')
        with self.assertRaises(exceptions.ValidationError):
            artist.clean_fields()
        artist = music_publisher.models.Artist(
            first_name='Matija', last_name='Kolaric', isni='1X')
        self.assertIsNone(artist.clean_fields())
        artist.save()
        self.assertEqual(str(artist), 'MATIJA KOLARIC')
        self.assertDictEqual(artist.get_dict(), {
            'code': 'A000001',
            'first_name': 'Matija',
            'isni': '000000000000001X',
            'last_name': 'Kolaric'})

    def test_library_release(self):
        library = music_publisher.models.Library(name='Music Library')
        library.save()
        self.assertEqual(str(library), 'MUSIC LIBRARY')
        self.assertDictEqual(library.get_dict(), {
            'code': 'LI000001',
            'name': 'Music Library'})
        release = music_publisher.models.LibraryRelease(
            library=library, cd_identifier='ML001')
        release.save()
        self.assertEqual(str(release), 'ML001 (MUSIC LIBRARY)')
        self.assertIsNone(release.get_dict())
        self.assertDictEqual(release.get_origin_dict(), {
            'origin_type': {'code': 'LIB', 'name': 'Library Work'},
             'cd_identifier': 'ML001',
             'library': {'code': 'LI000001', 'name': 'Music Library'}})

    def test_commercial_release(self):
        label = music_publisher.models.Label(name='Music Label')
        label.save()
        self.assertEqual(str(label), 'MUSIC LABEL')
        release = music_publisher.models.CommercialRelease(
            release_title='Album', release_label=label)
        release.save()
        self.assertEqual(str(release), 'ALBUM (MUSIC LABEL)')
        self.assertDictEqual(release.get_dict(), {
            'code': 'RE000001',
            'release_title': 'Album',
            'ean': None,
            'release_date': None,
            'release_label': {
                'code': 'LA000001',
                'name': 'Music Label'}})

    def test_writer(self):
        writer = music_publisher.models.Writer(
            first_name='Matija', last_name='Kolarić')
        with self.assertRaises(exceptions.ValidationError):
            writer.clean_fields()
        writer = music_publisher.models.Writer(
            first_name='Matija', last_name='Kolaric', ipi_name='199',
            pr_society='10')
        self.assertIsNone(writer.clean_fields())
        writer.save()
        self.assertEqual(str(writer), 'MATIJA KOLARIC')
        self.assertDictEqual(writer.get_dict(), {
            'code': 'W000001',
            'first_name': 'Matija',
            'last_name': 'Kolaric',
            'ipi_name': '00000000199',
            'ipi_base': None,
            'affiliations': [{
                'affiliation_type': {
                    'code': 'PR',
                    'name': 'Performance Rights'},
                'organization': {
                    'code': '10',
                    'name': 'ASCAP'},
                'territory': {
                    'code': '2136',
                    'name': 'World',
                    'tis_code': '2136'}}]})

ACK_CONTENT = """HDRSO000000021BMI                                          01.102018060715153220180607
GRHACK0000102.100020180607
ACK0000000000000000201805160910510000100000000NWRONE                                                         00000000000001      123                 20180607RA
ACK0000000100000000201805160910510000100000001NWRTWO                                                         00000000000002                          20180607AS
ACK0000000200000000201805160910510000100000002NWRTHREE                                                       00000000000003                          20180607AS
ACK0000000300000000201805160910510000100000003NWRTHREE                                                       00000000000004                          20180607NP
ACK0000000400000000201805160910510000100000004NWRX                                                           0000000000000X                          20180607NP
TRL000010000008000000839"""


# class AllTest(TestCase):
#     """All Tests in a single class.
#     """
#
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
#     def get(self, path, re_post=None):
#         """A helper method that similates opening of view and then simulates
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
#     def test_0_admin_login(self):
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
#         writer = Writer.objects.all().first()
#         self.assertFalse(writer._can_be_controlled)
#         response = self.get(
#             reverse('admin:music_publisher_writer_change', args=(
#                 writer.id,)),
#             re_post={
#                 'pr_society': '52'
#             })
#         self.assertEqual(response.status_code, 302)
#         writer = Writer.objects.all().first()
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
#         writer2 = Writer.objects.filter(pr_society='10').first()
#         response = self.get(
#             reverse('admin:music_publisher_writer_add'),
#             re_post={
#                 'last_name': 'THIRD',
#                 'ipi_name': '395',
#                 'pr_society': '10',
#             })
#         self.assertEqual(response.status_code, 302)
#         writer3 = Writer.objects.filter(last_name='THIRD').first()
#         response = self.get(
#             reverse('admin:music_publisher_writer_add'),
#             re_post={
#                 'last_name': 'OTHER',
#             })
#         self.assertEqual(response.status_code, 302)
#         writer4 = Writer.objects.filter(last_name='OTHER').first()
#         response = self.get(
#             reverse('admin:music_publisher_writer_changelist'))
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
#         release = CommercialRelease.objects.all().first()
#         self.assertEqual(str(release), 'VERY COOL')
#         response = self.get(
#             reverse('admin:music_publisher_commercialrelease_change', args=(
#                 release.id,)),
#             re_post={
#                 'release_date': '2018-01-01',
#                 'ean': '4006381333931',
#             })
#         self.assertEqual(response.status_code, 302)
#         release = CommercialRelease.objects.all().first()
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
#         self.assertEqual(response.status_code, 302)
#         artist = Artist.objects.all().first()
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
#                 'recordings-TOTAL_FORMS': 1,
#                 'recordings-0-artist': artist.id,
#                 'recordings-0-isrc': 'USX1X1234567',
#                 'recordings-0-duration': '01:23',
#                 'recordings-0-release_date': '2018-01-31',
#             })
#         self.assertEqual(response.status_code, 302)
#         work = Work.objects.all().first()
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
#             })
#         self.assertEqual(response.status_code, 302)
#         work2 = Work.objects.filter(title='MODIFICATION').first()
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
#         # response = self.get(
#         #     reverse('admin:music_publisher_cwrexport_add'),
#         #     re_post={'nwr_rev': 'NWR', 'works': [work.id, work2.id]})
#         # settings.MUSIC_PUBLISHER_SETTINGS['work_id_prefix'] = PREFIX
#         # cwr_export = CWRExport.objects.all().first()
#         # self.assertEqual(cwr_export.cwr[86:], CWR_CONTENT[86:])
#         # response = self.get(
#         #     reverse('admin:music_publisher_cwrexport_add'),
#         #     re_post={'nwr_rev': 'REV', 'works': [work.id, work2.id]})
#         # response = self.get(
#         #     reverse(
#         #         'admin:music_publisher_cwrexport_change',
#         #         args=(cwr_export.id,)),
#         #     re_post={'nwr_rev': 'NWR', 'works': [work.id, work2.id]})
#         # response = self.get(
#         #     '{}?download=1'.format(
#         #         reverse(
#         #             'admin:music_publisher_work_change',
#         #             args=(cwr_export.id,))))
#         # self.assertEqual(response.status_code, 200)
#         # response = self.client.post(
#         #     reverse('admin:music_publisher_work_changelist'),
#         #     data={
#         #         'action': 'create_cwr', 'select_across': 1,
#         #         'index': 0, '_selected_action': work.id})
#         # response = self.get(
#         #     reverse('admin:music_publisher_cwrexport_changelist'))
#         # self.assertEqual(response.status_code, 200)
#         # response = self.get(reverse(
#         #     'admin:music_publisher_cwrexport_change', args=(cwr_export.id,)))
#         # self.assertEqual(response.status_code, 200)
#         # response = self.client.get(reverse(
#         #     'admin:music_publisher_cwrexport_change',
#         #     args=(cwr_export.id,)) + '?download=true',)
#         # self.assertEqual(response.status_code, 200)
#         # response = self.client.get(reverse(
#         #     'admin:music_publisher_cwrexport_change',
#         #     args=(cwr_export.id,)) + '?preview=true',)
#         # self.assertEqual(response.status_code, 200)
#
#         # response = self.get(
#         #     reverse('admin:music_publisher_work_changelist',) +
#         #     '?has_iswc=N&has_rec=Y&in_cwr=Y')
#         # self.assertEqual(response.status_code, 200)
#         # self.get(
#         #     reverse('admin:music_publisher_work_changelist',) +
#         #     '?has_iswc=Y&has_rec=N&in_cwr=N&q=01')
#         # self.get(
#         #     reverse('admin:music_publisher_work_changelist',) +
#         #     '?ack_society=021')
#         # self.assertEqual(response.status_code, 200)
#         # response = self.get(
#         #     reverse('admin:music_publisher_artist_add') + '?_popup=1')
#         # self.assertEqual(response.status_code, 200)
#         # response = self.get(
#         #     reverse('admin:music_publisher_release_add') + '?_popup=1')
#         # self.assertEqual(response.status_code, 200)
#         # response = self.get(
#         #     reverse('admin:music_publisher_work_add') + '?_popup=1')
#         # self.assertEqual(response.status_code, 200)
#         # mock = StringIO()
#         # mock.write(ACK_CONTENT)
#         # mock.seek(0)
#         # mockfile = InMemoryUploadedFile(
#         #     mock, 'acknowledgement_file', 'CW180001000_FOO.V21',
#         #     'text', 0, None)
#         # response = self.get(
#         #     reverse('admin:music_publisher_ackimport_add'),
#         #     re_post={'acknowledgement_file': mockfile})
#         # self.assertEqual(response.status_code, 302)
#         # ackimport = ACKImport.objects.first()
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
#         # # Removing needed data from controlled writer
#         # response = self.get(
#         #     reverse('admin:music_publisher_writer_change', args=(
#         #         writer.id,)),
#         #     re_post={
#         #         'pr_society': ''
#         #     })
#         # self.assertEqual(response.status_code, 200)
#         # self.assertIn('controlled in at least', response.content.decode())
#         # response = self.get(
#         #     reverse('admin:music_publisher_work_change', args=(work.id,)),
#         #     re_post={
#         #         'title': 'GOOD TITLE',
#         #         'iswc': 'T1234567894',
#         #         'alternatetitle_set-TOTAL_FORMS': 1,
#         #         'alternatetitle_set-0-title': 'BETTER TITLE',
#         #         'writerinwork_set-TOTAL_FORMS': 2,
#         #         'writerinwork_set-0-writer': '',
#         #         'writerinwork_set-0-capacity': 'CA',
#         #         'writerinwork_set-0-relative_share': '50',
#         #         'writerinwork_set-0-controlled': '1',
#         #         'writerinwork_set-0-saan': '1LJ4V4',
#         #         'writerinwork_set-0-publisher_fee': '25',
#         #         'writerinwork_set-1-writer': writer4.id,
#         #         'writerinwork_set-1-capacity': 'CA',
#         #         'writerinwork_set-1-relative_share': '50',
#         #         'writerinwork_set-1-controlled': '1',
#         #         'recordings-TOTAL_FORMS': 1,
#         #         'recordings-0-artist': artist.id,
#         #         'recordings-0-isrc': 'USX1X1234567',
#         #         'recordings-0-duration': '01:23',
#         #         'recordings-0-release_date': '2018-01-31',
#         #     })
#         # self.assertEqual(response.status_code, 200)
#         # self.assertIn('Must be set for', response.content.decode())
#         # response = self.get(
#         #     reverse('admin:music_publisher_work_change', args=(work.id,)),
#         #     re_post={
#         #         'title': 'GOOD TITLE',
#         #         'iswc': 'T1234567894',
#         #         'alternatetitle_set-TOTAL_FORMS': 1,
#         #         'alternatetitle_set-0-title': 'BETTER TITLE',
#         #         'writerinwork_set-TOTAL_FORMS': 3,
#         #         'writerinwork_set-0-writer': writer.id,
#         #         'writerinwork_set-0-capacity': 'CA',
#         #         'writerinwork_set-0-relative_share': '50',
#         #         'writerinwork_set-0-controlled': '1',
#         #         'writerinwork_set-0-saan': '1LJ4V4',
#         #         'writerinwork_set-0-publisher_fee': '25',
#         #         'writerinwork_set-1-writer': writer2.id,
#         #         'writerinwork_set-1-capacity': 'CA',
#         #         'writerinwork_set-1-relative_share': '25',
#         #         'writerinwork_set-1-controlled': '',
#         #         'writerinwork_set-2-writer': writer4.id,
#         #         'writerinwork_set-2-saan': '1LJ4V4',
#         #         'writerinwork_set-2-publisher_fee': '25',
#         #         'recordings-TOTAL_FORMS': 1,
#         #         'recordings-0-artist': artist.id,
#         #         'recordings-0-isrc': 'USX1X1234567',
#         #         'recordings-0-duration': '01:23',
#         #         'recordings-0-release_date': '2018-01-31',
#         #     })
#         # self.assertEqual(response.status_code, 200)
#         # self.assertIn('Must be set for', response.content.decode())
#         # # JSON must be at the end, so the export is complete
#         # response = self.client.post(
#         #     reverse('admin:music_publisher_work_changelist'),
#         #     data={
#         #         'action': 'create_json', 'select_across': 1,
#         #         'index': 0, '_selected_action': work.id})
#         # self.assertEqual(str(WorkAcknowledgement.objects.first()), 'RA')
#         # # Moved to the end, after the ACK file has been imported
#         # self.get(
#         #     reverse('admin:music_publisher_work_changelist',) +
#         #     '?ack_society=21&ack_status=AS')
#
#     def test_3_works(self):
#         self.client.force_login(self.user)
#         response = self.get(reverse('admin:music_publisher_work_changelist',))
#         self.assertEqual(response.status_code, 200)
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
#         writer = Writer.objects.all().first()
#         self.assertFalse(writer._can_be_controlled)
#         response = self.get(
#             reverse('admin:music_publisher_writer_change', args=(
#                 writer.id,)),
#             re_post={
#                 'pr_society': '52'
#             })
#         self.assertEqual(response.status_code, 302)
#         writer = Writer.objects.all().first()
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
#         writer2 = Writer.objects.filter(pr_society='10').first()
#         response = self.get(
#             reverse('admin:music_publisher_writer_add'),
#             re_post={
#                 'last_name': 'THIRD',
#                 'ipi_name': '395',
#                 'pr_society': '10',
#             })
#         self.assertEqual(response.status_code, 302)
#         writer3 = Writer.objects.filter(last_name='THIRD').first()
#         response = self.get(
#             reverse('admin:music_publisher_writer_add'),
#             re_post={
#                 'last_name': 'OTHER',
#             })
#         self.assertEqual(response.status_code, 302)
#         writer4 = Writer.objects.filter(last_name='OTHER').first()
#         response = self.get(
#             reverse('admin:music_publisher_writer_changelist'))
#         self.assertTrue(writer._can_be_controlled)
#         response = self.get(
#             reverse('admin:music_publisher_commercialrelease_add'),
#             re_post={
#                 'album_title': 'VERY COOL',
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
#         release = CommercialRelease.objects.all().first()
#         self.assertEqual(str(release), 'VERY COOL')
#         response = self.get(
#             reverse('admin:music_publisher_release_change', args=(
#                 release.id,)),
#             re_post={
#                 'release_date': '2018-01-01',
#                 'ean': '4006381333931',
#             })
#         self.assertEqual(response.status_code, 302)
#         release = CommercialRelease.objects.all().first()
#         response = self.get(
#             reverse('admin:music_publisher_release_changelist'))
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
#         self.assertEqual(response.status_code, 302)
#         artist = Artist.objects.all().first()
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
#                 'recordings-TOTAL_FORMS': 1,
#                 'recordings-0-artist': artist.id,
#                 'recordings-0-isrc': 'USX1X1234567',
#                 'recordings-0-duration': '01:23',
#                 'recordings-0-release_date': '2018-01-31',
#             })
#         self.assertEqual(response.status_code, 302)
#         # work = Work.objects.all().first()
#         # response = self.get(
#         #     reverse('admin:music_publisher_cwrexport_add'),
#         #     re_post={'nwr_rev': 'NWR', 'works': [work.id]})
#         # response = self.client.post(
#         #     reverse('admin:music_publisher_work_changelist'),
#         #     data={
#         #         'action': 'create_normalized_json', 'select_across': 1,
#         #         'index': 0, '_selected_action': work.id})
#
# PATH = os.path.join(
#     os.path.dirname(__file__), 'cwrexample.txt')
# CWR_CONTENT = open(PATH, 'rb').read().decode()
