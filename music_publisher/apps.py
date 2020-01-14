from django.apps import AppConfig
from .validators import validate_settings


class MusicPublisherConfig(AppConfig):

    """Configuration for Music Publisher app.

    Attributes:
        label (str): app label
        name (str): app name
        verbose_name (str): app verbose name
    """

    name = 'music_publisher'
    label = 'music_publisher'
    verbose_name = 'Music Publisher'

    def ready(self):
        validate_settings()

