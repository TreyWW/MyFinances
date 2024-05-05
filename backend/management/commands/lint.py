import subprocess

from django.core.management import BaseCommand
from django.utils.termcolors import colorize


class Command(BaseCommand):
    help = "Run linters"
    requires_system_checks = []
    requires_migrations_checks = False

    def add_arguments(self, parser):
        parser.add_argument("action", type=str, nargs="?", help="djlint or black")  # parser.add_argument("-f", type=str, dest="flag",

    def handle(self, *args, **kwargs):
        if kwargs["action"] == "djlint":
            djlint()
        elif kwargs["action"] == "black":
            black()
        else:
            self.stdout.write(colorize("Linting with: BLACK FORMATTER", fg="green", opts=("bold",)))
            black()
            self.stdout.write(colorize("Linting with: DJLINT", fg="green", opts=("bold",)))
            djlint()


def djlint():
    subprocess.run(["djlint", "./frontend/templates/", "--reformat"])


def black():
    subprocess.run(["black", "./"])
