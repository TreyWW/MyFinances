from django.core.management.base import BaseCommand

from backend.models import FeatureFlags


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("flag", type=str, help="Name of the feature flag to disable")

    def handle(self, *args, **kwargs):
        try:
            flag = FeatureFlags.objects.get(name=kwargs["flag"])

            flag.disable()
        except FeatureFlags.DoesNotExist:
            self.stdout.write(f"Feature flag {kwargs['flag']} does not exist")
            return

        self.stdout.write(f"[👍] Feature flag {kwargs['flag']} has been disabled")
