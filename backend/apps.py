import importlib

from django.apps import AppConfig


class BackendConfig(AppConfig):
    name = "backend"

    def ready(self):
        from .finance import signals

        importlib.import_module("backend.modals")

        # from .clients import signals
        # from .storage import signals
        # from .events import signals
        pass
