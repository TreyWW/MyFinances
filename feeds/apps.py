from django.apps import AppConfig

class FeedsConfig(AppConfig):
    name = "feeds"           # Must match your app folder name exactly
    verbose_name = "RSS Feeds"

    def ready(self):
        # Only here, after all apps are loaded, do we import signals
        import feeds.signals  # noqa
