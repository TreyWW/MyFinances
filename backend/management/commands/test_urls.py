from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    help = "Runs URL verification tests."

    def handle(self, *args, **options):
        call_command("test", "backend.tests.urls.verify_urls")
