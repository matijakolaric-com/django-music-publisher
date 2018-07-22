from django.contrib import admin
from django import forms
from django.db import models
from .models import (
    AlbumCD, AlternateTitle, Artist, ArtistInWork, FirstRecording, Work)
from django.conf import settings

SETTINGS = settings.MUSIC_PUBLISHER_SETTINGS


@admin.register(AlbumCD)
class AlbumCDAdmin(admin.ModelAdmin):
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


@admin.register(Artist)
class ArtistAdmin(admin.ModelAdmin):
    list_display = ('last_or_band', 'first_name')
    search_fields = ('last_name',)

    def last_or_band(self, obj):
        return obj.last_name
    last_or_band.short_description = 'Last or band name'
    last_or_band.admin_order_field = 'last_name'


class AlternateTitleInline(admin.StackedInline):
    model = AlternateTitle
    extra = 0


class ArtistInWorkInline(admin.StackedInline):
    autocomplete_fields = ('artist', )
    model = ArtistInWork
    extra = 0


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
class WorkAdmin(admin.ModelAdmin):
    inlines = (
        AlternateTitleInline, FirstRecordingInline, ArtistInWorkInline)
