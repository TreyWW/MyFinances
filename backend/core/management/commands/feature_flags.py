from django.core.management.base import BaseCommand
from django.db.models.functions import Length
from django.utils.termcolors import colorize
from backend.models import FeatureFlags


class Command(BaseCommand):
    help = "Manage the feature flag statuses"

    def add_arguments(self, parser):
        parser.add_argument("action", type=str, help="enable, disable or list")
        parser.add_argument("flag", type=str, nargs="?", help="feature flag name")
        # parser.add_argument("-f", type=str, dest="flag", help="feature flag name")

    #
    def handle(self, *args, **kwargs):
        if kwargs["action"] == "list":
            flags = FeatureFlags.objects.annotate(name_len=Length("name"), description_len=Length("description"))
            width = flags.order_by("-name_len").first().name_len + 4
            description_width = flags.order_by("-description_len").first().description_len + 4

            header = "{:<{width}} {:<10} {:<{description_width}} {:<20}".format(
                "Name", "Enabled", "Description", "Last updated", width=width, description_width=description_width
            )
            self.stdout.write("Feature flags:")
            self.stdout.write(header)

            for flag in FeatureFlags.objects.all():
                value = "✔" if flag.value else "❌"

                formatted_date = flag.updated_at.strftime("%Y-%m-%d %H:%M:%S")
                row = "{:<{width}} {:<10} {:<{description_width}} {:<20}".format(
                    flag.name, value, flag.description or "No description", formatted_date, width=width, description_width=description_width
                )
                self.stdout.write(row)
            return

        if not kwargs["flag"]:
            self.stdout.write(
                colorize("Please provide a feature flag name with `feature_flags enable|disable <name>`", fg="red", opts=("bold",))
            )
            return

        try:
            flag = FeatureFlags.objects.get(name=kwargs["flag"])

            if kwargs["action"] == "enable":
                flag.enable()
                self.stdout.write(f"[👍] Feature flag {kwargs['flag']} has been enabled")
            elif kwargs["action"] == "disable":
                flag.disable()
                self.stdout.write(f"[👍] Feature flag {kwargs['flag']} has been disabled")
        except FeatureFlags.DoesNotExist:
            self.stdout.write(colorize("Feature flag  with the name of `{kwargs['flag']}` does not exist", fg="red", opts=("bold",)))
            return
