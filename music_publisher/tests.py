"""Tests for :mod:`music_publisher`.

Tests are the weakest link in the package. They do test that things do not break, which makes a grat difference, but they do not test how things work.

A major re-write is required.

Attributes:
    CONTENT (str): CWR ACK file contents
"""

from django.contrib.auth.models import User
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from music_publisher.admin import *
from music_publisher.models import *
from io import StringIO


class AllTest(TestCase):
    """All Tests in a sibgle class.
    """

    fixtures = ['publishing_staff.json']

    def setUp(self):
        """Set up the initial data.
        """

        self.user = User(
            username='user', is_superuser=False, is_staff=True)
        self.user.set_password('password')
        self.user.save()
        self.user.groups.add(1)

    def get(self, path, re_post=False):
        """A helper method that similates opening of view and then simulates
            manual changes and save.
        """
        response = self.client.get(path)
        if response.status_code != 200:
            return response
        adminform = response.context_data.get('adminform')
        if not re_post:
            return response
        data = {}
        for sc in response.context:
            for d in sc:
                if 'widget' in sc:
                    if (sc['widget'].get('type') == 'select' and
                            sc['widget']['selected'] is False):
                        continue
                    data[sc['widget']['name']] = sc['widget']['value']
        if adminform:
            data.update(adminform.form.initial)
        if isinstance(re_post, dict):
            data.update(re_post)
        for key, value in data.items():
            if value is None:
                data[key] = ''
            else:
                data[key] = value
        response = self.client.post(path, data)
        return response

    def test_0_admin_login(self):
        """Basic navigation tests."""

        response = self.get(reverse('admin:index'))
        self.assertEqual(response.status_code, 302)
        location = reverse('admin:login') + '?next=' + reverse('admin:index')
        self.assertEqual(
            response._headers.get('location'), (
                'Location',
                location))
        response = self.get(location, re_post={
            'username': 'user', 'password': 'wrongpassword'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('errornote', response.content.decode())
        response = self.get(location, re_post={
            'username': 'user', 'password': 'password'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response._headers.get('location'), (
                'Location',
                reverse('admin:index')))

    def test_1_indices(self):
        self.client.force_login(self.user)
        response = self.get(reverse('admin:index'))
        self.assertEqual(response.status_code, 200)
        response = self.get(
            reverse('admin:app_list', args=('music_publisher',)))
        self.assertEqual(response.status_code, 200)

    @override_settings()
    def test_2_works(self):
        self.client.force_login(self.user)
        response = self.get(reverse('admin:music_publisher_work_changelist',))
        self.assertEqual(response.status_code, 200)
        response = self.get(
            reverse('admin:music_publisher_writer_add'),
            re_post={
                'last_name': 'Lošija',
                'ipi_name': 'X',
                'ipi_base': '1000000000'
            })
        self.assertEqual(response.status_code, 200)
        self.assertIn('Name contains invalid', response.content.decode())
        self.assertIn('Value must be numeric.', response.content.decode())
        self.assertIn('I-NNNNNNNNN-C format', response.content.decode())
        response = self.get(
            reverse('admin:music_publisher_writer_add'),
            re_post={
                'first_name': 'VERY',
                'last_name': 'COOL',
                'ipi_name': '100',
                'ipi_base': 'I-123456789-0'
            })
        self.assertEqual(response.status_code, 200)
        self.assertIn('Not a valid IPI name', response.content.decode())
        self.assertIn('Not valid:', response.content.decode())
        response = self.get(
            reverse('admin:music_publisher_writer_add'),
            re_post={
                'first_name': 'VERY',
                'last_name': 'COOL',
                'ipi_name': '199',
                'ipi_base': 'I-123456789-3'
            })
        self.assertEqual(response.status_code, 302)
        writer = Writer.objects.all().first()
        self.assertFalse(writer._can_be_controlled)
        response = self.get(
            reverse('admin:music_publisher_writer_change', args=(
                writer.id,)),
            re_post={
                'pr_society': '052'
            })
        self.assertEqual(response.status_code, 302)
        writer = Writer.objects.all().first()
        response = self.get(
            reverse('admin:music_publisher_writer_add'),
            re_post={
                'first_name': 'YANKEE',
                'last_name': 'DOODLE',
                'generally_controlled': 1,
            })
        self.assertEqual(response.status_code, 200)
        self.assertIn('Unsufficient data for a', response.content.decode())
        self.assertIn('This field is required.', response.content.decode())
        response = self.get(
            reverse('admin:music_publisher_writer_add'),
            re_post={
                'first_name': 'YANKEE',
                'last_name': 'DOODLE',
                'ipi_name': '297',
                'pr_society': '010',
                'saan': 'DREAM',
                'publisher_fee': '100'
            })
        self.assertEqual(response.status_code, 200)
        self.assertIn('Only for a general agreemen', response.content.decode())
        response = self.get(
            reverse('admin:music_publisher_writer_add'),
            re_post={
                'first_name': 'YANKEE',
                'last_name': 'DOODLE',
                'ipi_name': '297',
                'pr_society': '010',
                'generally_controlled': 1,
                'saan': 'DREAM',
                'publisher_fee': '100'
            })
        self.assertEqual(response.status_code, 302)
        writer2 = Writer.objects.filter(pr_society='010').first()
        response = self.get(
            reverse('admin:music_publisher_writer_add'),
            re_post={
                'last_name': 'THIRD',
                'ipi_name': '395',
                'pr_society': '010',
            })
        self.assertEqual(response.status_code, 302)
        writer3 = Writer.objects.filter(last_name='THIRD').first()
        response = self.get(
            reverse('admin:music_publisher_writer_add'),
            re_post={
                'last_name': 'OTHER',
            })
        self.assertEqual(response.status_code, 302)
        writer4 = Writer.objects.filter(last_name='OTHER').first()
        response = self.get(
            reverse('admin:music_publisher_writer_changelist'))
        self.assertTrue(writer._can_be_controlled)
        response = self.get(
            reverse('admin:music_publisher_albumcd_add'),
            re_post={
                'album_title': 'VERY COOL',
                'ean': '199',
            })
        self.assertEqual(response.status_code, 200)
        self.assertIn('does not match EAN13 format', response.content.decode())
        response = self.get(
            reverse('admin:music_publisher_albumcd_add'),
            re_post={
                'ean': '1234567890123',
            })
        self.assertEqual(response.status_code, 200)
        self.assertIn('Invalid EAN.', response.content.decode())
        self.assertIn('Required if Album Title ', response.content.decode())
        response = self.get(
            reverse('admin:music_publisher_albumcd_add'),
            re_post={
                'cd_identifier': 'C00L',
                'ean': '1234567890123',
            })
        self.assertEqual(response.status_code, 200)
        self.assertIn('Required if EAN or release ', response.content.decode())
        response = self.get(
            reverse('admin:music_publisher_albumcd_add'),
            re_post={
                'album_title': 'VERY COOL',
            })
        self.assertEqual(response.status_code, 302)
        albumcd = AlbumCD.objects.all().first()
        self.assertEqual(str(albumcd), 'VERY COOL')
        response = self.get(
            reverse('admin:music_publisher_albumcd_change', args=(
                albumcd.id,)),
            re_post={
                'cd_identifier': 'C00L',
                'release_date': '2018-01-01',
                'ean': '4006381333931',
            })
        self.assertEqual(response.status_code, 302)
        albumcd = AlbumCD.objects.all().first()
        response = self.get(
            reverse('admin:music_publisher_albumcd_changelist'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(str(albumcd), 'VERY COOL (C00L)')
        response = self.get(
            reverse('admin:music_publisher_artist_add'),
            re_post={
                'first_name': 'VERY',
                'last_name': 'VERY COOL',
                'isni': '1234567890123',
            })
        self.assertEqual(response.status_code, 200)
        response = self.get(
            reverse('admin:music_publisher_artist_add'),
            re_post={
                'last_name': 'VERY COOL',
                'isni': '12345678SD23',
            })
        self.assertEqual(response.status_code, 200)
        response = self.get(
            reverse('admin:music_publisher_artist_add',),
            re_post={
                'first_name': 'VERY',
                'last_name': 'VERY COOL',
                'isni': '1X',
            })
        self.assertEqual(response.status_code, 302)
        artist = Artist.objects.all().first()
        response = self.get(
            reverse('admin:music_publisher_artist_changelist'))
        self.assertEqual(response.status_code, 200)

        response = self.get(
            reverse('admin:music_publisher_work_add'),
            re_post={
                'title': 'LOŠ NASLOV',
                'iswc': 'ADC',
                'writerinwork_set-0-writer': writer.id,
                'writerinwork_set-0-capacity': 'XX',
                'writerinwork_set-0-relative_share': '100',
                'writerinwork_set-0-controlled': '1',
                'writerinwork_set-0-saan': '1LJ4V4',
                'writerinwork_set-0-publisher_fee': '25',
            })
        self.assertEqual(response.status_code, 200)
        self.assertIn('Title contains invalid', response.content.decode())
        self.assertIn('match TNNNNNNNNNC', response.content.decode())
        response = self.get(
            reverse('admin:music_publisher_work_add'),
            re_post={
                'title': 'GOOD TITLE',
                'iswc': 'T1234567893',
                'writerinwork_set-0-writer': writer.id,
                'writerinwork_set-0-capacity': 'CA',
                'writerinwork_set-0-relative_share': '50',
                'writerinwork_set-0-controlled': '',
                'writerinwork_set-0-saan': '',
                'writerinwork_set-0-publisher_fee': '',
                'writerinwork_set-1-writer': writer.id,
                'writerinwork_set-1-capacity': 'CA',
                'writerinwork_set-1-relative_share': '50',
                'writerinwork_set-1-controlled': '',
                'writerinwork_set-1-saan': '',
                'writerinwork_set-1-publisher_fee': '',
                'firstrecording-TOTAL_FORMS': 1,
                'firstrecording-0-album_cd': albumcd.id,
                'firstrecording-0-isrc': 'USX1X12345',
            })
        self.assertEqual(response.status_code, 200)
        self.assertIn('must be controlled', response.content.decode())
        self.assertIn('not match ISRC', response.content.decode())
        response = self.get(
            reverse('admin:music_publisher_work_add'),
            re_post={
                'title': 'GOOD TITLE',
                'iswc': 'T1234567894',
                'alternatetitle_set-TOTAL_FORMS': 1,
                'alternatetitle_set-0-title': 'BETTER TITLE',
                'writerinwork_set-TOTAL_FORMS': 5,
                'writerinwork_set-0-writer': writer.id,
                'writerinwork_set-0-capacity': 'CA',
                'writerinwork_set-0-relative_share': '25',
                'writerinwork_set-0-controlled': '1',
                'writerinwork_set-0-saan': '1LJ4V4',
                'writerinwork_set-0-publisher_fee': '25',
                'writerinwork_set-1-writer': writer2.id,
                'writerinwork_set-1-capacity': 'CA',
                'writerinwork_set-1-relative_share': '11.66',
                'writerinwork_set-1-controlled': '1',
                'writerinwork_set-2-writer': writer3.id,
                'writerinwork_set-2-capacity': 'A ',
                'writerinwork_set-2-relative_share': '33.33',
                'writerinwork_set-2-controlled': '1',
                'writerinwork_set-2-saan': '1LJ4V4',
                'writerinwork_set-2-publisher_fee': '25',
                'writerinwork_set-3-writer': writer.id,
                'writerinwork_set-3-capacity': 'CA',
                'writerinwork_set-3-relative_share': '25',
                'writerinwork_set-4-writer': writer3.id,
                'writerinwork_set-4-relative_share': '5',
                'firstrecording-TOTAL_FORMS': 1,
                'firstrecording-0-album_cd': albumcd.id,
                'firstrecording-0-artist': artist.id,
                'firstrecording-0-isrc': 'USX1X1234567',
                'firstrecording-0-duration': '01:23',
                'firstrecording-0-release_date': '2018-01-31',
            })
        self.assertEqual(response.status_code, 302)
        work = Work.objects.all().first()
        settings.MUSIC_PUBLISHER_SETTINGS['allow_multiple_ops'] = False
        response = self.get(
            reverse('admin:music_publisher_work_add'),
            re_post={
                'title': 'ANOTHER TITLE',
                'writerinwork_set-TOTAL_FORMS': 2,
                'writerinwork_set-0-writer': writer.id,
                'writerinwork_set-0-capacity': 'CA',
                'writerinwork_set-0-relative_share': '50',
                'writerinwork_set-0-controlled': '1',
                'writerinwork_set-0-saan': '1LJ4V4',
                'writerinwork_set-0-publisher_fee': '25',
                'writerinwork_set-1-writer': writer.id,
                'writerinwork_set-1-capacity': 'CA',
                'writerinwork_set-1-relative_share': '50',
            })
        self.assertEqual(response.status_code, 200)
        settings.MUSIC_PUBLISHER_SETTINGS['allow_multiple_ops'] = True
        response = self.get(
            reverse('admin:music_publisher_work_add'),
            re_post={
                'title': 'ANOTHER TITLE',
                'writerinwork_set-TOTAL_FORMS': 4,
                'writerinwork_set-0-writer': writer.id,
                'writerinwork_set-0-capacity': 'CA',
                'writerinwork_set-0-relative_share': '25',
                'writerinwork_set-0-controlled': '1',
                'writerinwork_set-0-saan': '1LJ4V4',
                'writerinwork_set-0-publisher_fee': '25',
                'writerinwork_set-1-writer': writer.id,
                'writerinwork_set-1-capacity': 'CA',
                'writerinwork_set-1-relative_share': '25',
                'writerinwork_set-2-writer': writer3.id,
                'writerinwork_set-2-relative_share': '25',
                'writerinwork_set-3-relative_share': '25',
                'artistinwork_set-TOTAL_FORMS': 1,
                'artistinwork_set-0-artist': artist.id,
            })
        self.assertEqual(response.status_code, 302)
        work2 = Work.objects.filter(title='ANOTHER TITLE').first()
        response = self.get(
            reverse('admin:music_publisher_work_add'),
            re_post={
                'title': 'MODIFICATION1',
                'original_title': 'ORIGINAL',
                'writerinwork_set-TOTAL_FORMS': 4,
                'writerinwork_set-0-writer': writer.id,
                'writerinwork_set-0-capacity': 'CA',
                'writerinwork_set-0-relative_share': '25',
                'writerinwork_set-0-controlled': '1',
                'writerinwork_set-0-saan': '1LJ4V4',
                'writerinwork_set-0-publisher_fee': '25',
                'writerinwork_set-1-writer': writer.id,
                'writerinwork_set-1-capacity': 'CA',
                'writerinwork_set-1-relative_share': '25',
                'writerinwork_set-2-writer': writer3.id,
                'writerinwork_set-2-relative_share': '25',
                'writerinwork_set-3-relative_share': '25',
                'artistinwork_set-TOTAL_FORMS': 1,
                'artistinwork_set-0-artist': artist.id,
            })
        self.assertEqual(response.status_code, 200)
        self.assertIn('one writer must be Arranger', response.content.decode())
        response = self.get(
            reverse('admin:music_publisher_work_add'),
            re_post={
                'title': 'MODIFICATION2',
                'original_title': 'ORIGINAL',
                'writerinwork_set-TOTAL_FORMS': 4,
                'writerinwork_set-0-writer': writer.id,
                'writerinwork_set-0-capacity': 'CA',
                'writerinwork_set-0-relative_share': '25',
                'writerinwork_set-0-controlled': '1',
                'writerinwork_set-0-saan': '1LJ4V4',
                'writerinwork_set-0-publisher_fee': '25',
                'writerinwork_set-1-writer': writer.id,
                'writerinwork_set-1-capacity': 'AR',
                'writerinwork_set-1-relative_share': '25',
                'writerinwork_set-2-writer': writer3.id,
                'writerinwork_set-2-relative_share': '25',
                'writerinwork_set-3-relative_share': '25',
                'artistinwork_set-TOTAL_FORMS': 1,
                'artistinwork_set-0-artist': artist.id,
            })
        self.assertEqual(response.status_code, 200)
        self.assertIn('same as in controlled', response.content.decode())
        response = self.get(
            reverse('admin:music_publisher_work_add'),
            re_post={
                'title': 'MODIFICATION',
                'original_title': 'ORIGINAL',
                'writerinwork_set-TOTAL_FORMS': 4,
                'writerinwork_set-0-writer': writer.id,
                'writerinwork_set-0-capacity': 'AR',
                'writerinwork_set-0-relative_share': '25',
                'writerinwork_set-0-controlled': '1',
                'writerinwork_set-0-saan': '1LJ4V4',
                'writerinwork_set-0-publisher_fee': '25',
                'writerinwork_set-1-writer': writer.id,
                'writerinwork_set-1-capacity': 'AR',
                'writerinwork_set-1-relative_share': '25',
                'writerinwork_set-2-writer': writer3.id,
                'writerinwork_set-2-relative_share': '25',
                'writerinwork_set-2-capacity': 'CA',
                'writerinwork_set-3-relative_share': '25',
                'artistinwork_set-TOTAL_FORMS': 1,
                'artistinwork_set-0-artist': artist.id,
            })
        self.assertEqual(response.status_code, 302)
        work3 = Work.objects.filter(title='MODIFICATION').first()
        response = self.get(
            reverse('admin:music_publisher_work_add'),
            re_post={
                'title': 'NO COMPOSER TITLE',
                'writerinwork_set-0-writer': writer.id,
                'writerinwork_set-0-capacity': 'A ',
                'writerinwork_set-0-relative_share': '100',
                'writerinwork_set-0-controlled': '1',
                'writerinwork_set-0-saan': '1LJ4V4',
                'writerinwork_set-0-publisher_fee': '25',
            })
        self.assertEqual(response.status_code, 200)
        response = self.get(
            reverse('admin:music_publisher_work_add'),
            re_post={
                'title': 'OVER 100 PERCENT',
                'writerinwork_set-0-writer': writer.id,
                'writerinwork_set-0-capacity': 'CA',
                'writerinwork_set-0-relative_share': '101',
                'writerinwork_set-0-controlled': '1',
                'writerinwork_set-0-saan': '1LJ4V4',
                'writerinwork_set-0-publisher_fee': '25',
            })
        self.assertEqual(response.status_code, 200)
        response = self.get(
            reverse('admin:music_publisher_work_add'),
            re_post={
                'title': 'ORIGINAL WITH AN ARRANGER',
                'writerinwork_set-TOTAL_FORMS': 2,
                'writerinwork_set-0-writer': writer.id,
                'writerinwork_set-0-capacity': 'CA',
                'writerinwork_set-0-relative_share': '0',
                'writerinwork_set-1-writer': writer2.id,
                'writerinwork_set-1-capacity': 'AR',
                'writerinwork_set-1-relative_share': '100',
                'writerinwork_set-1-controlled': '1',
            })
        self.assertEqual(response.status_code, 200)
        self.assertIn('Not allowed in original', response.content.decode())
        response = self.get(
            reverse('admin:music_publisher_work_changelist'))
        response = self.get(
            reverse('admin:music_publisher_work_change', args=(work.id,)))
        response = self.get(
            reverse('admin:music_publisher_cwrexport_add'),
            re_post={'nwr_rev': 'NWR', 'works': [work.id, work2.id, work3.id]})
        cwr_export = CWRExport.objects.all().first()
        self.assertEqual(cwr_export.cwr[86:], CWR_CONTENT[86:])
        response = self.get(
            reverse('admin:music_publisher_cwrexport_add'),
            re_post={'nwr_rev': 'REV', 'works': [work.id, work2.id]})
        response = self.get(
            reverse(
                'admin:music_publisher_cwrexport_change',
                args=(cwr_export.id,)),
            re_post={'nwr_rev': 'NWR', 'works': [work.id, work2.id]})
        response = self.get(
            '{}?download=1'.format(
                reverse(
                    'admin:music_publisher_work_change',
                    args=(cwr_export.id,))))
        self.assertEqual(response.status_code, 200)
        response = self.client.post(
            reverse('admin:music_publisher_work_changelist'),
            data={
                'action': 'create_cwr', 'select_across': 1,
                'index': 0, '_selected_action': work.id})
        response = self.get(
            reverse('admin:music_publisher_cwrexport_changelist'))
        self.assertEqual(response.status_code, 200)
        response = self.get(reverse(
            'admin:music_publisher_cwrexport_change', args=(cwr_export.id,)))
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse(
            'admin:music_publisher_cwrexport_change',
            args=(cwr_export.id,)) + '?download=true',)
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse(
            'admin:music_publisher_cwrexport_change',
            args=(cwr_export.id,)) + '?preview=true',)
        self.assertEqual(response.status_code, 200)

        response = self.get(
            reverse('admin:music_publisher_work_changelist',) +
            '?has_iswc=N&has_rec=Y')
        self.assertEqual(response.status_code, 200)
        self.get(
            reverse('admin:music_publisher_work_changelist',) +
            '?has_iswc=Y&has_rec=N&q=01')
        self.assertEqual(response.status_code, 200)
        response = self.get(
            reverse('admin:music_publisher_artist_add') + '?_popup=1')
        self.assertEqual(response.status_code, 200)
        response = self.get(
            reverse('admin:music_publisher_albumcd_add') + '?_popup=1')
        self.assertEqual(response.status_code, 200)
        response = self.get(
            reverse('admin:music_publisher_work_add') + '?_popup=1')
        self.assertEqual(response.status_code, 200)
        mock = StringIO()
        mock.write(ACK_CONTENT)
        mock.seek(0)
        mockfile = InMemoryUploadedFile(
            mock, 'acknowledgement_file', 'CW180001000_FOO.V21',
            'text', 0, None)
        response = self.get(
            reverse('admin:music_publisher_ackimport_add'),
            re_post={'acknowledgement_file': mockfile})
        self.assertEqual(response.status_code, 302)
        ackimport = ACKImport.objects.first()
        # open and repost
        mock.seek(0)
        mockfile = InMemoryUploadedFile(
            mock, 'acknowledgement_file', 'CW180001000_FOO.V21',
            'text', 0, None)
        response = self.get(reverse(
            'admin:music_publisher_ackimport_change', args=(ackimport.id,)),
            re_post={'acknowledgement_file': mockfile})
        self.assertEqual(response.status_code, 302)
        # second pass, same thing
        mock.seek(0)
        mockfile = InMemoryUploadedFile(
            mock, 'acknowledgement_file', 'CW180001000_FOO.V21',
            'text', 0, None)
        response = self.get(
            reverse('admin:music_publisher_ackimport_add'),
            re_post={'acknowledgement_file': mockfile})
        self.assertEqual(response.status_code, 302)
        # incorrect filename
        mock.seek(0)
        mockfile = InMemoryUploadedFile(
            mock, 'acknowledgement_file', 'CW180001000_FOO.V22',
            'text', 0, None)
        response = self.get(
            reverse('admin:music_publisher_ackimport_add'),
            re_post={'acknowledgement_file': mockfile})
        self.assertEqual(response.status_code, 200)
        # incorrect header
        mock.seek(3)
        mockfile = InMemoryUploadedFile(
            mock, 'acknowledgement_file', 'CW180001000_FOO.V21',
            'text', 0, None)
        response = self.get(
            reverse('admin:music_publisher_ackimport_add'),
            re_post={'acknowledgement_file': mockfile})
        self.assertEqual(response.status_code, 200)
        # Removing needed data from controlled writer
        response = self.get(
            reverse('admin:music_publisher_writer_change', args=(
                writer.id,)),
            re_post={
                'pr_society': ''
            })
        self.assertEqual(response.status_code, 200)
        self.assertIn('controlled in at least', response.content.decode())
        response = self.get(
            reverse('admin:music_publisher_work_change', args=(work.id,)),
            re_post={
                'title': 'GOOD TITLE',
                'iswc': 'T1234567894',
                'alternatetitle_set-TOTAL_FORMS': 1,
                'alternatetitle_set-0-title': 'BETTER TITLE',
                'writerinwork_set-TOTAL_FORMS': 2,
                'writerinwork_set-0-writer': '',
                'writerinwork_set-0-capacity': 'CA',
                'writerinwork_set-0-relative_share': '50',
                'writerinwork_set-0-controlled': '1',
                'writerinwork_set-0-saan': '1LJ4V4',
                'writerinwork_set-0-publisher_fee': '25',
                'writerinwork_set-1-writer': writer4.id,
                'writerinwork_set-1-capacity': 'CA',
                'writerinwork_set-1-relative_share': '50',
                'writerinwork_set-1-controlled': '1',
                'firstrecording-TOTAL_FORMS': 1,
                'firstrecording-0-album_cd': albumcd.id,
                'firstrecording-0-artist': artist.id,
                'firstrecording-0-isrc': 'USX1X1234567',
                'firstrecording-0-duration': '01:23',
                'firstrecording-0-release_date': '2018-01-31',
            })
        self.assertEqual(response.status_code, 200)
        self.assertIn('Must be set for', response.content.decode())
        response = self.get(
            reverse('admin:music_publisher_work_change', args=(work.id,)),
            re_post={
                'title': 'GOOD TITLE',
                'iswc': 'T1234567894',
                'alternatetitle_set-TOTAL_FORMS': 1,
                'alternatetitle_set-0-title': 'BETTER TITLE',
                'writerinwork_set-TOTAL_FORMS': 3,
                'writerinwork_set-0-writer': writer.id,
                'writerinwork_set-0-capacity': 'CA',
                'writerinwork_set-0-relative_share': '50',
                'writerinwork_set-0-controlled': '1',
                'writerinwork_set-0-saan': '1LJ4V4',
                'writerinwork_set-0-publisher_fee': '25',
                'writerinwork_set-1-writer': writer2.id,
                'writerinwork_set-1-capacity': 'CA',
                'writerinwork_set-1-relative_share': '25',
                'writerinwork_set-1-controlled': '',
                'writerinwork_set-2-writer': writer4.id,
                'writerinwork_set-2-saan': '1LJ4V4',
                'writerinwork_set-2-publisher_fee': '25',
                'firstrecording-TOTAL_FORMS': 1,
                'firstrecording-0-album_cd': albumcd.id,
                'firstrecording-0-artist': artist.id,
                'firstrecording-0-isrc': 'USX1X1234567',
                'firstrecording-0-duration': '01:23',
                'firstrecording-0-release_date': '2018-01-31',
            })
        self.assertEqual(response.status_code, 200)
        self.assertIn('Must be set for', response.content.decode())
        # JSON must be at the end, so the export is complete
        response = self.client.post(
            reverse('admin:music_publisher_work_changelist'),
            data={
                'action': 'create_normalized_json', 'select_across': 1,
                'index': 0, '_selected_action': work.id})
        response = self.client.post(
            reverse('admin:music_publisher_work_changelist'),
            data={
                'action': 'create_json', 'select_across': 1,
                'index': 0, '_selected_action': work.id})
        self.assertEqual(str(WorkAcknowledgement.objects.first()), 'RA')


ACK_CONTENT = """HDRSO000000021BMI                                          01.102018060715153220180607
GRHACK0000102.100020180607
ACK0000000000000000201805160910510000100000000NWRONE                                                         00000000000001      123                 20180607RA
ACK0000000100000000201805160910510000100000001NWRTWO                                                         00000000000002                          20180607AS
ACK0000000200000000201805160910510000100000002NWRTHREE                                                       00000000000003                          20180607AS
ACK0000000300000000201805160910510000100000003NWRTHREE                                                       00000000000004                          20180607NP
ACK0000000400000000201805160910510000100000004NWRX                                                           0000000000000X                          20180607NP
TRL000010000008000000839"""

CWR_CONTENT = open('music_publisher/cwrexample.txt', 'rb').read().decode()