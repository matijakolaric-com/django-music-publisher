"""Interface for :mod:`music_publisher` app.

Please note that this is the only interface.

Attributes:
    IS_POPUP_VAR (bool): :attr:`django.contrib.admin.options.IS_POPUP_VAR`
"""
from collections import OrderedDict
from datetime import datetime
from decimal import Decimal
import re

from django import forms
from django.conf import settings
from django.contrib import admin, messages
from django.core.exceptions import ValidationError
from django.db import models
from django.forms import FileField, ModelForm
from django.forms.models import BaseInlineFormSet
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils.html import mark_safe
from django.utils.timezone import now

from .base import SOCIETIES
from .models import (
    ACKImport, AlternateTitle, Artist, ArtistInWork, CommercialRelease,
    CWRExport, Label, Library, LibraryRelease, Recording, Release, Track, Work,
    WorkAcknowledgement, Writer, WriterInWork)


SETTINGS = settings.MUSIC_PUBLISHER_SETTINGS
IS_POPUP_VAR = admin.options.IS_POPUP_VAR


class MusicPublisherAdmin(admin.ModelAdmin):
    """Custom Admin class, easily extendable.

    Should only be used for admin classes for top-level models."""

    save_as = True


class ArtistInWorkInline(admin.TabularInline):
    """Inline interface for :class:`.models.ArtistInWork`.
    """
    autocomplete_fields = ('artist', 'work')
    model = ArtistInWork
    extra = 0
    verbose_name_plural = \
        'Performing Artists (not mentioned in "recordings" section)'


class RecordingInline(admin.StackedInline):
    """Inline interface for :class:`.models.Recording`,
        used in :class:`WorkAdmin` and :class:`ArtistAdmin`.
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
                ('isrc', 'artist', 'record_label'),
                ('duration', 'release_date'),
                # ('album_cd', )
            ),
        }),
    )
    formfield_overrides = {
        models.TimeField: {'widget': forms.TimeInput},
    }
    verbose_name_plural = 'Recordings (with recording artists and labels)'
    model = Recording
    extra = 0

    def complete_recording_title(selfSelf, obj):
        return obj.complete_recording_title

    def complete_version_title(selfSelf, obj):
        return obj.complete_version_title


@admin.register(Artist)
class ArtistAdmin(MusicPublisherAdmin):
    """Admin interface for :class:`.models.Artist`.
    """

    list_display = ('last_or_band', 'first_name', 'isni')
    search_fields = ('last_name', 'isni',)
    inlines = [RecordingInline, ArtistInWorkInline]
    fieldsets = (
        ('Name', {
            'fields': (
                ('first_name', 'last_name'),)}),
        ('ISNI', {
            'fields': (
                'isni',),
        }),
    )

    def get_inline_instances(self, request, obj=None):
        """Limit inlines in popups."""
        if IS_POPUP_VAR in request.GET or IS_POPUP_VAR in request.POST:
            return []
        return super().get_inline_instances(request)

    def last_or_band(self, obj):
        """Placeholder for :attr:`.models.Artist.last_name`."""
        return obj.last_name

    last_or_band.short_description = 'Last or band name'
    last_or_band.admin_order_field = 'last_name'

    actions = None

    def save_model(self, request, obj, form, *args, **kwargs):
        """Save, then update ``last_change`` of the corresponding works.
        """
        super().save_model(request, obj, form, *args, **kwargs)
        if form.changed_data:
            qs = Work.objects.filter(artistinwork__artist=obj)
            qs.update(last_change=now())


@admin.register(Label)
class LabelAdmin(MusicPublisherAdmin):
    search_fields = ('name', )


@admin.register(Library)
class LibraryAdmin(MusicPublisherAdmin):
    search_fields = ('name', )


class TrackInline(admin.TabularInline):
    model = Track
    autocomplete_fields = ('release', 'recording')
    extra = 0


@admin.register(Release)
class ReleaseAdmin(MusicPublisherAdmin):
    """Admin interface for :class:`.models.Release`.
    """

    fieldsets = (
        ('Library', {
            'fields': (
                ('cd_identifier', 'library'),)
        }),
        ('Release (album)', {
            'fields': (
                ('release_title', 'release_label'),
                ('ean', 'release_date'))
        }),
    )


    list_display = (
        '__str__',
    )

    search_fields = ('release_title', '^cd_identifier')
    actions = None

    def has_module_permission(self, request):
        return False

    def has_add_permission(self, request):
        return False


class LibraryReleaseForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['cd_identifier'].required = True
        self.fields['library'].required = True


@admin.register(LibraryRelease)
class LibraryReleaseAdmin(MusicPublisherAdmin):
    """Admin interface for :class:`.models.AlbumCD`.
    """

    form = LibraryReleaseForm
    inlines = [TrackInline]
    autocomplete_fields = ('release_label', 'library')

    def get_fieldsets(self, request, obj=None):
        """Fields depend on settings.
        """
        return ReleaseAdmin.get_fieldsets(self, request, obj)

    list_display = (
        'cd_identifier',
        'library',
        'release_title',
        'release_label'
    )

    list_filter = ('release_label', 'library')
    search_fields = ('release_title', '^cd_identifier')
    actions = None

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
            qs = Work.objects.filter(recordings__album_cd=obj)
            qs.update(last_change=now())


@admin.register(CommercialRelease)
class CommercialReleaseAdmin(MusicPublisherAdmin):
    """Admin interface for :class:`.models.AlbumCD`.
    """

    inlines = [TrackInline]
    autocomplete_fields = ('release_label',)

    list_display = (
        'release_title',
        'release_label'
    )

    list_filter = ('release_label',)
    search_fields = ('release_title',)
    actions = None

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



@admin.register(Writer)
class WriterAdmin(MusicPublisherAdmin):
    """Interface for :class:`.models.Writer`.
    """

    list_display = ('last_name', 'first_name', 'ipi_name', 'pr_society',
                    '_can_be_controlled', 'generally_controlled')

    list_filter = ('_can_be_controlled', 'generally_controlled', 'pr_society')
    search_fields = ('last_name', 'ipi_name')
    readonly_fields = ('_can_be_controlled', 'original_publisher')
    fieldsets = (
        ('Name', {
            'fields': (
                ('first_name', 'last_name'),)}),
        ('IPI', {
            'fields': (
                ('ipi_name', 'ipi_base'),
                'pr_society'),
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
    def original_publisher(obj):
        """Return the original publisher.

        This makes sense only in the US context."""

        if obj.generally_controlled and obj.pr_society:
            return obj.get_publisher_dict().get('publisher_name')
        return ''

    def save_model(self, request, obj, form, *args, **kwargs):
        """Perform normal save_model, then update last_change of
        all connected works."""
        super().save_model(request, obj, form, *args, **kwargs)
        if form.changed_data:
            qs = Work.objects.filter(writerinwork__writer=obj)
            qs.update(last_change=now())


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
                if work_title_len + title_suffix_len > 59:  # 60 - 1 for space
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
    verbose_name_plural = 'Alternative titles (not mentioned in "recordings" section)'
    fields = ('title', 'suffix', 'complete_alt_title')

    def complete_alt_title(self, obj):
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
                    'relative_share', 'Sum of relative shares must be 100%.')
            raise ValidationError('Sum of relative shares must be 100%.')
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

        Please note that normal users should only have a 'view' permission.
    """

    model = WorkAcknowledgement
    extra = 0
    fields = ('date', 'society_code', 'remote_work_id', 'status')


class WorkForm(forms.ModelForm):
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
        RecordingInline, AlternateTitleInline,
        ArtistInWorkInline,
        WorkAcknowledgementInline)

    def writer_last_names(self, obj):
        """This is a standard way how writers are shown in other apps."""

        return ' / '.join(
            writer.last_name.upper() for writer in set(obj.writers.all()))

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
        return obj.work_id

    work_id.short_description = 'Work ID'
    work_id.admin_order_field = 'id'

    def library_release(self, obj):
        if not (hasattr(obj, 'recording') and obj.recording):
            return None
        return obj.recording.album_cd

    library_release.short_description = 'Album / Library CD'
    library_release.admin_order_field = 'library_release__name'

    # def isrcs(self, obj):
    #     return [r.isrc for r in obj.recordings.all()]
    #
    # isrcs.short_description = 'ISRCs'
    # isrcs.admin_order_field = 'recordings__isrc'

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

    def duration(self, obj):
        if not (hasattr(obj, 'recording') and
                obj.recording and obj.recording.duration):
            return None
        return obj.recording.duration.strftime('%H:%M:%S')

    duration.admin_order_field = 'recordings__duration'

    readonly_fields = (
        'writer_last_names', 'work_id', 'cwr_export_count')
    list_display = (
        'work_id', 'title', 'iswc', 'writer_last_names',
        'percentage_controlled', 'duration', 'library_release',
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
            SDICT = dict()
            for key, value in SOCIETIES:
                key1 = key.lstrip('0')
                key2 = key.rjust(3, '0')
                SDICT[key1] = value
                SDICT[key2] = value
            codes = WorkAcknowledgement.objects.values_list(
                'society_code', flat=True).distinct()
            return [(code, SDICT.get(code, code)) for code in codes]

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
        """Custom list filter on the presence of first recording.
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
                return queryset.exclude(recordings__isnull=True)
            elif self.value() == 'N':
                return queryset.filter(recordings__isnull=True)

    list_filter = (
        HasISWCListFilter,
        HasRecordingListFilter,
        ('library_release', admin.RelatedOnlyFieldListFilter),
        'last_change',
        InCWRListFilter,
        ACKSocietyListFilter,
        ACKStatusListFilter,
    )

    search_fields = (
        'title', 'alternatetitle__title', 'writerinwork__writer__last_name',
        '^iswc', '^id')

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
                )}),
        ('Library (Production music only)', {
            'fields': (
                ('library_release',),
            )}),
    )

    autocomplete_fields = ('library_release',)

    def save_model(self, request, obj, form, *args, **kwargs):
        if form.changed_data:
            obj.last_change = now()
        super().save_model(request, obj, form, *args, **kwargs)

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

    def create_json(self, request, qs, normalize=False):
        """Batch action that downloads a JSON file containing selected works.

        Returns:
            JsonResponse: JSON file with selected works
        """

        works = OrderedDict()
        affiliation_types = {}
        agreement_types = {}
        artists = {}
        labels = {}
        libraries = {}
        organizations = {}
        territories = {}
        writers = {}
        publishers = {}
        qs = qs.prefetch_related('alternatetitle_set')
        qs = qs.prefetch_related('writerinwork_set__writer')
        qs = qs.prefetch_related('artistinwork_set__artist')
        qs = qs.prefetch_related('recordings__record_label')
        qs = qs.prefetch_related('recordings__artist')
        qs = qs.prefetch_related('recordings__tracks__release__library')
        qs = qs.prefetch_related('recordings__tracks__release__release_label')
        for work in qs:
            work_data = work.get_dict(normalize=normalize)
            key = next(iter(work_data))
            j = work_data[key]
            affiliation_types.update(j.pop('affiliation_types'))
            agreement_types.update(j.pop('agreement_types'))
            writers.update(j.pop('writers'))
            if normalize:
                publishers.update(j.pop('publishers'))
            artists.update(j.pop('artists', {}))
            labels.update(j.pop('labels', {}))
            organizations.update(j.pop('organizations', {}))
            territories.update(j.pop('territories', {}), )
            libraries.update(j.pop('libraries', {}), )
            works[key] = j
        if normalize:
            j = {
                'affiliation_types': affiliation_types,
                'agreement_types': agreement_types,
                'artists': artists,
                'labels': labels,
                'libraries': libraries,
                'organizations': organizations,
                'territories': territories,
                'publishers': publishers,
                'writers': writers,
                'works': works,
            }
        else:
            j = {
                'works': works,
            }

        response = JsonResponse(j, json_dumps_params={'indent': 4})
        name = '{}{}'.format(
            SETTINGS.get('work_id_prefix', ''), datetime.now().toordinal())
        cd = 'attachment; filename="{}.json"'.format(name)
        response['Content-Disposition'] = cd
        return response

    create_json.short_description = \
        'Export selected works (JSON).'

    def create_normalized_json(self, request, qs):
        return self.create_json(request, qs, normalize=True)

    create_normalized_json.short_description = \
        'Export selected works (normalized JSON).'

    actions = (create_cwr, create_json, create_normalized_json)

    def get_actions(self, request):
        """Custom action disabling the default ``delete_selected``."""
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    def get_inline_instances(self, request, obj=None):
        """Limit inlines in popups."""
        instances = super().get_inline_instances(request)
        if IS_POPUP_VAR in request.GET or IS_POPUP_VAR in request.POST:
            return [i for i in instances if type(i) not in [
                ArtistInWorkInline, RecordingInline, WorkAcknowledgementInline
            ]]
        return instances


@admin.register(Recording)
class RecordingAdmin(MusicPublisherAdmin):
    inlines = [TrackInline]
    list_display = (
        'recording_id', 'title', 'isrc', 'work_link', 'artist_link',
        'record_label')

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
    search_fields = ('work__title', 'recording_title', 'version_title')
    autocomplete_fields = ('artist', 'work', 'record_label')
    readonly_fields = (
        'complete_recording_title', 'complete_version_title', 'title',
        'work_link', 'artist_link')
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
                ('isrc', 'artist', 'record_label'),
                ('duration', 'release_date'),
                # ('album_cd', )
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
        return obj.complete_version_title or obj.complete_version_title or obj.work.title

    def work_link(self, obj):
        url = reverse('admin:music_publisher_work_change', args=[obj.work.id])
        link = '<a href="{}">{}</a>'.format(url, obj.work)
        return mark_safe(link)
    work_link.short_description = 'Work'
    work_link.admin_order_field = 'work__id'

    def artist_link(self, obj):
        if not (obj.artist):
            return None
        url = reverse('admin:music_publisher_artist_change', args=[obj.artist.id])
        link = '<a href="{}">{}</a>'.format(url, obj.artist)
        return mark_safe(link)
    artist_link.short_description = 'Recording Artist'
    artist_link.admin_order_field = 'artist'


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
        if obj.cwr:
            url = reverse(
                'admin:music_publisher_cwrexport_change', args=(obj.id,))
            url += '?preview=true'
            return mark_safe(
                '<a href="{}" target="_blank">View CWR</a>'.format(url))

    def download_link(self, obj):
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

    def has_delete_permission(self, request, obj=None):
        """If CWR has been created, it can no longer be deleted, as it may
        have been sent. This may change once the delivery is automated."""

        if obj and obj.cwr:
            return None
        return super().has_delete_permission(request, obj)

    def get_form(self, request, obj=None, **kwargs):
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
            html = self.get_preview(obj)
            return render(request, 'raw_cwr.html', {
                **self.admin_site.each_context(request),
                'lines': html,
                'title': obj.filename})
        elif 'download' in request.GET:
            response = HttpResponse(obj.cwr.encode().decode('latin1'))
            cd = 'attachment; filename="{}"'.format(obj.filename)
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

    def save_model(self, request, obj, form, change):
        """Django splits the saving process int two parts, which does not
            work in this case, so this is simply passing the main object
            through to :meth:`save_related`.
        """
        if not (hasattr(self, 'obj') and self.obj.cwr):
            super().save_model(request, obj, form, change)
            self.obj = obj

    def save_related(self, request, form, formsets, change):
        """:meth:`save_model` passes the main object, which is needed to fetch
            CWR form the external service, but only after related objects are
            saved.
        """
        if hasattr(self, 'obj'):
            super().save_related(request, form, formsets, change)
            self.obj.create_cwr()
            del self.obj


class ACKImportForm(ModelForm):
    """Form used for CWR acknowledgement imports.

    Attributes:
        acknowledgement_file (FileField): Field for file upload
    """

    class Meta:
        model = ACKImport
        fields = ('acknowledgement_file',)

    acknowledgement_file = FileField()

    RE_HDR = re.compile(
        r'^HDR(?:SO|AA)[0 ]{6}([ \d][ \d]\d)(.{45})01\.10(\d{8})\d{6}(\d{8})')

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
        match = re.match(self.RE_HDR, content)
        if not match:
            raise ValidationError('Incorrect CWR header')
        code, name, date1, date2 = match.groups()
        self.cleaned_data['society_code'] = code
        self.cleaned_data['society_name'] = name.strip()
        self.cleaned_data['date'] = datetime.strptime(
            max([date1, date2]), '%Y%m%d').date()
        self.cleaned_data['acknowledgement_file'] = content


@admin.register(ACKImport)
class ACKImportAdmin(admin.ModelAdmin):
    """Admin interface for :class:`.models.ACKImport`.
    """

    def get_form(self, request, obj=None, **kwargs):
        """Returns a custom form for new objects, default one for changes.
        """
        if obj is None:
            return ACKImportForm
        return super().get_form(request, obj, **kwargs)

    list_display = (
        'filename', 'society_code', 'society_name', 'date')
    list_filter = ('society_code', 'society_name')
    fields = readonly_fields = (
        'filename', 'society_code', 'society_name', 'date', 'report')

    add_fields = ('acknowledgement_file',)

    def get_fields(self, request, obj=None):
        """Return different fields for add vs change.
        """
        if obj:
            return self.fields
        return self.add_fields

    RE_ACK = re.compile(re.compile(
        r'(?<=\n)ACK.{106}(.{20})(.{20})(.{8})(.{2})', re.S))

    def process(self, request, society_code, file_content):
        """Create appropriate WorkAcknowledgement objects, without duplicates.

        Big part of this code should be moved to the model, left here because
        messaging is simpler.
        """

        unknown_work_ids = []
        existing_work_ids = []
        report = ''
        for x in re.findall(self.RE_ACK, file_content):
            work_id, remote_work_id, dat, status = x
            # work ID is numeric with an optional string
            work_id = work_id.strip()
            PREFIX = SETTINGS.get('work_id_prefix', '')
            if work_id.startswith(PREFIX):
                work_id = work_id[len(PREFIX):]
            if not work_id.isnumeric():
                unknown_work_ids.append(work_id)
                continue
            work_id = int(work_id)
            remote_work_id = remote_work_id.strip()
            dat = datetime.strptime(dat, '%Y%m%d').date()
            work = Work.objects.filter(id=work_id).first()
            if not work:
                messages.add_message(
                    request, messages.ERROR,
                    'Unknown work ID: {}'.format(work_id))
                continue
            wa, c = WorkAcknowledgement.objects.get_or_create(
                work_id=work_id,
                remote_work_id=remote_work_id,
                society_code=society_code,
                date=dat,
                status=status)
            if not c:
                existing_work_ids.append(str(work_id))
            report += '{} {} <{}>\n'.format(
                work.work_id, work.title, wa.get_status_display())
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
        if change:
            return
        if form.is_valid():
            cd = form.cleaned_data
            obj.filename = cd['filename']
            obj.society_code = cd['society_code']
            obj.society_name = cd['society_name']
            obj.date = cd['date']
            # TODO move process() to model, and handle messages here
            obj.report = self.process(
                request, obj.society_code, cd['acknowledgement_file'])
            super().save_model(request, obj, form, change)

    def has_delete_permission(self, request, obj=None, *args, **kwargs):
        """Deleting ACK imports is a really bad idea.
        """
        return False


