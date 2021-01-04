"""
Main interface for :mod:`music_publisher`.

All views are here, except for :mod:`.royalty_calculation`.

"""
import re
import zipfile
from csv import DictWriter
from datetime import datetime
from decimal import Decimal

from django import forms
from django.conf import settings
from django.contrib import admin, messages
from django.core.exceptions import ValidationError
from django.db import models
from django.forms import FileField, ModelForm, BooleanField
from django.forms.models import BaseInlineFormSet
from django.http import HttpResponse, JsonResponse, StreamingHttpResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils.html import mark_safe
from django.utils.timezone import now

from .validators import CWRFieldValidator
from .models import (
    ACKImport, AlternateTitle, Artist, ArtistInWork, CWRExport,
    CommercialRelease, Label, Library, LibraryRelease, Recording, Release,
    SOCIETY_DICT, Track, Work, WorkAcknowledgement, Writer, WriterInWork,
    DataImport,
)

IS_POPUP_VAR = admin.options.IS_POPUP_VAR


class MusicPublisherAdmin(admin.ModelAdmin):
    """Parent class to all admin classes."""
    save_as = True


class ArtistInWorkInline(admin.TabularInline):
    """Inline interface for :class:`.models.ArtistInWork`.
    """
    autocomplete_fields = ('artist', 'work')
    model = ArtistInWork
    extra = 0
    verbose_name_plural = \
        'Artists performing Works (not mentioned in "recordings" section)'


class RecordingInline(admin.StackedInline):
    """Inline interface for :class:`.models.Recording`,
        used in :class:`WorkAdmin`.
    """
    autocomplete_fields = ('artist', 'work', 'record_label')
    readonly_fields = ('complete_recording_title', 'complete_version_title')
    show_change_link = True
    fieldsets = (
        (None, {
            'fields': (
                'work',
                ('recording_title', 'recording_title_suffix',
                 'complete_recording_title'),
                ('version_title', 'version_title_suffix',
                 'complete_version_title'),
                ('isrc', 'record_label', 'artist'),
                ('duration', 'release_date'),
            ),
        }),
    )
    formfield_overrides = {
        models.TimeField: {'widget': forms.TimeInput},
    }
    verbose_name_plural = \
        'Recordings (with recording artists and record labels)'
    model = Recording
    ordering = ('recording_title', 'version_title')
    extra = 0


@admin.register(Artist)
class ArtistAdmin(MusicPublisherAdmin):
    """Admin interface for :class:`.models.Artist`.
    """

    list_display = (
        'last_or_band', 'first_name', 'isni', 'recording_count', 'work_count')
    search_fields = ('last_name', 'isni',)
    fieldsets = (
        ('Name', {'fields': (('first_name', 'last_name'),)}),
        ('ISNI', {'fields': ('isni',), }),
    )

    def last_or_band(self, obj):
        """Placeholder for :attr:`.models.Artist.last_name`."""
        return obj.last_name

    last_or_band.short_description = 'Last or band name'
    last_or_band.admin_order_field = 'last_name'

    actions = None

    def save_model(self, request, obj, form, *args, **kwargs):
        """Save, then update ``last_change`` of the works whose CWR
        registration changes due to this change.
        """
        super().save_model(request, obj, form, *args, **kwargs)
        if form.changed_data:
            qs = Work.objects.filter(
                models.Q(artistinwork__artist=obj) |
                models.Q(recordings__artist=obj))
            qs.update(last_change=now())

    def get_queryset(self, request):
        """Optimized queryset for changelist view.
        """
        qs = super().get_queryset(request)
        qs = qs.annotate(models.Count('work', distinct=True))
        qs = qs.annotate(models.Count('recording', distinct=True))
        return qs

    def work_count(self, obj):
        """Return the work count from the database field, or count them.
        (dealing with legacy)"""

        count = obj.work__count

        url = reverse('admin:music_publisher_work_changelist')
        url += '?artists__id__exact={}'.format(obj.id)
        return mark_safe('<a href="{}">{}</a>'.format(url, count))

    work_count.short_description = 'Perf. Works'
    work_count.admin_order_field = 'work__count'

    def recording_count(self, obj):
        """Return the work count from the database field, or count them.
        (dealing with legacy)"""

        count = obj.recording__count

        url = reverse('admin:music_publisher_recording_changelist')
        url += '?recording_artist__id__exact={}'.format(obj.id)
        return mark_safe('<a href="{}">{}</a>'.format(url, count))

    recording_count.short_description = 'Recordings'
    recording_count.admin_order_field = 'recording__count'


@admin.register(Label)
class LabelAdmin(MusicPublisherAdmin):
    """Admin interface for :class:`.models.Label`.
    """
    actions = None
    search_fields = ('name',)
    list_display = (
        'name', 'recording_count', 'commercialrelease_count',
        'libraryrelease_count')
    readonly_fields = (
        'recording_count', 'commercialrelease_count', 'libraryrelease_count')
    
    fields = ('name',)

    def get_queryset(self, request):
        """Optimized queryset for changelist view.
        """
        qs = super().get_queryset(request)
        qs = qs.annotate(
            libraryrelease__count=models.Count(
                'release', distinct=True,
                filter=models.Q(release__cd_identifier__isnull=False)))
        qs = qs.annotate(
            commercialrelease__count=models.Count(
                'release', distinct=True,
                filter=models.Q(release__cd_identifier__isnull=True)))
        qs = qs.annotate(models.Count('recording', distinct=True))
        return qs

    def commercialrelease_count(self, obj):
        """Return the work count from the database field, or count them.
        (dealing with legacy)"""

        count = obj.commercialrelease__count

        url = reverse('admin:music_publisher_commercialrelease_changelist')
        url += '?release_label__id__exact={}'.format(obj.id)
        return mark_safe('<a href="{}">{}</a>'.format(url, count))

    commercialrelease_count.short_description = 'Commercial releases'
    commercialrelease_count.admin_order_field = 'commercialrelease__count'

    def libraryrelease_count(self, obj):
        """Return the work count from the database field, or count them.
        (dealing with legacy)"""

        count = obj.libraryrelease__count

        url = reverse('admin:music_publisher_libraryrelease_changelist')
        url += '?release_label__id__exact={}'.format(obj.id)
        return mark_safe('<a href="{}">{}</a>'.format(url, count))

    libraryrelease_count.short_description = 'Library releases'
    libraryrelease_count.admin_order_field = 'libraryrelease__count'

    def recording_count(self, obj):
        """Return the work count from the database field, or count them.
        (dealing with legacy)"""

        count = obj.recording__count

        url = reverse('admin:music_publisher_recording_changelist')
        url += '?record_label__id__exact={}'.format(obj.id)
        return mark_safe('<a href="{}">{}</a>'.format(url, count))

    recording_count.short_description = 'Recordings'
    recording_count.admin_order_field = 'recording__count'

    def save_model(self, request, obj, form, *args, **kwargs):
        """Save, then update ``last_change`` of the corresponding works.
        """
        super().save_model(request, obj, form, *args, **kwargs)
        if form.changed_data:
            qs = Work.objects.filter(
                models.Q(recordings__record_label=obj))
            qs.update(last_change=now())


@admin.register(Library)
class LibraryAdmin(MusicPublisherAdmin):
    """Admin interface for :class:`.models.Library`.
    """
    actions = None
    search_fields = ('name',)

    list_display = ('name', 'libraryrelease_count', 'work_count')
    readonly_fields = ('libraryrelease_count', 'work_count')
    fields = ('name',)

    def get_queryset(self, request):
        """Optimized queryset for changelist view.
        """
        qs = super().get_queryset(request)
        qs = qs.annotate(
            work__count=models.Count('release__works', distinct=True))
        qs = qs.annotate(
            release__count=models.Count('release__id', distinct=True))
        return qs

    def libraryrelease_count(self, obj):
        """Return the work count from the database field, or count them.
        (dealing with legacy)"""

        count = obj.release__count

        url = reverse('admin:music_publisher_libraryrelease_changelist')
        url += '?library__id__exact={}'.format(obj.id)
        return mark_safe('<a href="{}">{}</a>'.format(url, count))

    libraryrelease_count.short_description = 'Library releases'
    libraryrelease_count.admin_order_field = 'libraryrelease__count'

    def work_count(self, obj):
        """Return the work count from the database field, or count them.
        (dealing with legacy)"""

        count = obj.work__count

        url = reverse('admin:music_publisher_work_changelist')
        url += '?library_release__library__id__exact={}'.format(obj.id)
        return mark_safe('<a href="{}">{}</a>'.format(url, count))

    work_count.short_description = 'Works'
    work_count.admin_order_field = 'work__count'

    def save_model(self, request, obj, form, *args, **kwargs):
        """Save, then update ``last_change`` of the corresponding works.
        """
        super().save_model(request, obj, form, *args, **kwargs)
        if form.changed_data:
            qs = Work.objects.filter(
                models.Q(library_release__library=obj))
            qs.update(last_change=now())


class TrackInline(admin.TabularInline):
    """Inline interface for :class:`.models.Track`, used in
    :class:`LibraryReleaseAdmin` and :class:`CommercialReleaseAdmin`.
    """
    model = Track
    autocomplete_fields = ('release', 'recording')
    extra = 0


@admin.register(Release)
class ReleaseAdmin(MusicPublisherAdmin):
    """Admin interface for :class:`.models.Release`.
    """

    actions = None
    list_display = (
        '__str__',
    )

    search_fields = ('release_title', '^cd_identifier')

    def has_module_permission(self, request):
        """Return False"""
        return False

    def has_add_permission(self, request):
        """Return False"""
        return False

    def has_change_permission(self, request, obj=None):
        """Return False"""
        return False

    def has_delete_permission(self, request, obj=None):
        """Return False"""
        return False


class LibraryReleaseForm(forms.ModelForm):
    """Custom form for :class:`.models.LibraryRelease`.
    """

    def __init__(self, *args, **kwargs):
        """Make cd_identifier and library fields required."""
        super().__init__(*args, **kwargs)
        self.fields['cd_identifier'].required = True
        self.fields['library'].required = True


@admin.register(LibraryRelease)
class LibraryReleaseAdmin(MusicPublisherAdmin):
    """Admin interface for :class:`.models.LibraryRelease`.
    """

    form = LibraryReleaseForm
    inlines = [TrackInline]
    autocomplete_fields = ('release_label', 'library')

    fieldsets = (
        ('Library', {
            'fields': (
                ('library', 'cd_identifier'),)
        }),
        ('Release (album)', {
            'fields': (
                ('release_title', 'release_label'),
                ('ean', 'release_date'))
        }),
    )

    list_display = (
        'cd_identifier',
        'library',
        'release_title',
        'release_label',
        'release_date',
        'work_count',
        'track_count',
    )
    readonly_fields = ('work_count', 'track_count')

    list_filter = ('release_label', 'library')
    search_fields = ('release_title', '^cd_identifier')

    def get_inline_instances(self, request, obj=None):
        """Limit inlines in popups."""
        if IS_POPUP_VAR in request.GET or IS_POPUP_VAR in request.POST:
            return []
        return super().get_inline_instances(request)

    def save_model(self, request, obj, form, *args, **kwargs):
        """Save, then update ``last_change`` of the corresponding works.
        """
        super().save_model(request, obj, form, *args, **kwargs)
        if form.changed_data:
            qs = Work.objects.filter(library_release=obj)
            qs.update(last_change=now())

    def get_queryset(self, request):
        """Optimized queryset for changelist view.
        """
        qs = super().get_queryset(request)
        qs = qs.annotate(models.Count('tracks', distinct=True))
        qs = qs.annotate(models.Count('works', distinct=True))
        return qs

    def work_count(self, obj):
        """Return the work count from the database field, or count them.
        (dealing with legacy)"""

        count = obj.works__count

        url = reverse('admin:music_publisher_work_changelist')
        url += '?library_release__id__exact={}'.format(obj.id)
        return mark_safe('<a href="{}">{}</a>'.format(url, count))

    work_count.short_description = 'Works'
    work_count.admin_order_field = 'works__count'

    def track_count(self, obj):
        """Return the work count from the database field, or count them.
        (dealing with legacy)"""

        count = obj.tracks__count

        url = reverse('admin:music_publisher_recording_changelist')
        url += '?release__id__exact={}'.format(obj.id)
        return mark_safe('<a href="{}">{}</a>'.format(url, count))

    track_count.short_description = 'Recordings'
    track_count.admin_order_field = 'tracks__count'

    def create_json(self, request, qs):
        """Batch action that downloads a JSON file containing library releases.

        Returns:
            JsonResponse: JSON file with selected works
        """

        j = LibraryRelease.objects.get_dict(qs)

        response = JsonResponse(j, json_dumps_params={'indent': 4})
        name = '{}-libraryreleases-{}'.format(
            settings.PUBLISHER_CODE, datetime.now().toordinal())
        cd = 'attachment; filename="{}.json"'.format(name)
        response['Content-Disposition'] = cd
        return response

    create_json.short_description = \
        'Export selected library releases (JSON).'

    actions = ['create_json']

    def get_actions(self, request):
        """Custom action disabling the default ``delete_selected``."""
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions


@admin.register(CommercialRelease)
class CommercialReleaseAdmin(MusicPublisherAdmin):
    """Admin interface for :class:`.models.CommercialRelease`.
    """

    inlines = [TrackInline]
    autocomplete_fields = ('release_label',)

    list_display = (
        'release_title',
        'release_label',
        'release_date',
        'track_count',
    )

    readonly_fields = ('track_count',)

    list_filter = ('release_label',)
    search_fields = ('release_title',)

    fieldsets = (
        (None, {
            'fields': (
                ('release_title', 'release_label'),
                ('ean', 'release_date'))
        }),
    )

    def get_inline_instances(self, request, obj=None):
        """Limit inlines in popups."""
        if IS_POPUP_VAR in request.GET or IS_POPUP_VAR in request.POST:
            return []
        return super().get_inline_instances(request)

    def get_queryset(self, request):
        """Optimized queryset for changelist view.
        """
        qs = super().get_queryset(request)
        qs = qs.annotate(models.Count('tracks', distinct=True))
        return qs

    def track_count(self, obj):
        """Return the work count from the database field, or count them.
        (dealing with legacy)"""

        count = obj.tracks__count

        url = reverse('admin:music_publisher_recording_changelist')
        url += '?release__id__exact={}'.format(obj.id)
        return mark_safe('<a href="{}">{}</a>'.format(url, count))

    track_count.short_description = 'Recordings'
    track_count.admin_order_field = 'tracks__count'

    def create_json(self, request, qs):
        """Batch action that downloads a JSON file containing comercial releases.

        Returns:
            JsonResponse: JSON file with selected commercial releases
        """

        j = CommercialRelease.objects.get_dict(qs)

        response = JsonResponse(j, json_dumps_params={'indent': 4})
        name = '{}-libraryreleases-{}'.format(
            settings.PUBLISHER_CODE, datetime.now().toordinal())
        cd = 'attachment; filename="{}.json"'.format(name)
        response['Content-Disposition'] = cd
        return response

    create_json.short_description = \
        'Export selected commercial releases (JSON).'

    actions = ['create_json']

    def get_actions(self, request):
        """Custom action disabling the default ``delete_selected``."""
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions


@admin.register(Writer)
class WriterAdmin(MusicPublisherAdmin):
    """Interface for :class:`.models.Writer`.
    """

    list_display = ('last_name', 'first_name', 'ipi_name', 'pr_society',
                    '_can_be_controlled', 'generally_controlled',
                    'work_count')

    list_filter = ('_can_be_controlled', 'generally_controlled', 'pr_society')
    search_fields = ('last_name', 'ipi_name')
    readonly_fields = ('_can_be_controlled', 'work_count')

    def get_fieldsets(self, request, obj=None):
        """Return the fieldsets.

        Depending on settings, MR and PR affiliations may not be needed.
        See :meth:`WriterAdmin.get_society_list`"""
        return (
            ('Name', {
                'fields': (
                    ('first_name', 'last_name'),)
            }),
            ('IPI', {
                'fields': (
                    ('ipi_name', 'ipi_base'),),
            }),
            ('Societies', {
                'fields': (
                    self.get_society_list(),),
            }),
            ('General agreement', {
                'fields': (
                    ('generally_controlled',
                     ('saan', 'publisher_fee'))
                ),
            }),
        )

    actions = None

    @staticmethod
    def get_society_list():
        """List which society fields are required.

        Mechanical and Sync affiliation is not required if writers don't
        collect any of it, which is the most usual case."""

        societies = ['pr_society']
        if settings.PUBLISHING_AGREEMENT_PUBLISHER_MR != Decimal(1):
            societies.append('mr_society')
        if settings.PUBLISHING_AGREEMENT_PUBLISHER_SR != Decimal(1):
            societies.append('sr_society')
        return societies

    def save_model(self, request, obj, form, *args, **kwargs):
        """Perform normal save_model, then update last_change of
        all connected works."""
        super().save_model(request, obj, form, *args, **kwargs)
        if form.changed_data:
            qs = Work.objects.filter(writerinwork__writer=obj)
            qs.update(last_change=now())

    def get_queryset(self, request):
        """Optimized queryset for changelist view.
        """
        qs = super().get_queryset(request)
        qs = qs.annotate(models.Count('work', distinct=True))
        return qs

    def work_count(self, obj):
        """Return the work count from the database field, or count them.
        (dealing with legacy)"""

        count = obj.work__count

        url = reverse('admin:music_publisher_work_changelist')
        url += '?writers__id__exact={}'.format(obj.id)
        return mark_safe('<a href="{}">{}</a>'.format(url, count))

    work_count.short_description = 'Works'
    work_count.admin_order_field = 'work__count'


class AlternateTitleFormSet(BaseInlineFormSet):
    """Formset for :class:`AlternateTitleInline`.
    """

    orig_cap = ['C ', 'A ', 'CA']

    def clean(self):
        """Performs these checks:
            if suffix is used, then validates the total length

        Returns:
            None

        Raises:
            ValidationError
        """
        work_title_len = len(self.instance.title)
        for form in self.forms:
            if not form.is_valid():
                return
            if form.cleaned_data and not form.cleaned_data.get('DELETE'):
                if not form.cleaned_data.get('suffix'):
                    continue
                title_suffix_len = len(form.cleaned_data['title'])
                if work_title_len + title_suffix_len > 60 - 1:
                    form.add_error(
                        'title',
                        'Too long for suffix, work title plus suffix must be '
                        '59 characters or less.')


class AlternateTitleInline(admin.TabularInline):
    """Inline interface for :class:`.models.AlternateTitle`.
    """
    model = AlternateTitle
    formset = AlternateTitleFormSet
    extra = 0
    readonly_fields = ('complete_alt_title',)
    verbose_name_plural = \
        'Alternative titles (not mentioned in "recordings" section)'
    fields = ('title', 'suffix', 'complete_alt_title')

    def complete_alt_title(self, obj):
        """Return the complete title, see
        :meth:`.models.AlternateTitle.__str__`"""
        return str(obj)


class WriterInWorkFormSet(BaseInlineFormSet):
    """Formset for :class:`WriterInWorkInline`.
    """

    orig_cap = ['C ', 'A ', 'CA']

    def clean(self):
        """Performs these checks:
            at least one writer must be controlled,
            at least one writer music be Composer or Composer&Lyricist
            sum of relative shares must be ~100%

        Returns:
            None

        Raises:
            ValidationError
        """
        is_modification = self.instance.is_modification()
        super().clean()
        total = 0
        controlled = False
        has_composer = False
        writers = []
        needs_extended_capacity = is_modification
        for form in self.forms:
            if not form.is_valid():
                return
            if form.cleaned_data and not form.cleaned_data.get('DELETE'):
                writer = form.cleaned_data['writer']
                writers.append(writer)
                total += form.cleaned_data['relative_share']
                if form.cleaned_data['controlled']:
                    controlled = True
                if form.cleaned_data['capacity'] in ['C ', 'CA']:
                    has_composer = True
                if (not is_modification and form.cleaned_data['capacity'] and
                        form.cleaned_data['capacity'] not in self.orig_cap):
                    form.add_error(
                        'capacity',
                        'Not allowed in original works.')
                if (is_modification and form.cleaned_data['capacity'] and
                        form.cleaned_data['capacity'] not in self.orig_cap):
                    needs_extended_capacity = False
        if needs_extended_capacity:
            for form in self.forms:
                form.add_error(
                    'capacity',
                    'At least one must be Arranger, Adaptor or Translator.')
            raise ValidationError(
                'In a modified work, '
                'at least one writer must be Arranger, Adaptor or Translator.')
        if not controlled:
            for form in self.forms:
                form.add_error(
                    'controlled', 'At least one writer must be controlled.')
            raise ValidationError('At least one writer must be controlled.')
        if not has_composer:
            for form in self.forms:
                form.add_error(
                    'capacity',
                    'At least one writer must be Composer or '
                    'Composer&Lyricist.')
            raise ValidationError(
                'At least one writer must be Composer or Composer&Lyricist.')
        if not (Decimal(99.98) <= total <= Decimal(100.02)):
            for form in self.forms:
                form.add_error(
                    'relative_share', 'Sum of manuscript shares must be 100%.')
            raise ValidationError('Sum of manuscript shares must be 100%.')
        if is_modification:
            writer_capacities = {}
            for form in self.forms:
                cd = form.cleaned_data
                if cd['controlled']:
                    writer_capacities[cd['writer'].id] = cd['capacity']
            for form in self.forms:
                cd = form.cleaned_data
                if cd['writer'] and not cd['controlled']:
                    controlled_capacity = writer_capacities.get(
                        cd['writer'].id)
                    if (controlled_capacity and
                            cd['capacity'] != controlled_capacity):
                        form.add_error(
                            'capacity',
                            'Must be same as in controlled line for this '
                            'writer.')


class WriterInWorkInline(admin.TabularInline):
    """Inline interface for :class:`.models.WriterInWork`.
    """

    autocomplete_fields = ('writer',)
    model = WriterInWork
    formset = WriterInWorkFormSet
    extra = 0
    min_num = 1  # One writer is required
    fields = (
        'writer', 'capacity', 'relative_share', 'controlled', 'saan',
        'publisher_fee')


class WorkAcknowledgementInline(admin.TabularInline):
    """Inline interface for :class:`.models.WorkAcknowledgement`,
        used in :class:`WorkAdmin`.

        Note that normal users should only have a 'view' permission.
    """

    model = WorkAcknowledgement
    extra = 0
    fields = ('date', 'society_code', 'remote_work_id', 'status')


class WorkForm(forms.ModelForm):
    """Custom form for :class:`.models.Work`.

    Calculate values for readonly field version_type."""

    class Meta:
        model = Work
        fields = [
            'title', 'iswc', 'original_title', 'library_release']

    version_type = forms.NullBooleanField(
        widget=forms.Select(
            choices=(
                (None, ''),
                (True, 'Modification'),
                (False, 'Original Work'))),
        disabled=True,
        required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['version_type'].initial = self.instance.is_modification()


@admin.register(Work)
class WorkAdmin(MusicPublisherAdmin):
    """Admin interface for :class:`.models.Work`.

    This is by far the most important part of the interface.

    Attributes:
        actions (tuple): batch actions used:
            :meth:`create_cwr`,
            :meth:`create_json`
        inlines (tuple): inlines used in change view:
            :class:`AlternateTitleInline`,
            :class:`WriterInWorkInline`,
            :class:`RecordingInline`,
            :class:`ArtistInWorkInline`,
            :class:`WorkAcknowledgementInline`,
    """

    form = WorkForm

    inlines = (
        WriterInWorkInline,
        RecordingInline,
        AlternateTitleInline,
        ArtistInWorkInline,
        WorkAcknowledgementInline)

    def writer_last_names(self, obj):
        """This is a standard way how writers are shown in other apps."""

        return ' / '.join(
            writer.last_name.upper() for writer in set(
                obj.writers.order_by('last_name')))

    writer_last_names.short_description = 'Writers\' last names'
    writer_last_names.admin_order_field = 'writers__last_name'

    def percentage_controlled(self, obj):
        """Controlled percentage
        (sum of relative shares for controlled writers)

        Please note that writers in work are already included in the queryset
        for other reasons, so no overhead except summing.
        """
        return sum(
            wiw.relative_share for wiw in obj.writerinwork_set.all()
            if wiw.controlled)

    percentage_controlled.short_description = '% controlled'

    def work_id(self, obj):
        """Return :attr:`.models.Work.work_id`, make it sortable."""
        return obj.work_id

    work_id.short_description = 'Work ID'
    work_id.admin_order_field = 'id'

    def cwr_export_count(self, obj):
        """Return the count of CWR exports with the link to the filtered
        changelist view for :class:`CWRExportAdmin`."""

        count = obj.cwr_exports__count
        url = reverse('admin:music_publisher_cwrexport_changelist')
        url += '?works__id__exact={}'.format(obj.id)
        return mark_safe('<a href="{}">{}</a>'.format(url, count))

    cwr_export_count.short_description = 'CWRs'
    cwr_export_count.admin_order_field = 'cwr_exports__count'

    def recording_count(self, obj):
        """Return the count of CWR exports with the link to the filtered
        changelist view for :class:`CWRExportAdmin`."""

        count = obj.recordings__count
        url = reverse('admin:music_publisher_recording_changelist')
        url += '?work__id__exact={}'.format(obj.id)
        return mark_safe('<a href="{}">{}</a>'.format(url, count))

    recording_count.short_description = 'Recordings'
    recording_count.admin_order_field = 'recordings__count'

    readonly_fields = (
        'writer_last_names', 'work_id', 'cwr_export_count')
    list_display = (
        'work_id', 'title', 'iswc', 'writer_last_names',
        'percentage_controlled', 'library_release',
        'recording_count', 'cwr_export_count')

    def get_queryset(self, request):
        """Optimized queryset for changelist view.
        """
        qs = super().get_queryset(request)
        qs = qs.prefetch_related('writerinwork_set')
        qs = qs.prefetch_related('writers')
        qs = qs.prefetch_related('library_release__library')
        qs = qs.annotate(models.Count('cwr_exports', distinct=True))
        qs = qs.annotate(models.Count('recordings', distinct=True))
        return qs

    class InCWRListFilter(admin.SimpleListFilter):
        """Custom list filter if work is included in any of CWR files.
        """

        title = 'In CWR'
        parameter_name = 'in_cwr'

        def lookups(self, request, model_admin):
            """Simple Yes/No filter
            """
            return (
                ('Y', 'Yes'),
                ('N', 'No'),
            )

        def queryset(self, request, queryset):
            """Filter if in any of CWR files.
            """
            if self.value() == 'Y':
                return queryset.exclude(cwr_exports__count=0)
            elif self.value() == 'N':
                return queryset.filter(cwr_exports__count=0)

    class ACKSocietyListFilter(admin.SimpleListFilter):
        """Custom list filter of societies from ACK files.
        """

        title = 'Acknowledgement society'
        parameter_name = 'ack_society'

        def lookups(self, request, model_admin):
            """Simple Yes/No filter
            """

            codes = WorkAcknowledgement.objects.order_by()
            codes = codes.values_list(
                'society_code', flat=True).distinct()
            return sorted(
                [(code, SOCIETY_DICT.get(code, code)) for code in codes],
                key=lambda code: code[1])

        def queryset(self, request, queryset):
            """Filter on society sending ACKs.
            """
            if self.value():
                return queryset.filter(
                    workacknowledgement__society_code=self.value()).distinct()
            return queryset

    class ACKStatusListFilter(admin.SimpleListFilter):
        """Custom list filter on ACK status.
        """

        title = 'Acknowledgement status'
        parameter_name = 'ack_status'

        def lookups(self, request, model_admin):
            """Simple Yes/No filter
            """
            return WorkAcknowledgement.TRANSACTION_STATUS_CHOICES

        def queryset(self, request, queryset):
            """Filter on ACK status.
            """
            if self.value():
                return queryset.filter(
                    workacknowledgement__status=self.value()).distinct()
            return queryset

    class HasISWCListFilter(admin.SimpleListFilter):
        """Custom list filter on the presence of ISWC.
        """

        title = 'Has ISWC'
        parameter_name = 'has_iswc'

        def lookups(self, request, model_admin):
            """Simple Yes/No filter
            """
            return (
                ('Y', 'Yes'),
                ('N', 'No'),
            )

        def queryset(self, request, queryset):
            """Filter on presence of :attr:`.iswc`.
            """
            if self.value() == 'Y':
                return queryset.exclude(iswc__isnull=True)
            elif self.value() == 'N':
                return queryset.filter(iswc__isnull=True)

    class HasRecordingListFilter(admin.SimpleListFilter):
        """Custom list filter on the presence of recordings.
        """
        title = 'Has Recordings'
        parameter_name = 'has_rec'

        def lookups(self, request, model_admin):
            """Simple Yes/No filter
            """
            return (
                ('Y', 'Yes'),
                ('N', 'No'),
            )

        def queryset(self, request, queryset):
            """Filter on presence of :class:`.models.Recording`.
            """
            if self.value() == 'Y':
                return queryset.exclude(recordings__count=0)
            elif self.value() == 'N':
                return queryset.filter(recordings__count=0)

    list_filter = (
        HasISWCListFilter,
        HasRecordingListFilter,
        ('library_release__library', admin.RelatedOnlyFieldListFilter),
        ('library_release', admin.RelatedOnlyFieldListFilter),
        ('writers', admin.RelatedOnlyFieldListFilter),
        'last_change',
        InCWRListFilter,
        ACKSocietyListFilter,
        ACKStatusListFilter,
    )

    search_fields = (
        'title', 'alternatetitle__title', '^iswc', '^id', '^_work_id',
        'recordings__recording_title', 'recordings__version_title',
        '^recordings__isrc', 'writerinwork__writer__last_name')

    def get_search_results(self, request, queryset, search_term):
        """Deal with the situation term is work ID.
        """
        if search_term.isnumeric():
            search_term = search_term.lstrip('0')
        return super().get_search_results(request, queryset, search_term)

    fieldsets = (
        (None, {
            'fields': (
                'work_id',
                ('title', 'iswc'),
                ('original_title', 'version_type')
            )
        }),
        ('Library (Production music only)', {
            'fields': (
                ('library_release',),
            )
        }),
    )

    autocomplete_fields = ('library_release',)

    def save_model(self, request, obj, form, *args, **kwargs):
        """Set last_change if the work form has changed."""
        if form.changed_data:
            obj.last_change = now()
        super().save_model(request, obj, form, *args, **kwargs)

    def save_formset(self, request, form, formset, change):
        """Set last_change for the work if any of the inline forms has changed.
        """
        save_instance = False
        for form in formset:
            if form.changed_data:
                save_instance = True
        super().save_formset(request, form, formset, change)
        if save_instance:
            formset.instance.last_change = now()
            formset.instance.save()

    def create_cwr(self, request, qs):
        """Batch action that redirects to the add view for
        :class:`CWRExportAdmin` with selected works.
        """
        url = reverse('admin:music_publisher_cwrexport_add')
        work_ids = qs.values_list('id', flat=True)
        view = CWRExportAdmin(CWRExport, admin.site).add_view(
            request, url, work_ids=work_ids)
        return view

    create_cwr.short_description = 'Create CWR from selected works.'

    def create_json(self, request, qs):
        """Batch action that downloads a JSON file containing selected works.

        Returns:
            JsonResponse: JSON file with selected works
        """

        Work.persist_work_ids(qs)
        j = Work.objects.get_dict(qs)

        response = JsonResponse(j, json_dumps_params={'indent': 4})
        name = '{}-works-{}'.format(
            settings.PUBLISHER_CODE, datetime.now().toordinal())
        cd = 'attachment; filename="{}.json"'.format(name)
        response['Content-Disposition'] = cd
        return response

    create_json.short_description = \
        'Export selected works (JSON).'

    def get_labels_for_csv(self, works):
        """Return the list of labels for the CSV file."""
        labels = [
            'Work ID',
            'Work Title', 'ISWC', 'Original Title', 'Library', 'CD Identifier',
        ]
        alt_title_max = 1
        writer_max = 1
        artist_max = 1
        for work in works:
            alt_title_max = max(alt_title_max, len(work.get('other_titles')))
            writer_max = max(writer_max, len(work.get('writers')))
            artist_max = max(artist_max, len(work.get('performing_artists')))
        for i in range(alt_title_max):
            labels.append('Alt Title {}'.format(i))
        for i in range(writer_max):
            labels.append('Writer {} Last'.format(i))
            labels.append('Writer {} First'.format(i))
            labels.append('Writer {} IPI'.format(i))
            labels.append('Writer {} PRO'.format(i))
            labels.append('Writer {} Role'.format(i))
            labels.append('Writer {} Share'.format(i))
            labels.append('Writer {} Controlled'.format(i))
            labels.append('Writer {} SAAN'.format(i))
        for i in range(artist_max):
            labels.append('Artist {} Last'.format(i))
            labels.append('Artist {} First'.format(i))
            labels.append('Artist {} ISNI'.format(i))
        return labels

    def get_rows_for_csv(self, works):
        """Return rows for the CSV file, including the header."""

        class EchoWriter:
            """Class with write() method just echoing values."""
            def write(self, value):
                return value

        pseudo_buffer = EchoWriter()
        labels = self.get_labels_for_csv(works)
        writer = DictWriter(pseudo_buffer, labels)
        header = dict(zip(labels, labels))
        yield writer.writerow(header)
        # yield writer.writeheader()  # In Python 3.8
        for work in works:
            ows = work.get('original_works')
            row = {
                'Work ID': work['code'],
                'Work Title': work['work_title'],
                'ISWC': work.get('iswc', ''),
            }
            if ows:
                row['Original Title'] = ows[0]['work_title']
            origin = work.get('origin')
            if origin:
                row['Library'] = origin['library']['name']
                row['CD Identifier'] = origin['cd_identifier']
            for i, alt in enumerate(work['other_titles']):
                row['Alt Title {}'.format(i)] = alt['title']
            for i, wiw in enumerate(work['writers']):
                w = wiw.get('writer') or {}
                row['Writer {} Last'.format(i)] = w.get('last_name', '')
                row['Writer {} First'.format(i)] = w.get('first_name', '')
                row['Writer {} IPI'.format(i)] = w.get('ipi_name_number', '')
                role = wiw.get('writer_role', {})
                if role:
                    row['Writer {} Role'.format(i)] = '{} - {}'.format(
                        role['code'], role['name'])
                row['Writer {} Share'.format(i)] = wiw.get('relative_share')
                for aff in w.get('affiliations', []):
                    if aff['affiliation_type']['code'] == 'PR':
                        pro = aff['organization']
                        row['Writer {} PRO'.format(i)] = '{} - {}'.format(
                        pro['code'], pro['name'])
                ops = wiw.get('original_publishers')
                if ops:
                    op = ops[0]
                    agreement = op.get('agreement')
                    saan = agreement.get('recipient_agreement_number', '')
                    row['Writer {} SAAN'.format(i)] = saan
                    agreement_type = agreement['agreement_type']['code']
                    if agreement_type == 'OG':
                        controlled = 'General Agreement'
                    else:
                        controlled = 'Yes'
                else:
                    controlled = 'No'
                row['Writer {} Controlled'.format(i)] = controlled
            for i, aiw in enumerate(work['performing_artists']):
                artist = aiw.get('artist')
                row['Artist {} Last'.format(i)] = artist.get('last_name', '')
                row['Artist {} First'.format(i)] = artist.get('first_name', '')
                row['Artist {} ISNI'.format(i)] = artist.get('isni', '')
            yield writer.writerow(row)

    def create_csv(self, request, qs):
        """Batch action that downloads a CSV file containing selected works.

        Returns:
            JsonResponse: JSON file with selected works
        """

        Work.persist_work_ids(qs)

        j = Work.objects.get_dict(qs)
        works = j.get('works', [])
        response = HttpResponse(
            self.get_rows_for_csv(works),
            content_type="text/csv")
        name = '{}{}'.format(
            settings.PUBLISHER_CODE, datetime.now().toordinal())
        cd = 'attachment; filename="{}.csv"'.format(name)
        response['Content-Disposition'] = cd
        return response

    create_csv.short_description = \
        'Export selected works (CSV).'

    actions = (create_cwr, create_json, create_csv)

    def get_actions(self, request):
        """Custom action disabling the default ``delete_selected``."""
        actions = super().get_actions(request)
        if not settings.PUBLISHER_CODE:
            del actions['create_cwr']
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    def get_inline_instances(self, request, obj=None):
        """Limit inlines in popups."""
        instances = super().get_inline_instances(request)
        if IS_POPUP_VAR in request.GET or IS_POPUP_VAR in request.POST:
            return [i for i in instances if type(i) not in [
                RecordingInline, WorkAcknowledgementInline
            ]]
        return instances


@admin.register(Recording)
class RecordingAdmin(MusicPublisherAdmin):
    """Admin interface for :class:`.models.Recording`."""

    actions = None
    list_display = (
        'recording_id', 'title', 'isrc', 'work_link', 'artist_link',
        'label_link')

    class HasISRCListFilter(admin.SimpleListFilter):
        """Custom list filter on the presence of ISRC.
        """

        title = 'Has ISRC'
        parameter_name = 'has_isrc'

        def lookups(self, request, model_admin):
            """Simple Yes/No filter
            """
            return (
                ('Y', 'Yes'),
                ('N', 'No'),
            )

        def queryset(self, request, queryset):
            """Filter on presence of :attr:`.iswc`.
            """
            if self.value() == 'Y':
                return queryset.exclude(isrc__isnull=True)
            elif self.value() == 'N':
                return queryset.filter(isrc__isnull=True)

    list_filter = (HasISRCListFilter, 'artist', 'record_label')
    search_fields = (
        'work__title', 'recording_title', 'version_title', 'isrc')
    autocomplete_fields = ('artist', 'work', 'record_label')
    readonly_fields = (
        'complete_recording_title', 'complete_version_title', 'title',
        'work_link', 'artist_link', 'label_link')
    fieldsets = (
        (None, {
            'fields': (
                'work',
                (
                    'recording_title', 'recording_title_suffix',
                    'complete_recording_title'),
                (
                    'version_title', 'version_title_suffix',
                    'complete_version_title'),
                ('isrc', 'record_label', 'artist'),
                ('duration', 'release_date'),
            ),
        }),
    )
    formfield_overrides = {
        models.TimeField: {'widget': forms.TimeInput},
    }

    def get_queryset(self, request):
        """Optimized query regarding work name
        """
        qs = super().get_queryset(request)
        qs = qs.prefetch_related('work__writers')
        qs = qs.prefetch_related('artist')
        qs = qs.prefetch_related('record_label')
        return qs

    def title(self, obj):
        """Return the recording title, which is not the necessarily the
        title field."""
        return str(obj)

    def work_link(self, obj):
        """Link to the work the recording is based on."""
        url = reverse('admin:music_publisher_work_change', args=[obj.work.id])
        link = '<a href="{}">{}</a>'.format(url, obj.work)
        return mark_safe(link)

    work_link.short_description = 'Work'
    work_link.admin_order_field = 'work__id'

    def artist_link(self, obj):
        """Link to the recording artist."""
        if not obj.artist:
            return None
        url = reverse(
            'admin:music_publisher_artist_change', args=[obj.artist.id])
        link = '<a href="{}">{}</a>'.format(url, obj.artist)
        return mark_safe(link)

    artist_link.short_description = 'Recording Artist'
    artist_link.admin_order_field = 'artist'

    def label_link(self, obj):
        """Link to the recording label."""
        if not obj.record_label:
            return None
        url = reverse(
            'admin:music_publisher_label_change', args=[obj.record_label.id])
        link = '<a href="{}">{}</a>'.format(url, obj.record_label)
        return mark_safe(link)

    label_link.short_description = 'Record Label'
    label_link.admin_order_field = 'record_label'


@admin.register(CWRExport)
class CWRExportAdmin(admin.ModelAdmin):
    """Admin interface for :class:`.models.CWRExport`.
    """

    actions = None

    def work_count(self, obj):
        """Return the work count from the database field, or count them.
        (dealing with legacy)"""

        count = obj.works__count

        url = reverse('admin:music_publisher_work_changelist')
        url += '?cwr_exports__id__exact={}'.format(obj.id)
        return mark_safe('<a href="{}">{}</a>'.format(url, count))

    work_count.short_description = 'Works'
    work_count.admin_order_field = 'works__count'

    def get_preview(self, obj):
        """Get CWR preview.

        If you are using highlighing, then override this method."""

        return obj.cwr

    def view_link(self, obj):
        """Link to the CWR preview."""
        if obj.cwr:
            url = reverse(
                'admin:music_publisher_cwrexport_change', args=(obj.id,))
            url += '?preview=true'
            return mark_safe(
                '<a href="{}" target="_blank">View CWR</a>'.format(url))

    def download_link(self, obj):
        """Link for downloading CWR file."""
        if obj.cwr:
            url = reverse(
                'admin:music_publisher_cwrexport_change', args=(obj.id,))
            url += '?download=true'
            return mark_safe('<a href="{}">Download</a>'.format(url))

    def get_queryset(self, request):
        """Optimized query with count of works in the export.
        """
        qs = super().get_queryset(request)
        qs = qs.annotate(models.Count('works'))
        return qs

    autocomplete_fields = ('works',)
    list_display = (
        'filename', 'nwr_rev', 'work_count', 'view_link',
        'download_link', 'description')
    list_editable = ('description',)

    list_filter = ('nwr_rev', 'year')
    search_fields = ('works__title',)

    def get_readonly_fields(self, request, obj=None):
        """Read-only fields differ if CWR has been completed."""
        if obj and obj.cwr:
            return (
                'nwr_rev', 'description', 'works', 'filename', 'view_link',
                'download_link')
        else:
            return ()

    def get_fields(self, request, obj=None):
        """Shown fields differ if CWR has been completed."""
        if obj and obj.cwr:
            return (
                'nwr_rev', 'description', 'works', 'filename', 'view_link',
                'download_link')
        else:
            return ('nwr_rev', 'description', 'works')

    def has_add_permission(self, request):
        """Return false if CWR delivery code is not present."""
        if not settings.PUBLISHER_CODE:
            return False
        return super().has_add_permission(request)

    def has_delete_permission(self, request, obj=None):
        """If CWR has been created, it can no longer be deleted, as it may
        have been sent. This may change once the delivery is automated."""
        if obj and obj.cwr:
            return False
        return super().has_delete_permission(request, obj)

    def has_change_permission(self, request, obj=None):
        """If object exists, it can only be edited in changelist."""
        if not settings.PUBLISHER_CODE:
            return False
        if obj:
            return False
        return super().has_delete_permission(request, obj)

    def get_form(self, request, obj=None, **kwargs):
        """Set initial values for work IDs."""
        form = super().get_form(request, obj, **kwargs)
        if hasattr(self, 'work_ids'):
            form.base_fields['works'].initial = self.work_ids
        return form

    def add_view(self, request, form_url='', extra_context=None,
                 work_ids=None):
        """Added work_ids as default for wizard from
        :meth:`WorkAdmin.create_cwr`."""
        if work_ids:
            self.work_ids = work_ids
            request.method = 'GET'
        return super().add_view(request, form_url, extra_context)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        """Normal change view with two sub-views defined by GET parameters:

        Parameters:
            preview: that returns the preview of CWR file,
            download: that downloads the CWR file."""
        obj = get_object_or_404(CWRExport, pk=object_id)
        if 'preview' in request.GET:
            cwr = self.get_preview(obj)
            return render(request, 'raw_cwr.html', {
                **self.admin_site.each_context(request),
                'version': obj.version,
                'lines': cwr.split('\r\n'),
                'title': obj.filename
            })
        elif 'download' in request.GET:
            response = HttpResponse(content_type='application/zip')
            zip_file = zipfile.ZipFile(
                response, 'w', zipfile.ZIP_DEFLATED)
            zip_file.writestr(obj.filename, obj.cwr.encode().decode('latin1'))
            if obj.version in ['30', '31']:
                cd = 'attachment; filename="{}.zip"'.format(
                    obj.filename.replace('.', '_'))
            else:
                cd = 'attachment; filename="{}"'.format(
                    obj.filename.replace(
                        '.V21', '.zip'
                    ).replace('.V22', '.zip'))
            response['Content-Disposition'] = cd
            return response

        extra_context = {
            'show_save': False,
        }
        if obj.cwr:
            extra_context.update({
                'save_as': False,
                'show_save_and_continue': False,
                'show_delete': False,
            })
        return super().change_view(
            request, object_id, form_url='', extra_context=extra_context)

    def save_related(self, request, form, formsets, change):
        """:meth:`save_model` passes the main object, which is needed to fetch
            CWR from the external service, but only after related objects are
            saved.
        """
        super().save_related(request, form, formsets, change)
        form.instance.create_cwr()


class ACKImportForm(ModelForm):
    """Form used for CWR acknowledgement imports.

    Attributes:
        acknowledgement_file (FileField): Field for file upload
    """

    class Meta:
        model = ACKImport
        fields = ('acknowledgement_file', 'import_iswcs')

    acknowledgement_file = FileField()
    import_iswcs = BooleanField(label='Import ISWCs if present', required=False)

    RE_HDR_21 = re.compile(
        r'^HDR(?:SO|AA)([ \d]{9})(.{45})01\.10(\d{8})\d{6}(\d{8})')

    RE_HDR_30 = re.compile(
        r'^HDR(?:SO|AA)(.{4})(.{45})(\d{8})\d{6}(\d{8}).{15}3\.0000')

    def clean(self):
        """Perform usual clean, then process the file, returning the content
            field as if it was the TextField."""
        super().clean()
        cd = self.cleaned_data
        ack = cd.get('acknowledgement_file')
        filename = ack.name
        if not (len(filename) in [18, 19] and filename[-4:].upper() == '.V21'):
            raise ValidationError('Wrong file name format.')
        self.cleaned_data['filename'] = filename
        content = ack.file.read().decode('latin1')
        match = re.match(self.RE_HDR_21, content)
        if not match:
            match = re.match(self.RE_HDR_30, content)
        if not match:
            raise ValidationError('Incorrect CWR header')
        code, name, date1, date2 = match.groups()
        self.cleaned_data['society_code'] = code.strip().lstrip('0')
        self.cleaned_data['society_name'] = name.strip()
        self.cleaned_data['date'] = datetime.strptime(
            max([date1, date2]), '%Y%m%d').date()
        self.cleaned_data['acknowledgement_file'] = content


class AdminWithReport(admin.ModelAdmin):
    """The parent class for all admin classes with a report field."""
    def print_report(self, obj):
        """Mark report as HTML-safe."""
        return mark_safe(obj.report)
    print_report.short_description = 'Report'


@admin.register(ACKImport)
class ACKImportAdmin(AdminWithReport):
    """Admin interface for :class:`.models.ACKImport`.
    """

    def get_form(self, request, obj=None, **kwargs):
        """Returns a custom form for new objects, default one for changes.
        """
        if obj is None:
            return ACKImportForm
        return super().get_form(request, obj, **kwargs)

    list_display = (
        'filename', 'society_code', 'society_name', 'date', 'view_link')
    list_filter = ('society_code', 'society_name')
    fields = readonly_fields = (
        'filename', 'society_code', 'society_name', 'date', 'print_report',
        'view_link')

    add_fields = ('acknowledgement_file', 'import_iswcs')

    def get_fields(self, request, obj=None):
        """Return different fields for add vs change.
        """
        if obj:
            return self.fields
        return self.add_fields

    RE_ACK_21 = re.compile(re.compile(
        r'(?<=\n)ACK.{43}(NWR|REV).{60}(.{20})(.{20})(.{8})(.{2})(.*?)(?=^ACK|^GRT)', re.S | re.M))
    RE_ACK_30 = re.compile(re.compile(
        r'(?<=\n)ACK.{43}(WRK).{60}(.{20})(.{20}){20}(.{8})(.{2})(.*?)(?=^ACK|^GRT)', re.S | re.M))

    def process(self, request, society_code, file_content, import_iswcs=False):
        """Create appropriate WorkAcknowledgement objects, without duplicates.

        Big part of this code should be moved to the model, left here because
        messaging is simpler.
        """

        if import_iswcs:
            validator = CWRFieldValidator('iswc')

        unknown_work_ids = []
        existing_work_ids = []
        report = ''
        if file_content[59:64] == '01.10':
            pattern = self.RE_ACK_21
        else:
            pattern = self.RE_ACK_30
        for x in re.findall(pattern, file_content):
            tt, work_id, remote_work_id, dat, status, rest = x
            if import_iswcs and rest:
                header = rest.strip().split('\n')[0]
                iswc = header[95:106].strip() or None
                if iswc:
                    try:
                        validator(iswc)
                    except ValidationError:
                        iswc = None
            # work ID is numeric with an optional string
            work_id = work_id.strip()
            remote_work_id = remote_work_id.strip()
            dat = datetime.strptime(dat, '%Y%m%d').date()
            work = Work.objects.filter(_work_id=work_id).first()
            if not work:
                unknown_work_ids.append(work_id)
                continue
            if import_iswcs and iswc:
                if work.iswc:
                    if work.iswc != iswc:
                        raise ValidationError(
                            'A different ISWC exists for work {}: {} vs {}.'
                            ''.format(work, work.iswc, iswc))
                else:
                    work.iswc = iswc
                    work.last_change = now()
                    from django.contrib.admin.models import CHANGE, LogEntry
                    LogEntry.objects.log_action(
                        request.user.id,
                        admin.options.get_content_type_for_model(work).id,
                        work.id, str(work), CHANGE,
                        'ISWC imported from ACK file.')
                    work.save()
            wa, c = WorkAcknowledgement.objects.get_or_create(
                work_id=work.id,
                remote_work_id=remote_work_id,
                society_code=society_code,
                date=dat,
                status=status)
            if not c:
                existing_work_ids.append(str(work_id))
                continue
            url = reverse(
                'admin:music_publisher_work_change', args=(work.id,))
            report += '<a href="{}">{}</a> {} &mdash; {}<br/>\n'.format(
                url, work.work_id, work.title, wa.get_status_display())
        if unknown_work_ids:
            messages.add_message(
                request, messages.ERROR,
                'Unknown work IDs: {}'.format(', '.join(unknown_work_ids)))
        if existing_work_ids:
            messages.add_message(
                request, messages.ERROR,
                'Data already exists for some or all works. '
                'Affected work IDs: {}'.format(', '.join(existing_work_ids)))
        return report

    def save_model(self, request, obj, form, change):
        """Custom save_model, it ignores changes, validates the form for new
            instances, if valid, it processes the file and, upon success,
            calls ``super().save_model``."""

        if form.is_valid():
            cd = form.cleaned_data
            obj.filename = cd['filename']
            obj.society_code = cd['society_code']
            obj.society_name = cd['society_name']
            obj.date = cd['date']
            # TODO move process() to model, and handle messages here
            obj.report = self.process(
                request, obj.society_code, cd['acknowledgement_file'],
                cd['import_iswcs'])
            obj.cwr = cd['acknowledgement_file']
            super().save_model(request, obj, form, change)

    def has_add_permission(self, request):
        """Return false if CWR delivery code is not present."""
        if not settings.PUBLISHER_CODE:
            return False
        return super().has_add_permission(request)

    def has_delete_permission(self, request, obj=None, *args, **kwargs):
        """Deleting ACK imports is a really bad idea.
        """
        return False

    def has_change_permission(self, request, obj=None):
        """Deleting this would make no sense, since the data is processed."""
        return False

    def get_preview(self, obj):
        """Get CWR preview.

        If you are using highlighing, then override this method."""

        return obj.cwr

    def view_link(self, obj):
        """Link to CWR ACK preview."""
        if obj.cwr:
            url = reverse(
                'admin:music_publisher_ackimport_change', args=(obj.id,))
            url += '?preview=true'
            return mark_safe(
                '<a href="{}" target="_blank">View CWR</a>'.format(url))

    def change_view(self, request, object_id, form_url='', extra_context=None):
        """Normal change view with a sub-view defined by GET parameters:

        Parameters:
            preview: that returns the preview of CWR file."""
        obj = get_object_or_404(ACKImport, pk=object_id)
        if 'preview' in request.GET:
            cwr = self.get_preview(obj)
            if (cwr[59:64] == '01.10'):
                version = '21'
            else:
                version = '30'  # never seen one yet
            try:
                return render(request, 'raw_cwr.html', {
                    **self.admin_site.each_context(request),
                    'version': version,
                    'lines': cwr.split('\n'),
                    'title': obj.filename
                })
            except Exception:  # Parsing user garbage, could be anything
                return render(request, 'raw_cwr.html', {
                    **self.admin_site.each_context(request),
                    'version': '',
                    'lines': cwr.split('\n'),
                    'title': obj.filename
                })

        return super().change_view(
            request, object_id, form_url='', extra_context=extra_context)


class DataImportForm(ModelForm):
    """Form used for data imports.

    Attributes:
        data_file (FileField): Field for file upload
    """

    class Meta:
        model = ACKImport
        fields = ('data_file',)

    data_file = FileField()

    def clean(self):
        """
        This is the actual import process, if all goes well,
        the report is saved.

        Raises:
            ValidationError
        """
        super().clean()

        from .data_import import DataImporter
        from io import TextIOWrapper

        cd = self.cleaned_data
        f = cd.get('data_file')
        report = ''
        try:
            importer = DataImporter(TextIOWrapper(f), self.user)
            for work in importer.run():
                url = reverse(
                    'admin:music_publisher_work_change', args=(work.id,))
                report += '<a href="{}">{}</a> {}<br/>\n'.format(
                    url, work.work_id, work.title)
        except Exception as e:  # user garbage, too many possibilities
            raise ValidationError(str(e))
        self.cleaned_data['report'] = report


@admin.register(DataImport)
class DataImportAdmin(AdminWithReport):
    """Data import from CSV files.

    Only the interface is here, the whole logic is in
    :mod:`.data_import`.
    """

    form = DataImportForm

    list_display = ('filename', 'date')
    fields = readonly_fields = ('filename', 'date', 'print_report')

    add_fields = ('data_file',)

    def get_fields(self, request, obj=None):
        """Return different fields for add vs change.
        """
        if obj:
            return self.fields
        return self.add_fields

    def has_delete_permission(self, request, obj=None, *args, **kwargs):
        """Deleting data imports is a really bad idea.
        """
        return False

    def has_change_permission(self, request, obj=None):
        """Deleting this would make no sense, since the data is processed."""
        return False

    def get_form(self, request, obj=None, change=False, **kwargs):
        form = super().get_form(request, obj, change, **kwargs)
        form.user = request.user
        return form

    def save_model(self, request, obj, form, change):
        """Custom save_model, it ignores changes, validates the form for new
            instances, if valid, it processes the file and, upon success,
            calls ``super().save_model``."""

        if form.is_valid():
            cd = form.cleaned_data
            f = cd['data_file']
            obj.filename = f.name
            obj.report = cd['report']
            super().save_model(request, obj, form, change)
