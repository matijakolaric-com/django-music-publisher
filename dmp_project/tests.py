from django.test import TestCase
from django.apps import apps
from django.urls import reverse
from django.conf import settings


class DMPTestCase(TestCase):
    """Tests that go beyond music_publisher app tests."""

    def test_settings(self):
        """Test if all is well with the settings."""

        self.assertTrue(
            apps.is_installed('music_publisher'),
            'App "music_publisher" must be installed.')
        self.assertEqual(
            reverse('admin:index'), '/',
            'Admin not at root url "/". Code will work, but docs will '
            'be misleading.')

        self.assertTrue(hasattr(settings, 'MUSIC_PUBLISHER_SETTINGS'))
        SETTINGS = settings.MUSIC_PUBLISHER_SETTINGS
        self.assertTrue(SETTINGS.get('admin_show_publisher'))
        self.assertTrue(SETTINGS.get('admin_show_saan'))
        self.assertTrue(SETTINGS.get('token'))
        self.assertTrue(SETTINGS.get('validator_url'))
        self.assertTrue(SETTINGS.get('generator_url'))
        self.assertTrue(SETTINGS.get('library'))
        self.assertTrue(SETTINGS.get('label'))
        self.assertTrue(SETTINGS.get('publisher_id'))
        self.assertTrue(SETTINGS.get('publisher_name'))
        self.assertTrue(SETTINGS.get('publisher_ipi_name'))
        self.assertTrue(SETTINGS.get('publisher_pr_society'))
        self.assertIn('publisher_sr_society', SETTINGS)
        self.assertIn('publisher_mr_society', SETTINGS)
