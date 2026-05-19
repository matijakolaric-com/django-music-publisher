from django.core.management.base import BaseCommand

from music_publisher.models import CWRExport


class Command(BaseCommand):
    help = "Generate the oldest pending CWR export."

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help='Ignore "stop" marker and force CWR generation.',
        )

    def handle(self, *args, **options):
        cwr_exports = CWRExport.objects.filter(cwr="").order_by("id")

        if not cwr_exports:
            self.stdout.write(self.style.SUCCESS("No pending CWR exports."))
            return

        for cwr_export in cwr_exports:

            self.stdout.write(
                "Generating CWR #{id} ({description})...".format(
                    id=cwr_export.id,
                    description=cwr_export.description or "no description",
                )
            )

            cwr_export.create_cwr(generate=True, force=options["force"])

            if cwr_export.cwr:
                self.stdout.write(
                    self.style.SUCCESS(
                        "Generated CWR export #{id}: {filename}".format(
                            id=cwr_export.id,
                            filename=cwr_export.filename,
                        )
                    )
                )
                return

            elif cwr_export.options.get("stop"):
                if cwr_export.options.get("error"):
                    self.stderr.write(
                        self.style.WARNING(
                            "CWR generation #{id} stopped: {error}".format()
                        )
                    )
                else:
                    self.stderr.write(
                        self.style.SUCCESS(
                            "Another CWR generation running for #{id}.".format(
                                id=cwr_export.id,
                            )
                        )
                    )
            else:
                self.stderr.write(
                    self.style.SUCCESS(
                        "Failed CWR generation #{id}: {error}".format(
                            id=cwr_export.id,
                            error=cwr_export.options.get(
                                "error", "unknown error"
                            ),
                        )
                    )
                )
