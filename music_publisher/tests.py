from django.test import TestCase
from datetime import date
from music_publisher.models import *
from django.core.exceptions import ValidationError
import json


class ModelsTest(TestCase):
    def setUp(self):
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
            controlled=False, capacity='CA').save()
        self.alternate_title = AlternateTitle(
            work=self.work, title='The Alternate Title')
        self.alternate_title.save()
        self.work.firstrecording = FirstRecording(
            work=self.work, isrc='US-123-18-10000')
        self.work.firstrecording.save()
        self.work.clean()

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

    def test_json(self):
        dump = json.dumps(self.work.json, indent=4)
        self.assertIn('"SAMOSAN"', dump)


FIELDS = {
    'writer_id': 'XZY',
    'writer_last_name': 'DOE-SMITH',
    'writer_first_name': 'JOHN JAMES',
    'writer_ipi_name': '00000000395',
    'writer_pr_society': '021',
    'controlled': True,
    'capacity': 'CA',
    'relative_share': '1.0000'
}


TEST_JSON = '''{
    "publisher_id": "TOP",
    "publisher_name": "THE ORIGINAL PUBLISHER",
    "publisher_ipi_name": "199",
    "publisher_ipi_base": "I0000000393",
    "publisher_pr_society": "052",
    "publisher_mr_society": "044",
    "publisher_sr_society": null,
    "revision": false,
    "works": {
        "M1N1M41": {
            "work_title": "MINIMAL",
            "alternate_titles": [],
            "artists": [],
            "writers": [
                {
                    "writer_id": "XZY",
                    "writer_last_name": "DOE-SMITH",
                    "writer_first_name": "JOHN JAMES",
                    "writer_ipi_name": "00000000395",
                    "writer_pr_society": "021",
                    "controlled": true,
                    "capacity": "CA",
                    "relative_share": "1.0000"
                }
            ]
        },
        "ABC1": {
            "work_title": "WORK TWO",
            "isrc": "JMK401400212",
            "alternate_titles": [],
            "artists": [
                {
                    "artist_last_name": "THE JANE DOE EXTRA BAND"
                },
                {
                    "artist_last_name": "DOE-SMITH",
                    "artist_first_name": "JOHN JAMES"
                }
            ],
            "writers": [
                {
                    "writer_id": "XZY",
                    "writer_last_name": "DOE-SMITH",
                    "writer_first_name": "JOHN JAMES",
                    "writer_ipi_name": "00000000395",
                    "writer_pr_society": "021",
                    "controlled": true,
                    "capacity": "CA",
                    "relative_share": "1.0000"
                }
            ]
        },
        "1234": {
            "work_title": "WORK ONE",
            "iswc": "T1234567894",
            "alternate_titles": [
                {
                    "alternate_title": "THE ONE"
                },
                {
                    "alternate_title": "THE ONE WORK"
                }
            ],
            "artists": [],
            "writers": [
                {
                    "writer_id": "1",
                    "writer_last_name": "JONES",
                    "writer_first_name": "",
                    "writer_ipi_name": "297",
                    "writer_pr_society": "052",
                    "controlled": true,
                    "capacity": "C ",
                    "relative_share": "0.6667",
                    "saan": "XDF1234"
                },
                {
                    "writer_id": "2",
                    "writer_last_name": "",
                    "writer_first_name": "",
                    "controlled": false,
                    "capacity": "",
                    "relative_share": "0.3333"
                }
            ]
        },
        "FLH0U53": {
            "work_title": "FULL HOUSE",
            "iswc": "T1234567805",
            "first_release_date": "2001-07-30",
            "first_release_duration": "00:03:45",
            "first_album_title": "THE FIRST ALBUM",
            "first_album_label": "LABEL WITH NO LABEL",
            "first_release_catalog_number": "001",
            "ean": "4006381333931",
            "isrc": "QMK401400212",
            "library": "THE EXEMPLARY LIBRARY",
            "cd_identifier": "ASD 123",
            "alternate_titles": [
                {
                    "alternate_title": "THE COMPLETE EXAMPLE"
                }
            ],
            "artists": [
                {
                    "artist_last_name": "THE JANE DOE EXTRA BAND"
                },
                {
                    "artist_last_name": "DOE-SMITH",
                    "artist_first_name": "JOHN JAMES"
                }
            ],
            "writers": [
                {
                    "writer_id": "XZY",
                    "writer_last_name": "DOE-SMITH",
                    "writer_first_name": "JOHN JAMES",
                    "writer_ipi_name": "00000000395",
                    "writer_ipi_base": "I0000000393",
                    "writer_pr_society": "021",
                    "controlled": true,
                    "capacity": "CA",
                    "relative_share": "0.3333"
                },
                {
                    "writer_id": "007",
                    "writer_last_name": "BOND",
                    "writer_first_name": "JAMES",
                    "writer_ipi_name": "00000000493",
                    "writer_pr_society": "052",
                    "controlled": false,
                    "capacity": "CA",
                    "relative_share": "0.1667"
                },
                {
                    "writer_id": "",
                    "writer_last_name": "",
                    "writer_first_name": "",
                    "writer_ipi_name": "",
                    "writer_pr_society": "",
                    "controlled": false,
                    "capacity": "",
                    "relative_share": "0.1667"
                },
                {
                    "writer_id": "",
                    "writer_last_name": "",
                    "writer_first_name": "",
                    "writer_ipi_name": "",
                    "writer_pr_society": "",
                    "controlled": false,
                    "capacity": "",
                    "relative_share": "0.1667"
                },
                {
                    "writer_id": "",
                    "writer_last_name": "",
                    "writer_first_name": "",
                    "writer_ipi_name": "",
                    "writer_pr_society": "",
                    "controlled": false,
                    "capacity": "",
                    "relative_share": "0.1667"
                }
            ]
        }
    }
}'''