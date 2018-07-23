from django import forms
from django.contrib import admin
from django.db import models
from django.conf import settings
from django.contrib import messages
from django.utils.html import mark_safe
from django.utils.timezone import now
import json
from .models import (
    AlbumCD, AlternateTitle, Artist, ArtistInWork, FirstRecording, Work,
    Writer, WriterInWork, VALIDATE)


SETTINGS = settings.MUSIC_PUBLISHER_SETTINGS


class MusicPublisherAdmin(admin.ModelAdmin):
    """Custom Admin class, easily extendable.

    Should only be used for admin classes for top-level models."""

    def save_model(self, request, obj, *args, **kwargs):
        super().save_model(request, obj, *args, **kwargs)
        if not VALIDATE:
            messages.add_message(
                request, messages.WARNING,
                mark_safe(
                    'Validation was not performed. Your data may be corrupt. '
                    'Please acquire a Validation and CWR generation licence '
                    'from <a href="https://matijakolaric.com/z_'
                    'contact/" target="_blank">matijakolaric.com</a>.'))


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
    )

    search_fields = ('album_title', '^cd_identifier')
    actions = None

    def save_model(self, request, obj, form, *args, **kwargs):
        super().save_model(request, obj, form, *args, **kwargs)
        if form.changed_data:
            qs = Work.objects.filter(firstrecording__album_cd=obj)
            qs.update(last_change=now())


@admin.register(Artist)
class ArtistAdmin(MusicPublisherAdmin):
    list_display = ('last_or_band', 'first_name')
    search_fields = ('last_name',)

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
                    '_can_be_controlled', 'generally_controlled')
    list_filter = ('_can_be_controlled', 'generally_controlled',
                   'pr_society', )
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


class WriterInWorkInline(admin.TabularInline):
    autocomplete_fields = ('writer', )
    model = WriterInWork
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
    actions = None

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

    def json(self, obj):
        return json.dumps({
            "publisher_id": SETTINGS.get('publisher_id'),
            "publisher_name": SETTINGS.get('publisher_name'),
            "publisher_ipi_name": SETTINGS.get('publisher_ipi_name'),
            "publisher_ipi_base": SETTINGS.get('publisher_ipi_base'),
            "publisher_pr_society": SETTINGS.get(
                'publisher_pr_society'),
            "publisher_mr_society": SETTINGS.get(
                'publisher_mr_society'),
            "publisher_sr_society": SETTINGS.get(
                'publisher_pr_society'),
            "revision": False,
            "works": obj.json,
        })

    readonly_fields = ('writer_last_names',)
    list_display = (
        'title', 'iswc', 'writer_last_names', 'percentage_controlled',
        'duration', 'isrc', 'album_cd')
    fieldsets = (
        (None, {
            'fields': (
                ('title', 'iswc'),)}),)

    def save_model(self, request, obj, form, *args, **kwargs):
        if form.changed_data:
            obj.last_change = now()
        super().save_model(request, obj, form, *args, **kwargs)
