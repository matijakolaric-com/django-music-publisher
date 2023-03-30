"""Summary
"""
from django.test import (TestCase, override_settings)
from django.apps import apps
from django.urls import reverse
from django.conf import settings


@override_settings(OPTION_FILES=True)
class DMPTestCase(TestCase):
    """Tests that go beyond music_publisher app tests."""

    def test_settings(self):
        """Test if all is well with the settings."""

        self.assertTrue(
            apps.is_installed("music_publisher"),
            'App "music_publisher" must be installed.',
        )
        self.assertEqual(
            reverse("admin:index"),
            "/",
            'Admin not at root url "/". Code will work, but docs will '
            "be misleading.",
        )

        self.assertTrue(hasattr(settings, "PUBLISHER_NAME"))
        self.assertTrue(hasattr(settings, "PUBLISHER_CODE"))
        self.assertTrue(hasattr(settings, "PUBLISHER_IPI_BASE"))
        self.assertTrue(hasattr(settings, "PUBLISHER_IPI_NAME"))
        self.assertTrue(hasattr(settings, "PUBLISHER_SOCIETY_PR"))
        self.assertTrue(hasattr(settings, "PUBLISHER_SOCIETY_MR"))
        self.assertTrue(hasattr(settings, "PUBLISHER_SOCIETY_SR"))
        self.assertTrue(hasattr(settings, "PUBLISHING_AGREEMENT_PUBLISHER_PR"))
        self.assertTrue(hasattr(settings, "PUBLISHING_AGREEMENT_PUBLISHER_MR"))
        self.assertTrue(hasattr(settings, "PUBLISHING_AGREEMENT_PUBLISHER_SR"))
