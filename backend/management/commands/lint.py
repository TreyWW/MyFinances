import subprocess

from django.core.management import BaseCommand


class Command(BaseCommand):
    help = "Run linters"
    requires_system_checks = []
    requires_migrations_checks = False

    def add_arguments(self, parser):
        parser.add_argument("action", type=str, help="djlint or black")  # parser.add_argument("-f", type=str, dest="flag",

    def handle(self, *args, **kwargs):
        if kwargs["action"] == "djlint":
            djlint()
        elif kwargs["action"] == "black":
            black()


def djlint():
    subprocess.run(["djlint", "./frontend/templates/", "--reformat"])


def black():
    subprocess.run(["black", "./"])
