from django.core.management.base import BaseCommand
from backend.core.service.maintenance.expire.run import expire_and_cleanup_objects


class Command(BaseCommand):
    """
    Runs automation scripts to make sure objects are up to date, expired objects are deleted, etc.
    """

    def handle(self, *args, **kwargs):
        self.stdout.write("Running expire + cleanup script...")
        self.stdout.write(expire_and_cleanup_objects())
