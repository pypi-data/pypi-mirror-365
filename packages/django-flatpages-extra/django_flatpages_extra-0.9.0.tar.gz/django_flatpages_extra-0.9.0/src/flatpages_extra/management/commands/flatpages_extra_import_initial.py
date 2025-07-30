from django.contrib.admin.models import LogEntry
from django.contrib.contenttypes.models import ContentType
from django.contrib.flatpages.models import FlatPage as OriginalFlatPage
from django.core.management.base import BaseCommand
from django.utils.translation import ngettext

from flatpages_extra.models import FlatPage, Revision


class Command(BaseCommand):
    help = (
        "Create revisions for existing contrib.FlatPages and import their history too"
    )

    def handle(self, **options):
        revisions = self.create_initial_revisions()
        if options["verbosity"] > 0:
            self.stdout.write(
                self.style.SUCCESS(
                    ngettext(
                        "Successfully imported {} revision",
                        "Successfully imported {} revisions",
                        len(revisions),
                    ).format(len(revisions))
                )
            )

        logentries = self.copy_logentries()
        if options["verbosity"] > 0:
            self.stdout.write(
                self.style.SUCCESS(
                    ngettext(
                        "Successfully copied {} log entry",
                        "Successfully copied {} log entries",
                        len(logentries),
                    ).format(len(logentries))
                )
            )

    def create_initial_revisions(self):
        revisions = [
            Revision(
                page=page,
                content=page.content,
                description="Initial flatpages-extra import.",
                status=Revision.Status.PUBLISHED,
            )
            for page in FlatPage.objects.all()
        ]
        return Revision.objects.bulk_create(revisions)

    def copy_logentries(self):
        ct_original = ContentType.objects.get_for_model(OriginalFlatPage)
        ct_new = ContentType.objects.get_for_model(FlatPage, for_concrete_model=False)

        entries = LogEntry.objects.filter(content_type=ct_original)
        for e in entries:
            e.pk = None
            e._state.adding = True
            e.content_type = ct_new

        return LogEntry.objects.bulk_create(entries)
