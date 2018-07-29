from collections import OrderedDict
from datetime import date, time
from django.contrib.admin.sites import AdminSite
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase, Client
from django.test.client import RequestFactory
from django.urls import reverse
from music_publisher.admin import *
from music_publisher.models import *
import json


class ModelsTest(TestCase):
    def setUp(self):
        self.adminsite = AdminSite()
        self.user = User(
            username='superuser', is_superuser=True, is_staff=True)
        self.user.save()
        self.client = Client()
        self.client.force_login(self.user)
        self.factory = RequestFactory()

        self.artist = Artist(last_name="FOO", first_name="")
        self.artist.save()
        self.thiswriter = Writer(
            last_name='FOOBAR', first_name='JACK', ipi_name='199',
            ipi_base='I1234567893', pr_society='010')
        self.thiswriter.clean()
        self.thiswriter.save()
        self.otherwriter = Writer(last_name='DOE', first_name='JANE')
        self.otherwriter.clean()
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
            controlled=True, relative_share=50, capacity='CA').save()
        WriterInWork(
            writer=self.otherwriter, work=self.work, relative_share=50,
            controlled=False).save()
        self.alternate_title = AlternateTitle(
            work=self.work, title='The Alternate Title')
        self.alternate_title.save()
        self.work.firstrecording = FirstRecording(
            work=self.work, isrc='US-123-18-10000', duration=time(minute=1),
            catalog_number='THENUMBER', album_cd=self.album_cd,
            release_date=date.today())
        self.work.firstrecording.save()
        self.work.clean()
        self.work2 = Work(title='Minimal')
        self.work2.save()
        WriterInWork(
            writer=self.thiswriter, work=self.work2, saan='SAMOSAN',
            controlled=True, relative_share=100, capacity='CA').save()
        self.cwr_export = CWRExport()
        self.cwr_export.save()
        self.cwr_export.works.add(self.work)
        self.cwr_export.works.add(self.work2)
        self.cwr_export2 = CWRExport(nwr_rev='REV')
        self.cwr_export2.save()
        self.cwr_export2.works.add(self.work)

    def test_validation(self):
        self.assertTrue(VALIDATE)
        self.work.clean_fields()
        with self.assertRaises(ValidationError) as ve:
            self.artist.first_name = "BAR, JR"
            self.artist.clean_fields()
        self.assertIn('first_name', ve.exception.message_dict)
        self.artist.first_name = "BAR JR"
        self.assertFalse(CWRFieldValidator('x') == CWRFieldValidator('y'))
        with self.assertRaises(ValidationError):
            self.artist.validate_fields({'bad': 'dict'})
        self.work.firstrecording.clean_fields()
        self.assertEqual(self.work.firstrecording.isrc, 'US1231810000')
        self.thiswriter.clean_fields()
        self.assertTrue(self.thiswriter._can_be_controlled)
        self.assertFalse(self.otherwriter._can_be_controlled)
        with self.assertRaises(ValidationError) as ve:
            self.otherwriter.saan = 'S4N1LJ4V4'
            self.otherwriter.clean()
        self.assertIn('saan', ve.exception.message_dict)
        with self.assertRaises(ValidationError) as ve:
            self.otherwriter.saan = None
            self.otherwriter.generally_controlled = True
            self.otherwriter.clean()
        self.assertIn('generally_controlled', ve.exception.message_dict)
        with self.assertRaises(ValidationError) as ve:
            self.thiswriter.saan = 'S4N1LJ4V4'
            self.thiswriter.clean()
        self.assertIn('saan', ve.exception.message_dict)
        with self.assertRaises(ValidationError) as ve:
            self.thiswriter.ipi_name = None
            self.thiswriter.saan = None
            self.thiswriter.clean()
        self.assertFalse(hasattr(ve.exception, 'message_dict'))
        wiws = self.work.writerinwork_set.all()
        for wiw in wiws:
            if not wiw.controlled:
                with self.assertRaises(ValidationError) as ve:
                    wiw.writer.generally_controlled = True
                    wiw.clean()
                self.assertIn('controlled', ve.exception.message_dict)
            else:
                with self.assertRaises(ValidationError) as ve:
                    wiw.capacity = None
                    wiw.clean()
                self.assertIn('capacity', ve.exception.message_dict)
                wiw.capacity = 'CA'
                with self.assertRaises(ValidationError) as ve:
                    wiw.writer._can_be_controlled = False
                    wiw.clean()
                self.assertFalse(hasattr(ve.exception, 'message_dict'))
                with self.assertRaises(ValidationError) as ve:
                    wiw.writer = None
                    wiw.clean()
                self.assertIn('writer', ve.exception.message_dict)

    def test_str(self):
        self.assertEqual(str(self.artist), 'FOO')
        self.artist.first_name = "BAR JR"
        self.assertEqual(str(self.artist), 'BAR JR FOO')
        self.assertEqual(str(self.alternate_title), 'THE ALTERNATE TITLE')
        self.assertEqual(str(self.album_cd), 'ALBUM (XXX 123)')
        self.assertEqual(self.album_cd.album_label, SETTINGS.get('label'))
        self.assertEqual(self.album_cd.library, SETTINGS.get('library'))
        self.album_cd.album_title = None
        self.assertEqual(str(self.album_cd), 'XXX 123')
        self.assertIsNone(self.album_cd.album_label)
        with self.assertRaises(ValidationError) as ve:
            self.album_cd.clean()
        self.assertIn('album_title', ve.exception.message_dict)
        self.album_cd.cd_identifier = None
        with self.assertRaises(ValidationError) as ve:
            self.album_cd.clean()
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

    def test_cwr(self):
        self.assertIn('CW DRAFT ', self.cwr_export.filename)
        self.cwr_export.get_cwr()
        self.assertIn('CW', self.cwr_export.filename)
        self.cwr_export.get_cwr()
        self.cwr_export2.get_cwr()

    def get(self, path, re_post=False):
        response = self.client.get(path)
        self.assertEqual(response.status_code, 200)
        adminform = response.context_data.get('adminform')
        if adminform is None:
            return
        data = adminform.form.initial
        if not re_post:
            return
        if isinstance(re_post, dict):
            data.update(re_post)
        for key, value in data.items():
            if value is None:
                data[key] = ''
            else:
                data[key] = value
        response = self.client.post(path, data)
        self.assertEqual(response.status_code, 302)

    def test_admin(self):
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
        self.get(reverse('admin:music_publisher_cwrexport_changelist',))
        self.get(reverse('admin:music_publisher_ackimport_changelist',))
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
            re_post=False)
        self.client.get(reverse(
            'admin:music_publisher_cwrexport_change',
            args=(self.work.id,)) + '?download=true',
            re_post=False)
        self.client.get(reverse(
            'admin:music_publisher_cwrexport_change',
            args=(self.work.id,)),
            re_post=False)


CONTENT = """HDRSO000000021BMI                                          01.102018060715153220180607
GRHACK0000102.100020180607
ACK0000000000000000201805160910510000100000000NWRONE                                                         00000000000001                          20180607SA
ACK0000000100000000201805160910510000100000001NWRTWO                                                         00000000000002                          20180607SA
ACK0000000200000000201805160910510000100000002NWRTHREE                                                       00000000000003                          20180607NP
TRL000010000008000000839"""