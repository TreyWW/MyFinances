import os
from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    help = "Runs verification tests for view files in backend/tests/views."

    def add_arguments(self, parser):
        parser.add_argument(
            "test_label",
            nargs="?",
            type=str,
            help="Test label for a specific view file.",
        )

    def handle(self, *args, **options):
        test_dir = "backend/tests/views"
        test_label = options["test_label"]

        if test_label:
            self.run_test("backend.tests.views." + test_label)
        else:
            for root, dirs, files in os.walk(test_dir):
                for file in files:
                    if file.endswith(".py") and file != "__init__.py":
                        test_module = file.replace(".py", "")
                        test_label = f"MAIN.tests.views.{test_module}"
                        self.run_test(test_label)

    def run_test(self, test_label):
        self.stdout.write(self.style.SUCCESS(f"Running tests for {test_label}"))
        call_command("test", test_label)
