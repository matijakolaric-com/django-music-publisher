"""Tests for :mod:`music_publisher`.

Tests are the weakest link in the package. They do test that things do not break, which makes a grat difference, but they do not test how things work.

A major re-write is required.

Attributes:
    CONTENT (str): CWR ACK file contents
"""

from datetime import date, time
from django.contrib.admin.sites import AdminSite
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.test import TestCase, Client, override_settings
from django.test.client import RequestFactory
from django.urls import reverse
from music_publisher.admin import *
from music_publisher.models import *
from io import StringIO


class AllTest(TestCase):
    """All Tests in a sibgle class.
    """

    def setUp(self):
        """Set up the initial data.
        """
        self.adminsite = AdminSite()
        self.user = User(
            username='superuser', is_superuser=True, is_staff=True)
        self.user.save()
        self.client = Client()
        self.client.force_login(self.user)
        self.factory = RequestFactory()

        self.artist = Artist(last_name="FOO", first_name="")
        self.artist.save()
        self.recordingartist = Artist(last_name="BAR", first_name="BARBARA")
        self.recordingartist.save()z
        self.thiswriter = Writer(
            last_name='FOOBAR', first_name='JACK', ipi_name='199',
            ipi_base='I1234567893', pr_society='010')
        self.thiswriter.full_clean()
        self.thiswriter.save()
        self.thatwriter = Writer(
            last_name='FOOBAR', first_name='JACK JR.', ipi_name='297',
            pr_society='010', generally_controlled=True, saan='JaVa',
            publisher_fee=50)
        self.thatwriter.full_clean()
        self.thatwriter.save()
        self.otherwriter = Writer(last_name='DOE', first_name='JANE')
        self.otherwriter.full_clean()
        self.otherwriter.save()
        self.album_cd = AlbumCD(
            album_title='ALBUM', cd_identifier='XXX 123',
            release_date=date.today())
        self.album_cd.save()
        self.work = Work(title='THE TITLE', iswc='T-123.456.789-4')
        self.work.save()
        ArtistInWork(artist=self.artist, work=self.work).save()
        WriterInWork(
            writer=self.thiswriter, work=self.work, saan='SAMOSAN',
            publisher_fee='20',
            controlled=True, relative_share=50, capacity='CA').save()
        WriterInWork(
            writer=self.otherwriter, work=self.work, relative_share=50,
            controlled=False).save()
        self.alternate_title = AlternateTitle(
            work=self.work, title='The Alternate Title')
        self.alternate_title.save()
        self.work.firstrecording = FirstRecording(
            work=self.work, isrc='US-123-18-10000', duration=time(minute=1),
            album_cd=self.album_cd, artist=self.recordingartist,
            release_date=date.today())
        self.work.firstrecording.save()
        self.work.full_clean()
        self.work2 = Work(title='Minimal')
        self.work2.save()
        WriterInWork(
            writer=self.thiswriter, work=self.work2, saan='SAMOSAN',
            controlled=True, relative_share=50, capacity='CA').save()
        WriterInWork(
            work=self.work2, controlled=False, relative_share=50).save()
        self.cwr_export = CWRExport()
        self.cwr_export.save()
        self.cwr_export.works.add(self.work)
        self.cwr_export.works.add(self.work2)
        self.cwr_export2 = CWRExport(nwr_rev='REV')
        self.cwr_export2.works.add(self.work)
        self.cwr_export2.save()

    @override_settings()
    def test_validation(self):
        """Test the field-level validation for the initial models.
        """
        self.work.clean_fields()
        get_publisher_dict(None)
        with self.assertRaises(ValidationError) as ve:
            self.artist.first_name = "BAR, JR"
            self.artist.clean_fields()
        self.assertIn('first_name', ve.exception.message_dict)
        self.artist.first_name = "BAR JR"
        self.assertFalse(CWRFieldValidator('x') == CWRFieldValidator('y'))
        self.work.firstrecording.clean_fields()
        self.assertEqual(self.work.firstrecording.isrc, 'US1231810000')
        self.thiswriter.clean_fields()
        self.assertTrue(self.thiswriter._can_be_controlled)
        self.assertFalse(self.otherwriter._can_be_controlled)
        with self.assertRaises(ValidationError) as ve:
            self.otherwriter.saan = 'S4N1LJ4V4'
            self.otherwriter.full_clean()
        self.assertIn('saan', ve.exception.message_dict)
        with self.assertRaises(ValidationError) as ve:
            self.otherwriter.saan = None
            self.otherwriter.generally_controlled = True
            self.otherwriter.full_clean()
        self.assertIn('generally_controlled', ve.exception.message_dict)
        with self.assertRaises(ValidationError) as ve:
            self.thiswriter.saan = 'S4N1LJ4V4'
            self.thiswriter.full_clean()
        self.assertIn('saan', ve.exception.message_dict)
        with self.assertRaises(ValidationError) as ve:
            self.thiswriter.saan = None
            self.thiswriter.publisher_fee = 100
            self.thiswriter.full_clean()
        self.assertIn('publisher_fee', ve.exception.message_dict)
        self.thiswriter.publisher_fee = None
        with self.assertRaises(ValidationError) as ve:
            self.thiswriter.pr_society = None
            self.thiswriter.full_clean()
        with self.assertRaises(ValidationError) as ve:
            self.thatwriter.saan = None
            self.thatwriter.full_clean()
        self.assertIn('saan', ve.exception.message_dict)
        with self.assertRaises(ValidationError) as ve:
            self.thatwriter.saan = 'SANILJAVA'
            self.thatwriter.publisher_fee = None
            self.thatwriter.full_clean()
        self.assertIn('publisher_fee', ve.exception.message_dict)
        wiws = self.work.writerinwork_set.all()
        for wiw in wiws:
            if not wiw.controlled:
                with self.assertRaises(ValidationError) as ve:
                    wiw.writer.generally_controlled = True
                    wiw.full_clean()
                self.assertIn('controlled', ve.exception.message_dict)
                wiw.writer.generally_controlled = False
                with self.assertRaises(ValidationError) as ve:
                    wiw.publisher_fee = 100
                    wiw.full_clean()
                self.assertIn('publisher_fee', ve.exception.message_dict)
                wiw.publisher_fee = None
                with self.assertRaises(ValidationError) as ve:
                    wiw.saan = 'JAVA'
                    wiw.full_clean()
                self.assertIn('saan', ve.exception.message_dict)
                wiw.saan = None
            else:
                with self.assertRaises(ValidationError) as ve:
                    wiw.capacity = None
                    wiw.full_clean()
                self.assertIn('capacity', ve.exception.message_dict)
                wiw.capacity = 'CA'
                with self.assertRaises(ValidationError) as ve:
                    wiw.writer._can_be_controlled = False
                    wiw.full_clean()
                self.assertIn('__all__', ve.exception.message_dict)
                wiw.writer._can_be_controlled = True
                if wiw.writer and not wiw.writer.generally_controlled:
                    with self.assertRaises(ValidationError) as ve:
                        wiw.saan = None
                        wiw.full_clean()
                    self.assertIn('saan', ve.exception.message_dict)
                    with self.assertRaises(ValidationError) as ve:
                        wiw.saan = 'SIJ'
                        wiw.publisher_fee = None
                        wiw.full_clean()
                    self.assertIn('publisher_fee', ve.exception.message_dict)
                with self.assertRaises(ValidationError) as ve:
                    wiw.writer = None
                    wiw.full_clean()
                self.assertIn('writer', ve.exception.message_dict)
        settings.MUSIC_PUBLISHER_SETTINGS['validator_url'] = \
            'https://240.0.0.1/'  # no routing possible to this address
        self.work.full_clean()
        self.work.full_clean()

    def test_str(self):
        """Test that all strings are in CWR_compliant form.
        """
        self.assertEqual(str(self.artist), 'FOO')
        self.artist.first_name = "BAR JR"
        self.assertEqual(str(self.artist), 'BAR JR FOO')
        self.assertEqual(str(self.alternate_title), 'THE ALTERNATE TITLE')
        self.assertEqual(str(self.album_cd), 'ALBUM (XXX 123)')
        self.assertEqual(self.album_cd.album_label, SETTINGS.get('label'))
        self.assertEqual(self.album_cd.library, SETTINGS.get('library'))
        self.album_cd.album_title = None
        self.assertEqual(str(self.album_cd), 'XXX 123')
        with self.assertRaises(ValidationError) as ve:
            self.album_cd.full_clean()
        self.assertIn('album_title', ve.exception.message_dict)
        self.album_cd.cd_identifier = None
        with self.assertRaises(ValidationError) as ve:
            self.album_cd.full_clean()
        self.assertIn('cd_identifier', ve.exception.message_dict)
        self.assertIn('album_title', ve.exception.message_dict)
        self.assertEqual(str(self.thiswriter), 'JACK FOOBAR')
        self.thiswriter.generally_controlled = True
        self.assertEqual(str(self.thiswriter), 'JACK FOOBAR (*)')
        self.assertEqual(str(self.work.firstrecording), str(self.work))
        aiw = self.work.artistinwork_set.first()
        self.assertEqual(str(aiw), 'FOO')
        wiw = self.work.writerinwork_set.first()
        self.assertEqual(str(wiw), str(wiw.writer))

    @override_settings()
    def test_cwr(self):
        """Test external CWR generation.
        """
        self.cwr_export.get_cwr()
        self.assertIn('CW', self.cwr_export.filename)
        self.cwr_export.get_cwr()
        self.cwr_export2.get_cwr()

    def get(self, path, re_post=False):
        """A helper method that similates opening of view and then simulates
            manual changes and save.
        """
        response = self.client.get(path)
        self.assertEqual(response.status_code, 200)
        adminform = response.context_data.get('adminform')
        if adminform is None:
            return
        if not re_post:
            return response
        data = {}
        for sc in response.context:
            for d in sc:
                if 'widget' in sc:
                    data[sc['widget']['name']] = sc['widget']['value']
        data.update(adminform.form.initial)
        if isinstance(re_post, dict):
            data.update(re_post)
        for key, value in data.items():
            if value is None:
                data[key] = ''
            else:
                data[key] = value
        response = self.client.post(path, data)
        self.assertIn(response.status_code, [200, 302])
        return response

    @override_settings()
    def test_admin(self):
        """Integration tests for admin interface.
        """
        self.assertEqual(AlbumCDAdmin.label_not_set(None), 'NOT SET')
        self.cwr_export.get_cwr()
        self.cwr_export2.get_cwr()
        request = self.client.get(
            reverse('admin:music_publisher_ackimport_add',)).wsgi_request
        ACKImportAdmin(
            ACKImport, self.adminsite).process(request, '021', CONTENT)
        self.get(reverse('admin:index'))
        self.get(reverse('admin:app_list', args=('music_publisher',)))
        self.get(reverse('admin:music_publisher_artist_changelist',))
        self.get(reverse('admin:music_publisher_albumcd_changelist',))
        self.get(reverse('admin:music_publisher_writer_changelist',))
        self.get(reverse('admin:music_publisher_work_changelist',))
        self.get(
            reverse('admin:music_publisher_work_changelist',) +
            '?has_iswc=N&has_rec=Y')
        self.get(
            reverse('admin:music_publisher_work_changelist',) +
            '?has_iswc=Y&has_rec=N&q=01')
        self.get(reverse('admin:music_publisher_cwrexport_changelist',))
        self.get(reverse('admin:music_publisher_ackimport_changelist',))
        self.get(reverse('admin:music_publisher_artist_add',) + '?_popup=1')
        self.get(reverse('admin:music_publisher_albumcd_add',) + '?_popup=1')
        self.get(reverse('admin:music_publisher_work_add',) + '?_popup=1')
        self.get(reverse('admin:music_publisher_artist_add',))
        self.get(reverse('admin:music_publisher_albumcd_add',))
        self.get(reverse('admin:music_publisher_writer_add',))
        self.get(reverse('admin:music_publisher_work_add',))
        self.get(reverse('admin:music_publisher_cwrexport_add',))
        self.get(reverse('admin:music_publisher_ackimport_add',))
        self.get(reverse(
            'admin:music_publisher_artist_change', args=(self.artist.id,)),
            re_post={'last_name': 'BAR'})
        self.assertEqual(str(Artist.objects.get(pk=self.artist.id)), 'BAR')
        url = settings.MUSIC_PUBLISHER_SETTINGS['validator_url']
        settings.MUSIC_PUBLISHER_SETTINGS['validator_url'] = \
            'https://240.0.0.1/'  # no routing possiblle
        self.get(reverse(
            'admin:music_publisher_artist_change', args=(self.artist.id,)),
            re_post={'last_name': 'CAFE'})
        settings.MUSIC_PUBLISHER_SETTINGS['validator_url'] = url
        self.get(reverse(
            'admin:music_publisher_albumcd_change', args=(self.album_cd.id,)),
            re_post={'album_title': None, 'release_date': None})
        self.assertEqual(
            str(AlbumCD.objects.get(pk=self.album_cd.id)), 'XXX 123')
        self.get(reverse(
            'admin:music_publisher_writer_change', args=(self.thiswriter.id,)),
            re_post={'pr_society': '021'})
        self.get(reverse(
            'admin:music_publisher_work_change', args=(self.work.id,)),
            re_post={'title': 'CHANGED', 'writerinwork_set-0-controlled': 1})
        self.get(reverse(
            'admin:music_publisher_work_change', args=(self.work.id,)),
            re_post={
                'writerinwork_set-1-relative_share': '111',
                'writerinwork_set-0-controlled': 1})
        self.get(reverse(
            'admin:music_publisher_work_change', args=(self.work.id,)),
            re_post={
                'writerinwork_set-0-relative_share': '50',
                'writerinwork_set-1-relative_share': '50',
                'writerinwork_set-0-controlled': 0,
                'writerinwork_set-1-controlled': 0})
        self.get(reverse(
            'admin:music_publisher_work_change', args=(self.work.id,)),
            re_post={
                'writerinwork_set-1-relative_share': 'BAD DATA'})
        self.get(reverse(
            'admin:music_publisher_albumcd_change', args=(self.album_cd.id,)),
            re_post={'album_title': 'CHANGED', 'library': 'SET'})
        self.client.post(
            reverse('admin:music_publisher_work_changelist'),
            data={
                'action': 'create_cwr', 'select_across': 1,
                'index': 0, '_selected_action': self.work.id})
        self.client.post(
            reverse('admin:music_publisher_work_changelist'),
            data={
                'action': 'create_json', 'select_across': 1,
                'index': 0, '_selected_action': self.work.id})
        self.get(
            reverse(
                'admin:music_publisher_cwrexport_change',
                args=(self.cwr_export.id,)),
            re_post=True)
        self.client.get(reverse(
            'admin:music_publisher_cwrexport_change',
            args=(self.cwr_export.id,)) + '?download=true',)
        self.client.get(reverse(
            'admin:music_publisher_cwrexport_change',
            args=(self.cwr_export.id,)) + '?preview=true',)
        settings.MUSIC_PUBLISHER_SETTINGS['highlighter_url'] = \
            'https://240.0.0.1/'  # no routing possiblle
        self.get(
            reverse('admin:music_publisher_cwrexport_add'),
            re_post={'nwr_rev': 'NWR', 'works': [1]})
        self.get(
            reverse('admin:music_publisher_cwrexport_add'),
            re_post={'nwr_rev': 'WRK', 'works': [1]})
        for export in CWRExport.objects.order_by('-id')[0:2]:
            self.client.get(reverse(
                'admin:music_publisher_cwrexport_change',
                args=(export.id,)) + '?preview=true',)
        mock = StringIO()
        mock.write(CONTENT)
        mock.seek(0)
        mockfile = InMemoryUploadedFile(
            mock, 'acknowledgement_file', 'CW180001000_FOO.V21',
            'text', 0, None)
        self.get(
            reverse('admin:music_publisher_ackimport_add'),
            re_post={'acknowledgement_file': mockfile})
        mock.seek(3)
        mockfile = InMemoryUploadedFile(
            mock, 'acknowledgement_file', 'CW180001000_FOO.V21',
            'text', 0, None)
        self.get(
            reverse('admin:music_publisher_ackimport_add'),
            re_post={'acknowledgement_file': mockfile})
        mock.seek(3)
        mockfile = InMemoryUploadedFile(
            mock, 'acknowledgement_file', 'CW180001000_FOO.V21',
            'text', 0, None)
        self.get(
            reverse('admin:music_publisher_ackimport_add'),
            re_post={'acknowledgement_file': mockfile})
        mock.seek(0)
        mockfile = InMemoryUploadedFile(
            mock, 'acknowledgement_file', 'CW180001000_FOOL.V21',
            'text', 0, None)
        self.get(
            reverse('admin:music_publisher_ackimport_add'),
            re_post={'acknowledgement_file': mockfile})
        self.get(
            reverse(
                'admin:music_publisher_ackimport_change',
                args=(1,)),
            re_post=True)


CONTENT = """HDRSO000000021BMI                                          01.102018060715153220180607
GRHACK0000102.100020180607
ACK0000000000000000201805160910510000100000000NWRONE                                                         00000000000001                          20180607AS
ACK0000000100000000201805160910510000100000001NWRTWO                                                         00000000000002                          20180607AS
ACK0000000200000000201805160910510000100000002NWRTHREE                                                       00000000000003                          20180607NP
ACK0000000300000000201805160910510000100000003NWRX                                                           0000000000000X                          20180607NP
TRL000010000008000000839"""