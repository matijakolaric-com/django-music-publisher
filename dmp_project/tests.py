from django.test import TestCase
from django.apps import apps
from django.urls import reverse


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

