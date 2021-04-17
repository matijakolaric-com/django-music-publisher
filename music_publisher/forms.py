from django.forms import ModelForm, FileField, BooleanField
from .models import ACKImport
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.forms.models import BaseInlineFormSet
from decimal import Decimal


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



class DataImportForm(ModelForm):
    """Form used for data imports.

    Attributes:
        data_file (FileField): Field for file upload
    """

    class Meta:
        model = ACKImport
        fields = ('data_file',)

    data_file = FileField()
    ignore_unknown_columns = BooleanField(required=False, initial=False)

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
        from django.db import transaction

        cd = self.cleaned_data
        f = cd.get('data_file')
        report = ''
        with transaction.atomic():
            try:
                importer = DataImporter(TextIOWrapper(f), self.user)
                for work in importer.run():
                    url = reverse(
                        'admin:music_publisher_work_change', args=(work.id,))
                    report += '<a href="{}">{}</a> {}<br/>\n'.format(
                        url, work.work_id, work.title)
                if importer.unknown_keys:
                    if cd.get('ignore_unknown_columns'):
                        report += '<br>\nUNKNOWN COLUMN NAMES:<br>\n'
                        report += '<br>\n'.join(
                            [f'- {key}' for key in sorted(
                                importer.unknown_keys)]
                        )
                    else:
                        raise ValidationError(
                            'Unknown columns: ' +
                            ', '.join(importer.unknown_keys))
                report += importer.report
            except Exception as e:  # user garbage, too many possibilities
                raise ValidationError(str(e))
        self.cleaned_data['report'] = report


