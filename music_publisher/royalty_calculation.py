"""
This module is about processing royalty statements.

It processes files in the request-response cycle, not in background workers.
Therefore, focus is on speed. Nothing is written to the database, and
SELECTs are optimised and performed in one batch.

"""

import csv
import os
from collections import defaultdict
from decimal import Decimal
from io import TextIOWrapper
from tempfile import NamedTemporaryFile

from django import forms
from django.conf import settings
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.files.uploadhandler import TemporaryFileUploadHandler
from django.http import FileResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.edit import FormView

from .models import SOCIETY_DICT, WorkAcknowledgement, Writer, WriterInWork


def get_id_sources():
    """
    Yield choices, fixed and societies.
    """
    yield None, 'Publisher Work ID:'
    yield settings.PUBLISHER_CODE, settings.PUBLISHER_NAME
    yield None, 'International Standard Codes:'
    yield 'ISWC', 'ISWC'
    yield 'ISRC', 'ISRC'
    yield None, 'Sender Work ID:'
    codes = WorkAcknowledgement.objects.order_by(
        'society_code').values_list('society_code', flat=True).distinct()
    codes = [(code, SOCIETY_DICT.get(code, '')) for code in codes]
    codes.sort(key=lambda code: code[1])
    for code in codes:
        yield code


def get_right_types():
    """
    Yield fixed options.

    They will be extended with columns in JS and prior to validation.
    """
    yield 'p', 'Performance for all rows'
    yield 'm', 'Mechanical for all rows'
    yield 's', 'Sync for all rows'
    yield None, '-' * 40


class RoyaltyCalculationForm(forms.Form):
    """The form for royalty calculations.
    """
    class Meta:
        fields = ('in_file',)

    class Media:
        css = {'all': ('admin/css/forms.css',)}
        js = (
            'admin/js/vendor/jquery/jquery.js',
            'admin/js/jquery.init.js')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.file = None

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
        choices=get_id_sources, initial=settings.PUBLISHER_CODE,
        label='Work ID Source',
        help_text='You or CWR acknowledgement source.',
    )
    amount_column = forms.ChoiceField(
        choices=[], label='Amount', initial=-1,
        help_text='Select the column containing received amount.'
    )
    right_type_column = forms.ChoiceField(
        choices=get_right_types, initial='p', label='Right type',
        help_text='Select the right type or the column specifying it.'
    )
    algo = forms.ChoiceField(
        choices=ALGOS, initial='fee', label='Algorithm type',
        help_text='Choose the algorithm type, see user manual for details.'
    )
    default_fee = forms.DecimalField(
        max_digits=5, decimal_places=2, initial=0, label='Default fee (%)',
        help_text='Used if no fee is present in the database.'
    )

    def is_valid(self):
        """Append additional choices to various fields, prior to the actual
        validation.
        """
        self.file = TextIOWrapper(self.files.get('in_file'))
        try:
            csv_reader = csv.DictReader(self.file)
            for i, field in enumerate(csv_reader.fieldnames):
                self.fields['work_id_column'].choices.append((str(i), field))
                self.fields['right_type_column'].choices = list(
                    self.fields['right_type_column'].choices)
                self.fields['right_type_column'].choices.append(
                    (str(i), field))
                self.fields['amount_column'].choices.append((str(i), field))
            valid = super().is_valid()
        except Exception:  # to match user stupidity
            return False
        return valid


class RoyaltyCalculation(object):
    """The process of royalty calculation."""

    def __init__(self, form):
        """Initialization with data from thew form and empty attributes.
        """
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
        self.writer_ids = set()
        self.writers = {}
        self.works = defaultdict(list)

    @property
    def filename(self):
        """Return the filename of the output file."""
        in_name = self.in_file.name.rsplit('.', 1)[0]
        return in_name + '-output-' + self.algo + '.csv'

    @property
    def fieldnames(self):
        """Return the list of field names in the output file."""
        self.file.seek(0)
        csv_reader = csv.DictReader(self.file)
        fieldnames = csv_reader.fieldnames
        if self.algo == 'share':
            fieldnames.append('Right type')
        fieldnames += [
            'Controlled by publisher (%)',
            'Interested party',
            'Role']
        if self.algo == 'fee':
            fieldnames += [
                'Manuscript share (%)',
                'Share in amount received (%)',
                'Amount before fee',
                'Fee (%)',
                'Fee amount']
        elif self.algo == 'share':
            fieldnames += [
                'Owned share (%)',
                'Share in amount received (%)']
        fieldnames.append('Net amount')
        return fieldnames

    def get_work_ids(self):
        """
        Find work unambiguous work identifiers.

        Returns:
            set of work identifier from the file
        """

        self.file.seek(0)
        csv_reader = csv.reader(self.file)
        work_ids = set()
        for row in csv_reader:
            given_id = row[self.wc]
            if self.work_id_source in ['ISWC', 'ISRC']:
                given_id = given_id.replace('.', '').replace('-', '')
            work_ids.add(given_id)
        return work_ids

    def get_work_queryset(self, work_ids):
        """
        Return the appropriate queryset based on work ID source and ids.

        Returns:
            queryset with :class:`.models.WriterInWork` objects. \
            ``query_id`` has the matched field value.
        """
        qs = WriterInWork.objects.filter(controlled=True)
        if self.work_id_source == settings.PUBLISHER_CODE:
            qs = qs.filter(work___work_id__in=work_ids)
            qs = qs.extra(select={'query_id': "_work_id"})
        elif self.work_id_source == 'ISWC':
            qs = qs.filter(work__iswc__in=work_ids)
            qs = qs.extra(select={'query_id': "iswc"})
        elif self.work_id_source == 'ISRC':
            qs = qs.filter(work__recordings__isrc__in=work_ids)
            qs = qs.extra(select={'query_id': "isrc"})
        else:
            qs = qs.filter(
                work__workacknowledgement__society_code=self.work_id_source)
            qs = qs.filter(
                work__workacknowledgement__remote_work_id__in=work_ids)
            qs = qs.extra(select={
                'query_id':
                    "music_publisher_workacknowledgement.remote_work_id"})
        qs = qs.distinct()
        return qs

    def generate_works_dict(self, qs):
        """Generate the works cache.

        Returns:
            dict (works) of lists (writerinwork) of dicts
        """
        for wiw in qs:
            assert (wiw.work_id is not None)
            self.writer_ids.add(wiw.writer_id)
            d = {
                'writer_id': wiw.writer_id,
                'role': wiw.get_capacity_display(),
                'relative_share': wiw.relative_share,
                'fee': wiw.publisher_fee,
            }
            self.works[wiw.query_id].append(d)

    def generate_writer_dict(self):
        """Generate the writers cache.
        Returns:
            dict (writer) of dicts
        """
        qs = Writer.objects.filter(id__in=self.writer_ids)
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

    def get_works_and_writers(self):
        """Get work and writer data.

        Extract all work IDs, then perform the queries and put them in
        dictionaries. When the actual file processing happens, no further
        queries are required.
        """

        # the first pass of processing
        work_ids = self.get_work_ids()

        # the first query
        qs = self.get_work_queryset(work_ids)

        self.generate_works_dict(qs)

        # this includes the second query
        self.generate_writer_dict()

    def process_row(self, row):
        """Process one incoming row, yield multiple output rows."""
        # get the identifier and clean
        given_id = row[self.wc]
        if self.work_id_source in ['ISWC', 'ISRC']:
            given_id = given_id.replace('.', '').replace('-', '')

        # get the work, if not found yield error
        work = self.works.get(given_id)

        amount = Decimal(row[self.ac])
        right = (self.right or row[self.rc][0]).lower()
        share_split = {
            'p': settings.PUBLISHING_AGREEMENT_PUBLISHER_PR,
            'm': settings.PUBLISHING_AGREEMENT_PUBLISHER_MR,
            's': settings.PUBLISHING_AGREEMENT_PUBLISHER_SR}[right]

        # Add data to all output rows
        if self.algo == 'share':
            row.append({'p': 'Perf.', 'm': 'Mech.', 's': 'Sync'}[right])
        if not work:
            row.append('')
            row.append('ERROR: Work not found')
            yield row
            return

        controlled = sum([line['relative_share'] for line in work]) / 100
        row.append('{0:.4f}'.format(controlled))

        # Prepare output lines, one per controlled writer in work
        for line in work:

            # Common fields for all algorithms
            out_row = row.copy()
            writer = self.writers[line.get('writer_id')]
            out_row.append(writer['name'])
            out_row.append(line['role'])
            relative_share = line['relative_share'] / 100

            if self.algo == 'fee':
                out_row.append('{0:.4f}'.format(relative_share))
                share = (relative_share / controlled).quantize(
                    Decimal('.000001'))
                amount_before_fee = amount * share
                out_row.append('{0:.6f}'.format(share))
                out_row.append('{}'.format(amount_before_fee))
                fee = (line['fee'] or writer['fee'] or self.default_fee) / 100
                out_row.append('{}'.format(fee))
                fee_amount = amount_before_fee * fee
                out_row.append('{}'.format(fee_amount or '0'))
                net_amount = amount_before_fee - fee_amount
                out_row.append('{}'.format(net_amount))

            elif self.algo == 'share':

                # do not show lines when writers get nothing
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

            # "Share" algorithm has one additional row with the publisher
            if self.algo == 'share':
                out_row = row.copy()
                out_row.append('{}, [{}]'.format(
                    settings.PUBLISHER_NAME,
                    settings.PUBLISHER_IPI_NAME))
                out_row.append('Original Publisher')
                out_row.append('{0:.6f}'.format(share_split * controlled))
                out_row.append('{0:.6f}'.format(share_split))
                net_amount = amount * share_split
                out_row.append('{}'.format(net_amount))

                yield out_row

    @property
    def out_file_path(self):
        """This method creates the output file and outputs the temporary path.

        Note that the process happens is several passes.
        """
        self.get_works_and_writers()

        # the second pass of processing
        self.file.seek(0)
        csv_reader = csv.reader(self.file)

        f = NamedTemporaryFile(mode='w+', delete=False, encoding='utf8')
        csv_writer = csv.writer(f)
        csv_writer.writerow(self.fieldnames)
        for row in csv_reader:
            for out_row in self.process_row(row):
                csv_writer.writerow(out_row)

        f.filename = self.filename
        f.close()
        return f.name


class RoyaltyCalculationView(PermissionRequiredMixin, FormView):
    """The view for royalty calculations."""

    template_name = 'music_publisher/royalty_calculation.html'
    form_class = RoyaltyCalculationForm
    permission_required = ('music_publisher.can_process_royalties',)

    def render_to_response(self, context, **response_kwargs):
        """Prepare the context, required since we use admin template."""
        context['site_header'] = settings.PUBLISHER_NAME
        context['opts'] = {
            'app_label': 'music_publisher',
            'model_name': 'royaltycalculations',
        }
        context['has_permission'] = True
        context['is_nav_sidebar_enabled'] = False  # Permission issue
        return super().render_to_response(context, **response_kwargs)

    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        """Royalty processing works only with TemporaryFileUploadHandler."""
        request.upload_handlers = [TemporaryFileUploadHandler()]
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        """This is where the magic happens."""
        rc = RoyaltyCalculation(form)
        path = rc.out_file_path
        f = open(path, 'rb')
        try:
            return FileResponse(f, filename=rc.filename, as_attachment=False)
        finally:
            os.remove(path)
