from django.contrib import admin, messages
from django.db import models
from django import forms
from django.http import StreamingHttpResponse, HttpResponse, FileResponse
from django.conf import settings
from io import TextIOWrapper
from tempfile import NamedTemporaryFile
from collections import defaultdict
from .admin import WorkForm
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin

from .models import WorkAcknowledgement, SOCIETY_DICT, WriterInWork, Writer
import csv
import os

from django.contrib.admin import site

from django.apps import apps

from django.views.generic.edit import FormView
from django.core.files.uploadhandler import TemporaryFileUploadHandler

from decimal import Decimal


class RoyaltyCalculationForm(forms.Form):
    class Meta:
        fields = ('in_file', )

    class Media:
        css = {'all': ('admin/css/forms.css',)}
        js = ('admin/js/vendor/jquery/jquery.js',
              'admin/js/jquery.init.js')

    def get_id_sources():
        yield settings.PUBLISHER_CODE, settings.PUBLISHER_NAME
        yield 'ISWC', 'ISWC'
        yield None, '-' * 40
        codes = WorkAcknowledgement.objects.order_by('society_code').values_list ('society_code', flat=True).distinct()
        codes = [(code, SOCIETY_DICT.get(code, '') ) for code in codes]
        codes.sort(key=lambda code: code[1])
        for code in codes:
            yield code

    def get_right_types():
        yield 'p', ' Performance for all rows'
        yield 'm', 'Mechanical for all rows'
        yield 's', 'Sync for all rows'
        yield None, '-' * 40

    ALGOS = [
        ('share', 'Split by calculated share.'),
        ('fee', 'Split by manuscript share and apply fees.'),
    ]

    in_file = forms.FileField(
        label='Incoming statement',
        help_text='A CSV file with a header row is required.'
    )
    work_id_column = forms.ChoiceField(
        choices=[], label='Work ID', initial=1,
        help_text='Select the column containing work IDs.'
    )
    work_id_source = forms.ChoiceField(
        choices=get_id_sources, label='Work ID Source',
        help_text='You or CWR acknowledgement source.',
        initial=settings.PUBLISHER_CODE
    )
    amount_column = forms.ChoiceField(
        choices=[], label='Amount', initial=-1,
        help_text='Select the column containing received amount.'
    )
    right_type_column = forms.ChoiceField(
        choices=get_right_types, label='Right type',
        help_text='Select the right type or the column specifying it.'
    )
    algo = forms.ChoiceField(
        choices=ALGOS, label='Algorithm type',
        help_text='Choose the algorithm type, see user manual for details.'
    )
    default_fee = forms.DecimalField(
        max_digits=5, decimal_places=2, initial=0, label= 'Default fee (%)',
        help_text='Used if no fee is present in the database.'
    )

    def is_valid(self):
        self.file = TextIOWrapper(self.files.get('in_file'))
        try:
            csv_reader = csv.DictReader(self.file)
            for i, field in enumerate(csv_reader.fieldnames):
                self.fields['work_id_column'].choices.append((str(i), field))
                self.fields['right_type_column'].choices = list(self.fields['right_type_column'].choices)
                self.fields['right_type_column'].choices.append((str(i), field))
                self.fields['amount_column'].choices.append((str(i), field))
            valid = super().is_valid()
        except Exception as e:
            if settings.DEBUG:
                raise
            return False
        return valid


class RoyaltyCalculation(object):
    def __init__(self, form):
        self.file = form.file
        for key, value in form.cleaned_data.items():
            setattr(self, key, value)
        self.wc = int(form.cleaned_data.get('work_id_column'))
        self.right = form.cleaned_data.get('right_type_column')
        if self.right in ['p', 'm', 's']:
            self.rc = None
        else:
            self.rc = int(self.right)
            self.right = None
        self.ac = int(form.cleaned_data.get('amount_column'))
        self._fieldnames = []
        self.writers = {}
        self.works = defaultdict(list)

    def __str__(self):
        return self.filename

    @property
    def filename(self):
        in_name = self.in_file.name.rsplit('.', 1)[0]
        return in_name + '-output-' + self.algo + '.csv'

    @property
    def fieldnames(self):
        if self._fieldnames:
            return self._fieldnames
        self.file.seek(0)
        csv_reader = csv.DictReader(self.file)
        self._fieldnames = csv_reader.fieldnames
        if self.algo == 'share':
            self._fieldnames.append('Right Type')
        self._fieldnames += [
            'Controlled by publisher (%)',
            'Interested party',
            'Role']
        if self.algo == 'fee':
            self._fieldnames += [
                'Manuscript share (%)',
                'Share in amount received (%)',
                'Amount before fee',
                'Fee (%)',
                'Fee amount']
        elif self.algo == 'share':
            self._fieldnames += [
                'Owned Share (%)',
                'Share in amount received (%)']
        self._fieldnames.append('Net amount')
        return self._fieldnames

    def get_works_and_writers(self):
        self.file.seek(0)
        csv_reader = csv.reader(self.file)
        work_ids = set()
        for row in csv_reader:
            id = row[self.wc]
            if self.work_id_source == 'ISWC':
                id = id.replace('.', '').replace('-', '')
            work_ids.add(id)

        qs = WriterInWork.objects.filter(controlled=True)
        if self.work_id_source == settings.PUBLISHER_CODE:
            qs = qs.filter(work___work_id__in=work_ids)
            qs = qs.extra(select={'query_id': "_work_id"})
        elif self.work_id_source == 'ISWC':
            qs = qs.filter(work__iswc__in=work_ids)
            qs = qs.extra(select={'query_id': "iswc"})
        else:
            qs = qs.filter(work__workacknowledgement__society_code=self.work_id_source)
            qs = qs.filter(work__workacknowledgement__remote_work_id__in=work_ids)
            qs = qs.extra(select={'query_id': "music_publisher_workacknowledgement.remote_work_id"})
        writer_ids = set()
        for wiw in qs:
            assert(wiw.work_id is not None)
            writer_ids.add(wiw.writer_id)
            d = {
                'writer_id': wiw.writer_id,
                'role': wiw.get_capacity_display(),
                'relative_share': wiw.relative_share,
                'fee': wiw.publisher_fee,
            }
            self.works[wiw.query_id].append(d)
        qs = Writer.objects.filter(id__in=writer_ids)
        for writer in qs:
            if writer.first_name:
                name = '{}, {} [{}]'.format(
                        writer.last_name,
                        writer.first_name,
                        writer.ipi_name or '')
            else:
                name = '{} [{}]'.format(
                    writer.last_name,
                    writer.ipi_name or '')

            self.writers[writer.id] = {
                'name': name,
                'fee': writer.publisher_fee
            }

    def process_row(self, row):
        id = row[self.wc]
        work = self.works.get(id)
        if not work:
            row.append('ERROR: Work not found')
            return row
        amount = Decimal(row[self.ac])
        right = (self.right or row[self.rc][0]).lower()
        if self.algo == 'share':
            row.append({'p': 'Perf.', 'm': 'Mech.', 's': 'Sync'}[right])
        controlled = sum([line['relative_share'] for line in work]) / 100
        row.append('{0:.4f}'.format(controlled))
        share_split = {
            'p': settings.PUBLISHING_AGREEMENT_PUBLISHER_PR,
            'm': settings.PUBLISHING_AGREEMENT_PUBLISHER_MR,
            's': settings.PUBLISHING_AGREEMENT_PUBLISHER_SR}[right]
        for line in work:
            out_row = row.copy()
            writer = self.writers[line.get('writer_id')]
            out_row.append(writer['name'])
            out_row.append(line['role'])
            relative_share = line['relative_share'] / 100
            if self.algo == 'fee':
                out_row.append('{0:.4f}'.format(relative_share))
                share = (relative_share / controlled).quantize(Decimal('.000001'))
                amount_before_fee = amount * share
                out_row.append('{0:.6f}'.format(share))
                out_row.append('{}'.format(amount_before_fee))
                fee = (line['fee'] or writer['fee'] or self.default_fee) / 100
                out_row.append('{}'.format(fee))
                fee_amount = amount_before_fee * fee
                out_row.append('{}'.format(fee_amount))
                net_amount = amount_before_fee - fee_amount
                out_row.append('{}'.format(net_amount))
            elif self.algo == 'share':
                if share_split == Decimal(1):
                    continue
                owned_share = relative_share * (1 - share_split)
                out_row.append('{0:.6f}'.format(owned_share))
                share = (owned_share / controlled).quantize(Decimal('.000001'))
                net_amount = amount * share
                out_row.append('{0:.6f}'.format(share))
                out_row.append('{}'.format(net_amount))
            yield out_row
        else:
            if self.algo == 'share':
                out_row = row.copy()
                out_row.append('{}, [{}]'.format(settings.PUBLISHER_NAME, settings.PUBLISHER_IPI_NAME))
                out_row.append('Original Publisher')
                out_row.append('{0:.6f}'.format(share_split))
                out_row.append('{0:.6f}'.format(share_split))
                net_amount = amount * share_split
                out_row.append('{}'.format(net_amount))
                yield out_row


    @property
    def out_file_path(self):
        self.get_works_and_writers()

        self.file.seek(0)
        csv_reader = csv.reader(self.file)

        f = NamedTemporaryFile(mode='w+', delete=False, encoding='utf8')
        csv_writer = csv.writer(f)
        csv_writer.writerow(self.fieldnames)
        for row in csv_reader:
            for out_row in self.process_row(row):
                print(out_row)
                csv_writer.writerow(out_row)
        f.filename = self.filename
        f.close()
        return f.name


class RoyaltyCalculationView(PermissionRequiredMixin, FormView):
    template_name = 'music_publisher/royalty_calculation.html'
    form_class = RoyaltyCalculationForm
    permission_required = ('music_publisher.can_process_royalties',)

    def form_valid(self, form):
        rc = RoyaltyCalculation(form)
        path = rc.out_file_path
        f = open(path, 'rb')
        try:
            return FileResponse(f, filename=rc.filename, as_attachment=False)
        finally:
            os.remove(path)
