"Forms and formsets."

import re
from datetime import datetime
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.forms import (
    BooleanField,
    FileField,
    ModelForm,
    NullBooleanField,
    Select,
)
from django.forms.models import BaseInlineFormSet
from django.urls import reverse

from .models import ACKImport, Work


class LibraryReleaseForm(ModelForm):
    """Custom form for :class:`.models.LibraryRelease`."""

    def __init__(self, *args, **kwargs):
        """Make cd_identifier and library fields required."""
        super().__init__(*args, **kwargs)
        self.fields["cd_identifier"].required = True
        self.fields["library"].required = True


class PlaylistForm(ModelForm):
    """Custom form for :class:`.models.LibraryRelease`."""

    def __init__(self, *args, **kwargs):
        """Make cd_identifier and library fields required."""
        super().__init__(*args, **kwargs)
        self.fields["release_title"].required = True
        self.fields["release_title"].label = "Playlist title"
        self.fields["release_date"].label = "Valid Until"


class AlternateTitleFormSet(BaseInlineFormSet):
    """Formset for :class:`AlternateTitleInline`."""

    orig_cap = ["C ", "A ", "CA"]

    def clean(self):
        """Performs these checks:
            if suffix is used, then validates the total length

        Returns:
            None

        Raises:
            ValidationError
        """
        super().clean()
        work_title_len = len(self.instance.title)
        for form in self.forms:
            if not form.is_valid():
                return
            if form.cleaned_data and not form.cleaned_data.get("DELETE"):
                if not form.cleaned_data.get("suffix"):
                    continue
                title_suffix_len = len(form.cleaned_data["title"])
                if work_title_len + title_suffix_len > 60 - 1:
                    form.add_error(
                        "title",
                        "Too long for suffix, work title plus suffix must be "
                        "59 characters or less.",
                    )


class WorkForm(ModelForm):
    """Custom form for :class:`.models.Work`.

    Calculate values for readonly field version_type."""

    class Meta:
        model = Work
        fields = ["title", "iswc", "original_title", "library_release"]

    version_type = NullBooleanField(
        widget=Select(
            choices=(
                (None, ""),
                (True, "Modification"),
                (False, "Original Work"),
            )
        ),
        disabled=True,
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["version_type"].initial = self.instance.is_modification()


class ACKImportForm(ModelForm):
    """Form used for CWR acknowledgement imports.

    Attributes:
        acknowledgement_file (FileField): Field for file upload
    """

    class Meta:
        model = ACKImport
        fields = ("acknowledgement_file", "import_iswcs")

    acknowledgement_file = FileField()
    import_iswcs = BooleanField(
        label="Import ISWCs if present", required=False, initial=True
    )

    RE_HDR_21 = re.compile(
        r"^HDR(?:SO|AA)([ \d]{9})(.{45})01\.10(\d{8})\d{6}(\d{8})"
    )

    RE_HDR_30 = re.compile(
        r"^HDR(?:SO|AA)(.{4})(.{45})(\d{8})\d{6}(\d{8}).{15}3\.0000"
    )

    def clean(self):
        """Perform usual clean, then process the file, returning the content
        field as if it was the TextField."""
        super().clean()
        cd = self.cleaned_data
        ack = cd.get("acknowledgement_file")
        if not ack:
            return
        filename = ack.name
        if not (
            len(filename) in [18, 19]
            and filename[-4:].upper() in [".V21", ".V22"]
        ):
            raise ValidationError("Wrong file name format.")
        self.cleaned_data["filename"] = filename
        content = ack.file.read().decode("latin1")
        match = re.match(self.RE_HDR_21, content)
        if not match:
            match = re.match(self.RE_HDR_30, content)
        if not match:
            raise ValidationError("Incorrect CWR header")
        code, name, date1, date2 = match.groups()
        self.cleaned_data["society_code"] = code.strip().lstrip("0")
        self.cleaned_data["society_name"] = name.strip()
        self.cleaned_data["date"] = datetime.strptime(
            max([date1, date2]), "%Y%m%d"
        ).date()
        self.cleaned_data["acknowledgement_file"] = content


class WriterInWorkFormSet(BaseInlineFormSet):
    """Formset for :class:`WriterInWorkInline`."""

    orig_cap = ["C ", "A ", "CA"]

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
            if form.cleaned_data and not form.cleaned_data.get("DELETE"):
                writer = form.cleaned_data["writer"]
                writers.append(writer)
                total += form.cleaned_data["relative_share"]
                if form.cleaned_data["controlled"]:
                    controlled = True
                if form.cleaned_data["capacity"] in ["C ", "CA"]:
                    has_composer = True
                if (
                    not is_modification
                    and form.cleaned_data["capacity"]
                    and form.cleaned_data["capacity"] not in self.orig_cap
                ):
                    form.add_error(
                        "capacity", "Not allowed in original works."
                    )
                if (
                    is_modification
                    and form.cleaned_data["capacity"]
                    and form.cleaned_data["capacity"] not in self.orig_cap
                ):
                    needs_extended_capacity = False
        if needs_extended_capacity:
            for form in self.forms:
                form.add_error(
                    "capacity",
                    "At least one must be Arranger, Adaptor or Translator.",
                )
            raise ValidationError(
                "In a modified work, "
                "at least one writer must be Arranger, Adaptor or Translator."
            )
        if not controlled:
            for form in self.forms:
                form.add_error(
                    "controlled", "At least one writer must be controlled."
                )
            raise ValidationError("At least one writer must be controlled.")
        if not has_composer:
            for form in self.forms:
                form.add_error(
                    "capacity",
                    "At least one writer must be Composer or "
                    "Composer&Lyricist.",
                )
            raise ValidationError(
                "At least one writer must be Composer or Composer&Lyricist."
            )
        if not (Decimal(99.98) <= total <= Decimal(100.02)):
            for form in self.forms:
                form.add_error(
                    "relative_share", "Sum of manuscript shares must be 100%."
                )
            raise ValidationError("Sum of manuscript shares must be 100%.")
        if is_modification:
            writer_capacities = {}
            for form in self.forms:
                cd = form.cleaned_data
                if cd["controlled"]:
                    writer_capacities[cd["writer"].id] = cd["capacity"]
            for form in self.forms:
                cd = form.cleaned_data
                if cd["writer"] and not cd["controlled"]:
                    controlled_capacity = writer_capacities.get(
                        cd["writer"].id
                    )
                    if (
                        controlled_capacity
                        and cd["capacity"] != controlled_capacity
                    ):
                        form.add_error(
                            "capacity",
                            "Must be same as in controlled line for this "
                            "writer.",
                        )


class DataImportForm(ModelForm):
    """Form used for data imports.

    Attributes:
        data_file (FileField): Field for file upload
    """

    class Meta:
        model = ACKImport
        fields = ("data_file",)

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
        f = cd.get("data_file")
        report = ""
        with transaction.atomic():
            try:
                importer = DataImporter(TextIOWrapper(f), self.user)
                for work in importer.run():
                    url = reverse(
                        "admin:music_publisher_work_change", args=(work.id,)
                    )
                    report += '<a href="{}">{}</a> {}<br/>\n'.format(
                        url, work.work_id, work.title
                    )
                if importer.unknown_keys:
                    if cd.get("ignore_unknown_columns"):
                        report += "<br>\nUNKNOWN COLUMN NAMES:<br>\n"
                        report += "<br>\n".join(
                            [
                                f"- {key}"
                                for key in sorted(importer.unknown_keys)
                            ]
                        )
                    else:
                        raise ValidationError(
                            "Unknown columns: "
                            + ", ".join(importer.unknown_keys)
                        )
                report += importer.report
            except Exception as e:  # user garbage, too many possibilities
                raise ValidationError(str(e))
        self.cleaned_data["report"] = report
