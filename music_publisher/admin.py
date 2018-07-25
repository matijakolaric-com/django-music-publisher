from decimal import Decimal
from django import forms
from django.conf import settings
from django.contrib import admin
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db import models
from django.forms.models import BaseInlineFormSet
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.html import mark_safe
from django.utils.timezone import now
from django.views.decorators.csrf import csrf_protect
import json
from .models import (
    AlbumCD, AlternateTitle, Artist, ArtistInWork, FirstRecording, Work,
    Writer, WriterInWork, VALIDATE, CWRExport)


csrf_protect_m = method_decorator(csrf_protect)


SETTINGS = settings.MUSIC_PUBLISHER_SETTINGS


class MusicPublisherAdmin(admin.ModelAdmin):
    """Custom Admin class, easily extendable.

    Should only be used for admin classes for top-level models."""

    save_as = True

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

        if not VALIDATE:
            messages.add_message(
                request, messages.WARNING,
                mark_safe(
                    'Validation was not performed. Your data may be corrupt. '
                    'Please acquire a Validation and CWR generation licence '
                    'from <a href="https://matijakolaric.com/z_'
                    'contact/" target="_blank">matijakolaric.com</a>.'))
        elif not obj._cwr:
            messages.add_message(
                request, messages.ERROR,
                mark_safe(
                    'Validation failed, object saved, but marked as not'
                    'CWR-compliant. Please re-evaluate.'))


@admin.register(AlbumCD)
class AlbumCDAdmin(MusicPublisherAdmin):
    readonly_fields = ('album_label', 'library', 'label_not_set')

    def get_fieldsets(self, request, obj=None):
        fieldsets = (
            ('Library', {
                'fields': (
                    ('cd_identifier', 'library'),)
            }) if SETTINGS.get('library') else (
                'Library not set', {'fields': ()}),
            ('First Album', {
                'fields': (
                    ('album_title', 'album_label' if SETTINGS.get(
                        'label') else 'label_not_set'),
                    ('ean', 'release_date'))
            }),
        )
        return fieldsets

    def label_not_set(self, obj=None):
        return 'NOT SET'
    label_not_set.short_description = 'Label'

    list_display = (
        '__str__',
        'library', 'cd_identifier',
        'album_title', 'album_label', 'release_date', 'ean',
        '_cwr'
    )
    list_filter = ('_cwr',)

    search_fields = ('album_title', '^cd_identifier')
    actions = None

    def save_model(self, request, obj, form, *args, **kwargs):
        super().save_model(request, obj, form, *args, **kwargs)
        if form.changed_data:
            qs = Work.objects.filter(firstrecording__album_cd=obj)
            qs.update(last_change=now())


@admin.register(Artist)
class ArtistAdmin(MusicPublisherAdmin):
    list_display = ('last_or_band', 'first_name', '_cwr')
    search_fields = ('last_name',)
    list_filter = ('_cwr',)

    def last_or_band(self, obj):
        return obj.last_name
    last_or_band.short_description = 'Last or band name'
    last_or_band.admin_order_field = 'last_name'

    actions = None

    def save_model(self, request, obj, form, *args, **kwargs):
        super().save_model(request, obj, form, *args, **kwargs)
        if form.changed_data:
            qs = Work.objects.filter(artistinwork__artist=obj)
            qs.update(last_change=now())


@admin.register(Writer)
class WriterAdmin(MusicPublisherAdmin):
    list_display = ('last_name', 'first_name', 'ipi_name', 'pr_society',
                    '_can_be_controlled', 'generally_controlled', '_cwr')
    list_filter = ('_can_be_controlled', 'generally_controlled',
                   'pr_society', '_cwr')
    search_fields = ('last_name', '^ipi_name')
    readonly_fields = ('_can_be_controlled',)
    fieldsets = (
        ('Name', {
            'fields': (
                ('first_name', 'last_name'),)}),
        ('IPI', {
            'fields': (
                ('ipi_name', 'ipi_base'),
                'pr_society'),
        }),
        ('Generally controlled', {
            'fields': (
                ('generally_controlled', 'saan'),),
        }),
    )
    actions = None

    def save_model(self, request, obj, form, *args, **kwargs):
        super().save_model(request, obj, form, *args, **kwargs)
        if form.changed_data:
            qs = Work.objects.filter(writerinwork__writer=obj)
            qs.update(last_change=now())


class AlternateTitleInline(admin.TabularInline):
    model = AlternateTitle
    extra = 0


class ArtistInWorkInline(admin.TabularInline):
    autocomplete_fields = ('artist', )
    model = ArtistInWork
    extra = 0


class WriterInWorkFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        total = 0
        for form in self.forms:
            if not form.is_valid():
                return
            if form.cleaned_data and not form.cleaned_data.get('DELETE'):
                total += form.cleaned_data['relative_share']
        if not(Decimal(99.98) <= total <= Decimal(100.02)):
            raise ValidationError('Sum of relative shares must be 100%.')


class WriterInWorkInline(admin.TabularInline):
    autocomplete_fields = ('writer', )
    model = WriterInWork
    formset = WriterInWorkFormSet
    extra = 0
    min_num = 1
    fieldsets = (
        (None, {
            'fields': (
                'writer',
                ('capacity', 'relative_share'),
                ('controlled', 'saan'),
            ),
        }),
    )


class FirstRecordingInline(admin.StackedInline):
    autocomplete_fields = ('album_cd', )
    fieldsets = (
        (None, {
            'fields': (
                'album_cd',
                ('isrc', 'duration'),
                ('catalog_number', 'release_date')),
        }),
    )
    formfield_overrides = {
        models.TimeField: {'widget': forms.TimeInput},
    }
    model = FirstRecording
    extra = 0


@admin.register(Work)
class WorkAdmin(MusicPublisherAdmin):
    inlines = (
        AlternateTitleInline, WriterInWorkInline,
        FirstRecordingInline, ArtistInWorkInline)

    def writer_last_names(self, obj):
        return ' / '.join(
            writer.last_name.upper() for writer in obj.writers.all())
    writer_last_names.short_description = 'Writers\' last names'

    def percentage_controlled(self, obj):
        return sum(
            wiw.relative_share for wiw in obj.writerinwork_set.all()
            if wiw.controlled)
    percentage_controlled.short_description = '% controlled'

    def album_cd(self, obj):
        if not obj.firstrecording:
            return None
        return obj.firstrecording.album_cd
    album_cd.short_description = 'Album / Library CD'

    def isrc(self, obj):
        if not obj.firstrecording:
            return None
        return obj.firstrecording.isrc
    isrc.short_description = 'ISRC'

    def duration(self, obj):
        if not obj.firstrecording or not obj.firstrecording.duration:
            return None
        return obj.firstrecording.duration.strftime('%H:%M:%S')

    readonly_fields = ('writer_last_names', 'work_id')
    list_display = (
        'work_id', 'title', 'iswc', 'writer_last_names',
        'percentage_controlled', 'duration', 'isrc', 'album_cd', '_cwr')

    search_fields = (
        'title', 'alternatetitle__title', 'writerinwork__writer__last_name',
        '^iswc', '^id')

    def get_search_results(self, request, queryset, search_term):
        if search_term.isnumeric():
            print(search_term)
            search_term = search_term.lstrip('0')
        return super().get_search_results(request, queryset, search_term)

    fieldsets = (
        (None, {
            'fields': (
                ('title', 'iswc'),)}),)

    def save_model(self, request, obj, form, *args, **kwargs):
        if form.changed_data:
            obj.last_change = now()
        super().save_model(request, obj, form, *args, **kwargs)

    def create_cwr(self, request, qs):
        url = reverse('admin:music_publisher_cwrexport_add')
        ids = qs.values_list('id', flat=True)
        return HttpResponseRedirect(
            '{}?works={}'.format(url, ','.join(str(i) for i in ids)))
    create_cwr.short_description = 'Create CWR from selected works.'

    actions = (create_cwr,)

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions


@admin.register(CWRExport)
class CWRExportAdmin(admin.ModelAdmin):

    def cwr_ready(self, obj):
        return obj.cwr != ''
    cwr_ready.boolean = True

    def work_count(self, obj):
        return obj.works.count()
    cwr_ready.boolean = True

    def download_link(self, obj):
        if obj.cwr:
            url = reverse(
                'admin:music_publisher_cwrexport_change', args=(obj.id,))
            url += '?download=true'
            return mark_safe('<a href="{}">Download</a>'.format(url))

    autocomplete_fields = ('works', )
    list_display = (
        'filename', 'nwr_rev', 'work_count', 'cwr_ready', 'download_link')

    def get_readonly_fields(self, request, obj=None):
        if obj and obj.cwr:
            return ('nwr_rev', 'works', 'filename', 'download_link')
        else:
            return ()

    def get_fields(self, request, obj=None):
        if obj and obj.cwr:
            return ('nwr_rev', 'works', 'filename', 'download_link')
        else:
            return ('nwr_rev', 'works')

    def save_model(self, request, obj, form, change):
        if not change:
            super().save_model(request, obj, form, change)
            self.obj = obj

    def save_related(self, request, form, formsets, change):
        if not change:
            super().save_related(request, form, formsets, change)
            self.obj.get_cwr()

    def change_view(self, request, object_id, *args, **kwargs):
        if 'download' in request.GET:
            obj = get_object_or_404(CWRExport, pk=object_id)
            response = HttpResponse(obj.cwr.encode().decode('latin1'))
            cd = 'attachment; filename="{}"'.format(obj.filename)
            response['Content-Disposition'] = cd
            return response
        return super().change_view(request, object_id, *args, **kwargs)

