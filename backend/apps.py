from django.apps import AppConfig


class BackendConfig(AppConfig):
    name = "backend"

    def ready(self):
        # import backend.signals
        # Need to import signals if we use signals.py
        pass
