"""Contains base (abstract) classes used in :mod:`.models`
"""

import django.core.exceptions
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
import re
from .validators import CWRFieldValidator
from django.conf import settings

def get_societies():
    return settings.SOCIETIES

class TitleBase(models.Model):
    """Abstract class for all classes that have a title.

    Attributes:
        title (django.db.models.CharField): Title, used in work title,
            alternate title, etc.
    """

    class Meta:
        abstract = True

    title = models.CharField(
        max_length=60, db_index=True,
        validators=(CWRFieldValidator('work_title'),))

    def __str__(self):
        return self.title.upper()


class PersonBase(models.Model):
    """Base class for all classes that contain people with first and last name.

    Attributes:
        first_name (django.db.models.CharField): First Name
        last_name (django.db.models.CharField): Last Name
    """

    class Meta:
        abstract = True

    first_name = models.CharField(
        max_length=30, blank=True,
        validators=(CWRFieldValidator('artist_first_name'),))
    last_name = models.CharField(
        max_length=45, db_index=True,
        validators=(CWRFieldValidator('artist_last_name'),))

    def __str__(self):
        if self.first_name:
            return '{0.first_name} {0.last_name}'.format(self).upper()
        return self.last_name.upper()


class IPIBase(models.Model):
    """Abstract base for all objects containing IPI numbers.

    Attributes:
        generally_controlled (django.db.models.BooleanField):
            General agreement (renamed in verbose_name)
        ipi_base (django.db.models.CharField): IPI Base Number
        ipi_name (django.db.models.CharField): IPI Name Number
        pr_society (django.db.models.CharField):
            Performing Rights Society Code
        publisher_fee (django.db.models.DecimalField): Publisher Fee
        saan (django.db.models.CharField):
            Society-assigned agreement number, in this context it is used for
            general agreements, for specific agreements use
            :attr:`.models.WriterInWork.saan`.
        _can_be_controlled (django.db.models.BooleanField):
            used to determine if there is enough data for a writer
            to be controlled.
        generally_controlled (django.db.models.BooleanField):
            flags if a writer is generally controlled (in all works)
        publisher_fee (django.db.models.DecimalField):
            this field is used in calculating publishing fees
    """

    class Meta:
        abstract = True

    ipi_name = models.CharField(
        'IPI Name #', max_length=11, blank=True, null=True, unique=True,
        validators=(CWRFieldValidator('writer_ipi_name'),))
    ipi_base = models.CharField(
        'IPI Base #', max_length=15, blank=True, null=True,
        validators=(CWRFieldValidator('writer_ipi_base'),))
    pr_society = models.CharField(
        'Performance rights society', max_length=3, blank=True, null=True,
        validators=(CWRFieldValidator('writer_pr_society'),),
        choices=get_societies())
    mr_society = models.CharField(
        'Mechanical rights society', max_length=3, blank=True, null=True,
        validators=(CWRFieldValidator('writer_pr_society'),),
        choices=get_societies())
    sr_society = models.CharField(
        'Synchronization rights society', max_length=3, blank=True, null=True,
        validators=(CWRFieldValidator('writer_pr_society'),),
        choices=get_societies())
    saan = models.CharField(
        'Society-assigned general agreement number',
        help_text='Use this field for general agreements only.\n'
            'For specific agreements use the field in the Work form,\n'
            'in Writers In Work section.',
        validators=(CWRFieldValidator('saan'),),
        max_length=14, blank=True, null=True, unique=True)

    _can_be_controlled = models.BooleanField(editable=False, default=False)
    generally_controlled = models.BooleanField(
        'General agreement', default=False)
    publisher_fee = models.DecimalField(
        max_digits=5, decimal_places=2, blank=True, null=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text=
            'Percentage of royalties kept by the publisher,\n'
            'in a general agreement.')

    def clean_fields(self, *args, **kwargs):
        """
        Data cleanup, allowing various import formats to be converted into
        consistently formatted data.
        """
        if self.saan:
            self.saan = self.saan.upper()  # only in CWR, uppercase anyway
        if self.ipi_name:
            self.ipi_name = self.ipi_name.rjust(11, '0')
        if self.ipi_base:
            self.ipi_base = self.ipi_base.replace('.', '')
            self.ipi_base = re.sub(
                r'(I).?(\d{9}).?(\d)',
                r'\1-\2-\3',
                self.ipi_base)
        return super().clean_fields(*args, **kwargs)

    def clean(self):
        """Clean the data and validate."""

        self._can_be_controlled = bool(self.ipi_name) & bool(self.pr_society)
        d = {}
        if not self.generally_controlled:
            if self.saan:
                d['saan'] = 'Only for a general agreement.'
            if self.publisher_fee:
                d['publisher_fee'] = 'Only for a general agreement.'
        else:
            if not self._can_be_controlled:
                d['generally_controlled'] = (
                    'IPI name number and PR society fields are required for '
                    'a controlled writer.')
            if settings.REQUIRE_SAAN and not self.saan:
                d['saan'] = 'This field is required.'
            if settings.REQUIRE_PUBLISHER_FEE and not self.publisher_fee:
                d['publisher_fee'] = 'This field is required.'
        if d:
            raise django.core.exceptions.ValidationError(d)
