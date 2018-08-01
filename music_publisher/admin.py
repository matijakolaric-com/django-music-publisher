from datetime import datetime
from decimal import Decimal
from django import forms
from django.conf import settings
from django.contrib import admin
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db import models
from django.forms import ModelForm, FileField
from django.forms.models import BaseInlineFormSet
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
# from django.utils.decorators import method_decorator
from django.utils.html import mark_safe
from django.utils.timezone import now
# from django.views.decorators.csrf import csrf_protect
from .models import (
    AlbumCD, AlternateTitle, Artist, ArtistInWork, FirstRecording, Work,
    Writer, WriterInWork, VALIDATE, CWRExport, ACKImport, WorkAcknowledgement)
import re

# csrf_protect_m = method_decorator(csrf_protect)


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


class WorkAcknowledgementInline(admin.TabularInline):
    model = WorkAcknowledgement
    extra = 0
    fields = readonly_fields = (
        'date', 'society_code', 'remote_work_id', 'status')

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False


@admin.register(Work)
class WorkAdmin(MusicPublisherAdmin):
    inlines = (
        AlternateTitleInline, WriterInWorkInline,
        FirstRecordingInline, ArtistInWorkInline,
        WorkAcknowledgementInline)

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

    class HasISRCListFilter(admin.SimpleListFilter):
        title = 'Has ISWC'
        parameter_name = 'has_iswc'

        def lookups(self, request, model_admin):
            return (
                ('Y', 'Yes'),
                ('N', 'No'),
            )

        def queryset(self, request, queryset):
            if self.value() == 'Y':
                return queryset.exclude(iswc__isnull=True)
            elif self.value() == 'N':
                return queryset.filter(iswc__isnull=True)

    class HasRecordingListFilter(admin.SimpleListFilter):
        title = 'Has First Recording'
        parameter_name = 'has_rec'

        def lookups(self, request, model_admin):
            return (
                ('Y', 'Yes'),
                ('N', 'No'),
            )

        def queryset(self, request, queryset):
            if self.value() == 'Y':
                return queryset.exclude(firstrecording__isnull=True)
            elif self.value() == 'N':
                return queryset.filter(firstrecording__isnull=True)

    list_filter = (
        HasISRCListFilter,
        HasRecordingListFilter,
        ('firstrecording__album_cd', admin.RelatedOnlyFieldListFilter),
        '_cwr',
        'last_change',
    )

    search_fields = (
        'title', 'alternatetitle__title', 'writerinwork__writer__last_name',
        '^iswc', '^id')

    def get_search_results(self, request, queryset, search_term):
        if search_term.isnumeric():
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

    actions = None

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
        if not (hasattr(self, 'obj') and self.obj.cwr):
            super().save_model(request, obj, form, change)
            self.obj = obj

    def save_related(self, request, form, formsets, change):
        if not (hasattr(self, 'obj') and self.obj.cwr):
            super().save_related(request, form, formsets, change)
            try:
                self.obj.get_cwr()
            except ValidationError as e:
                messages.add_message(
                    request, messages.ERROR,
                    mark_safe(
                        'CWR could not be fetched from external service. '
                        'The reason is "{}". Please try saving again later. '
                        'Currently saved as draft.'.format(str(e))))
            finally:
                del self.obj

    def has_delete_permission(self, request, obj=None):
        if obj and obj.cwr:
            return None
        return super().has_delete_permission(request, obj)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        obj = get_object_or_404(CWRExport, pk=object_id)
        if 'download' in request.GET:
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


class ACKImportForm(ModelForm):
    class Meta:
        model = ACKImport
        fields = ('acknowledgement_file',)

    acknowledgement_file = FileField()

    RE_HDR = re.compile(
        r'^HDRSO[0 ]{6}([ \d][ \d]\d)(.{45})01\.10(\d{8})\d{6}(\d{8})')

    def clean(self):
        super().clean()
        cd = self.cleaned_data
        ack = cd.get('acknowledgement_file')
        filename = ack.name
        if not (len(filename) in [18, 19] and filename[-5:].upper() != '.V21'):
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
    def get_form(self, request, obj=None):
        if obj is None:
            return ACKImportForm
        return super().get_form(request, obj)

    list_display = (
        'filename', 'society_code', 'society_name', 'date')
    fields = readonly_fields = (
        'filename', 'society_code', 'society_name', 'date', 'report')

    add_fields = ('acknowledgement_file',)

    def get_fields(self, reqest, obj=None):
        if obj:
            return self.fields
        return self.add_fields

    RE_ACK = re.compile(re.compile(
        r'(?<=\n)ACK.{106}(.{20})(.{20})(.{8})(.{2})', re.S))

    def process(self, request, society_code, file_content):
        unknown_work_ids = []
        existing_work_ids = []
        report = ''
        for x in re.findall(self.RE_ACK, file_content):
            work_id, remote_work_id, dat, status = x
            work_id = work_id.strip()
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
        if change:
            return
        if form.is_valid():
            cd = form.cleaned_data
            obj.filename = cd['filename']
            obj.society_code = cd['society_code']
            obj.society_name = cd['society_name']
            obj.date = cd['date']
            obj.report = self.process(
                request, obj.society_code, cd['acknowledgement_file'])
            super().save_model(request, obj, form, change)

    def has_delete_permission(self, request, obj=None):
        return False
