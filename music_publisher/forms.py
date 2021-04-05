from django.forms import ModelForm, FileField, BooleanField
from .models import ACKImport
from django.core.exceptions import ValidationError
from django.urls import reverse


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


