import csv
from io import StringIO

from django.core.management.base import BaseCommand

from music_publisher.models import ACKImport
from music_publisher.societies import SOCIETY_DICT


class Command(BaseCommand):
    help = (
        "Inspect existing data for compatibility with proposed changes. "
        "No check option displays this help."
    )

    def add_arguments(self, parser):
        checks = parser.add_mutually_exclusive_group()
        checks.add_argument(
            "--all",
            action="store_true",
            help="Run all implemented checks.",
        )
        checks.add_argument(
            "--ack-xrf",
            action="store_true",
            help="Summarize XRF fields found in imported ACK files.",
        )
        parser.add_argument(
            "--output",
            choices=("table", "csv"),
            default="table",
            help="Output format (default: table).",
        )

    def handle(self, *args, **options):
        if not (options["all"] or options["ack_xrf"]):
            parser = self.create_parser("manage.py", "evaluate_suggestions")
            self.stdout.write(parser.format_help(), ending="")
            return

        acknowledgements = ACKImport.objects.only(
            "society_code", "society_name", "cwr"
        )
        total = acknowledgements.count()
        self.stderr.write(
            "Scanning {} ACK imports for XRF records.".format(total)
        )
        rows = self.get_ack_xrf_summary(
            acknowledgements,
            progress_callback=self.report_progress,
            total=total,
        )
        self.write_rows(
            rows,
            (
                "ACK sender",
                "XRF organisation",
                "Identifier type",
                "Validity",
                "Count",
            ),
            options["output"],
        )

    def report_progress(self, scanned, xrf_records, total):
        self.stderr.write(
            "Scanned {}/{} ACK imports; found {} XRF records.".format(
                scanned, total, xrf_records
            )
        )

    @staticmethod
    def get_ack_xrf_summary(
        acknowledgements=None, progress_callback=None, total=None
    ):
        counts = {}
        if acknowledgements is None:
            acknowledgements = ACKImport.objects.only(
                "society_code", "society_name", "cwr"
            )
        if total is None:
            total = acknowledgements.count()
        scanned = 0
        xrf_records = 0
        for society_code, society_name, cwr in acknowledgements.values_list(
            "society_code", "society_name", "cwr"
        ).iterator(chunk_size=100):
            xrf_records += Command.add_ack_xrf_counts(
                counts, society_code, society_name, cwr
            )
            scanned += 1
            if progress_callback and (
                scanned == total or scanned % 100 == 0
            ):
                progress_callback(scanned, xrf_records, total)

        return [(*key, count) for key, count in sorted(counts.items())]

    @staticmethod
    def add_ack_xrf_counts(counts, society_code, society_name, cwr):
        sender = "{} - {}".format(society_code, society_name)
        xrf_records = 0
        for record in StringIO(cwr):
            if not record.startswith("XRF"):
                continue
            organisation_code = record[19:22].strip()
            identifier_type = record[36:37].strip()
            validity = record[37:38].strip()
            organisation_name = {
                "ISW": "ISWC",
                "ISR": "ISRC",
            }.get(
                organisation_code,
                SOCIETY_DICT.get(organisation_code, "Unknown"),
            )
            organisation = "{} - {}".format(
                organisation_code, organisation_name
            )
            key = (sender, organisation, identifier_type, validity)
            counts[key] = counts.get(key, 0) + 1
            xrf_records += 1
        return xrf_records

    def write_rows(self, rows, headers, output_format):
        if output_format == "csv":
            writer = csv.writer(self.stdout)
            writer.writerow(headers)
            writer.writerows(rows)
            return

        values = [headers, *rows]
        widths = [
            max(len(str(row[index])) for row in values)
            for index in range(len(headers))
        ]
        separator = "+-" + "-+-".join("-" * width for width in widths) + "-+"
        self.stdout.write(separator)
        for index, row in enumerate(values):
            self.stdout.write(
                "| "
                + " | ".join(
                    str(value).ljust(widths[column])
                    for column, value in enumerate(row)
                )
                + " |"
            )
            if index == 0:
                self.stdout.write(separator)
        self.stdout.write(separator)
