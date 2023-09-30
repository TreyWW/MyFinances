from django.core.management.base import BaseCommand
from django.core.cache import cache


class Command(BaseCommand):
    """
    Deletes the "navbar_items" cache and prints a message to the standard output.
    """

    def handle(self, *args, **kwargs):
        cache.delete("navbar_items")
        self.stdout.write("Cleared cache\n")
