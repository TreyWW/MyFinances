import base64

from django.core.management import BaseCommand
from django.utils.termcolors import colorize


class Command(BaseCommand):
    help = "Encrypt a value"
    requires_system_checks = []
    requires_migrations_checks = False

    def add_arguments(self, parser):
        parser.add_argument("type", type=str, help="file/text", choices=["file", "text"], default="text")
        parser.add_argument("value", type=str, help="your value")
        # parser.add_argument("encryption", )

    def handle(self, *args, **kwargs):
        if kwargs["type"] == "file":
            with open(kwargs["value"], "r") as file:
                self.stdout.write(colorize(str(base64.b64encode(file.read().encode("ascii"))), fg="green"))
        else:
            self.stdout.write(colorize(str(base64.b64encode(kwargs["value"].encode("ascii"))), fg="green"))

        #  opts=("bold",)))
