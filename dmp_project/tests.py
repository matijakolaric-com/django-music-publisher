"""Summary"""

import importlib
import os
from unittest import mock

from django.apps import apps
from django.conf import settings
from django.test import TestCase, override_settings
from django.urls import reverse


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

    @override_settings(
        DEBUG=True, INSTALLED_APPS=list(settings.INSTALLED_APPS) + ["debug_toolbar"]
    )
    def test_urls_debug_toolbar(self):
        """Test URL configuration when DEBUG is True."""
        import dmp_project.urls

        importlib.reload(dmp_project.urls)
        self.assertTrue(len(dmp_project.urls.urlpatterns) > 0)
        with override_settings(DEBUG=False):
            importlib.reload(dmp_project.urls)

    @override_settings(
        DEBUG=True, INSTALLED_APPS=list(settings.INSTALLED_APPS) + ["debug_toolbar"]
    )
    def test_urls_debug_toolbar_import_error(self):
        """Test URL configuration when DEBUG is True and debug_toolbar is missing."""
        import dmp_project.urls

        with mock.patch.dict(
            "sys.modules",
            {"debug_toolbar": None, "debug_toolbar.toolbar": None},
        ):
            importlib.reload(dmp_project.urls)
            self.assertTrue(len(dmp_project.urls.urlpatterns) > 0)
        with override_settings(DEBUG=False):
            importlib.reload(dmp_project.urls)

    def test_settings_debug_toolbar(self):
        """Test debug toolbar loading in settings when DEBUG is True."""
        settings_path = os.path.abspath("dmp_project/settings.py")
        with open(settings_path) as f:
            code = compile(f.read(), settings_path, "exec")

        with mock.patch.dict(
            os.environ, {"DEBUG": "1", "SECRET_KEY": "testsecretkey"}
        ):
            ns = {"__file__": settings_path}
            exec(code, ns)
            self.assertIn("debug_toolbar", ns.get("INSTALLED_APPS", []))
            self.assertIn(
                "debug_toolbar.middleware.DebugToolbarMiddleware",
                ns.get("MIDDLEWARE", []),
            )

        with mock.patch.dict(
            os.environ, {"DEBUG": "1", "SECRET_KEY": "testsecretkey"}
        ), mock.patch.dict("sys.modules", {"debug_toolbar": None}):
            ns = {"__file__": settings_path}
            exec(code, ns)
