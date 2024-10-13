from django.apps import AppConfig


class BackendConfig(AppConfig):
    name = "backend"

    def ready(self):
        from .finance import signals
        from .core import signals

        # from .clients import signals
        # from .storage import signals
        # from .events import signals
        pass
