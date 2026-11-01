import time

from django.apps import apps
from django.core.exceptions import ImproperlyConfigured
from django.core.management.base import BaseCommand, CommandError

from music_publisher.models import CWRExport


class Command(BaseCommand):
    help = (
        "Generate the oldest pending CWR export. "
        "Exports marked as stopped are skipped unless --force is used."
    )

    def add_arguments(self, parser):
        modes = parser.add_mutually_exclusive_group()
        modes.add_argument(
            "--regenerate",
            type=int,
            metavar="ID",
            help="Regenerate this existing CWR export.",
        )
        modes.add_argument(
            "--duplicate",
            type=int,
            metavar="ID",
            help="Create and generate a copy of this export's type and works.",
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help=(
                'Ignore the "stop" marker and retry CWR generation. '
                "Use this only after checking the previous error or making sure "
                "no other generation process is still running."
            ),
        )
        parser.add_argument(
            "--code",
            help="Override the configured publisher code for the HDR and filename.",
        )
        parser.add_argument(
            "--ipi_name",
            help="Use the publisher with this IPI name number as the CWR sender.",
        )
        parser.add_argument(
            "--description",
            help="Set the export description.",
        )

    def handle(self, *args, **options):
        publisher = self.get_publisher(options["ipi_name"])
        publisher_code = options["code"]
        if options["regenerate"] is not None or options["duplicate"] is not None:
            publisher_code = self.resolve_publisher_code(publisher_code)

        cwr_exports = self.get_exports(options)
        if not cwr_exports:
            self.stdout.write(self.style.SUCCESS("No pending CWR exports."))
            return

        explicit_export = (
            options["regenerate"] is not None or options["duplicate"] is not None
        )
        self.generate_exports(
            cwr_exports, options, publisher, publisher_code, explicit_export
        )

    def generate_exports(
        self, cwr_exports, options, publisher, publisher_code, explicit_export
    ):
        for cwr_export in cwr_exports:
            if self.generate_export(
                cwr_export, options, publisher, publisher_code, explicit_export
            ):
                return

    def generate_export(
        self, cwr_export, options, publisher, publisher_code, explicit_export
    ):
        description = self.prepare_export_description(
            cwr_export, options, explicit_export
        )
        self.stdout.write(
            "Generating CWR #{id} ({description})...".format(
                id=cwr_export.id,
                description=description or "no description",
            )
        )

        duration = self.create_export(
            cwr_export, options, publisher, publisher_code
        )
        if not cwr_export.cwr:
            self.report_generation_failure(cwr_export, duration)
            return False

        self.report_generation_success(
            cwr_export, duration, options, explicit_export
        )
        return True

    @staticmethod
    def prepare_export_description(cwr_export, options, explicit_export):
        if explicit_export and options["description"] is not None:
            cwr_export.description = options["description"]
            cwr_export.save(update_fields=["description"])

        return (
            options["description"]
            if options["description"] is not None
            else cwr_export.description
        )

    @staticmethod
    def create_export(cwr_export, options, publisher, publisher_code):
        started_at = time.monotonic()
        try:
            cwr_export.create_cwr(
                publisher_code=publisher_code,
                generate=True,
                force=options["force"],
                publisher_name=publisher.name if publisher else None,
                publisher_ipi_name=publisher.ipi_name if publisher else None,
            )
        except ImproperlyConfigured as exc:
            raise CommandError(str(exc)) from exc
        return time.monotonic() - started_at

    def report_generation_success(
        self, cwr_export, duration, options, explicit_export
    ):
        if not explicit_export and options["description"] is not None:
            cwr_export.description = options["description"]
            cwr_export.save(update_fields=["description"])
        self.stdout.write(
            self.style.SUCCESS(
                "Generated CWR export #{id}: {filename} ({duration:.2f}s)".format(
                    id=cwr_export.id,
                    filename=cwr_export.filename,
                    duration=duration,
                )
            )
        )

    def report_generation_failure(self, cwr_export, duration):
        options_state = cwr_export.options or {}
        if options_state.get("stop") and options_state.get("error"):
            self.stderr.write(
                self.style.WARNING(
                    "CWR generation #{id} stopped: {error} ({duration:.2f}s)".format(
                        id=cwr_export.id,
                        error=options_state["error"],
                        duration=duration,
                    )
                )
            )
        elif options_state.get("stop"):
            self.stderr.write(
                self.style.SUCCESS(
                    "Another CWR generation running for #{id}. ({duration:.2f}s)".format(
                        id=cwr_export.id,
                        duration=duration,
                    )
                )
            )
        else:
            self.stderr.write(
                self.style.SUCCESS(
                    "Failed CWR generation #{id}: {error} ({duration:.2f}s)".format(
                        id=cwr_export.id,
                        error=options_state.get("error", "unknown error"),
                        duration=duration,
                    )
                )
            )

    @staticmethod
    def resolve_publisher_code(publisher_code):
        try:
            return CWRExport.resolve_publisher_code(publisher_code)
        except ImproperlyConfigured as exc:
            raise CommandError(str(exc)) from exc

    @staticmethod
    def get_export(export_id):
        try:
            return CWRExport.objects.get(pk=export_id)
        except CWRExport.DoesNotExist as exc:
            raise CommandError(
                "No CWR export found with ID {}.".format(export_id)
            ) from exc

    @classmethod
    def get_exports(cls, options):
        if options["regenerate"] is not None:
            cwr_export = cls.get_export(options["regenerate"])
            if (cwr_export.options or {}).get("stop") and not options["force"]:
                raise CommandError(
                    "CWR export #{} is stopped; use --force to regenerate it.".format(
                        cwr_export.pk
                    )
                )
            cwr_export.cwr = ""
            cwr_export.created_on = None
            cwr_export.year = ""
            cwr_export.num_in_year = 0
            cwr_export.options = {}
            cwr_export.save()
            return [cwr_export]

        if options["duplicate"] is not None:
            source = cls.get_export(options["duplicate"])
            cwr_export = CWRExport.objects.create(
                nwr_rev=source.nwr_rev,
                description=options["description"] or "",
            )
            cwr_export.works.set(source.works.all())
            return [cwr_export]

        return CWRExport.objects.filter(cwr="").order_by("id")

    @staticmethod
    def get_publisher(ipi_name):
        if ipi_name is None:
            return None

        try:
            publisher_model = apps.get_model("that_green_thing", "Publisher")
        except LookupError as exc:
            raise CommandError(
                "Publisher lookup requires the That Green Thing app."
            ) from exc

        try:
            return publisher_model.objects.get(ipi_name=ipi_name)
        except publisher_model.DoesNotExist as exc:
            raise CommandError(
                "No publisher found with IPI name number {!r}.".format(ipi_name)
            ) from exc
        except publisher_model.MultipleObjectsReturned as exc:
            raise CommandError(
                "Multiple publishers found with IPI name number {!r}.".format(
                    ipi_name
                )
            ) from exc
