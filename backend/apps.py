import importlib

from django.apps import AppConfig


class BackendConfig(AppConfig):
    name = "backend"

    def ready(self):
        from .finance import signals
        from .clients import clients

        importlib.import_module("backend.modals")

        # from .clients import signals
        # from .storage import signals
        # from .events import signalsupload_receipt
        pass
