import os
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
import feeds.routing

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings.settings")

application = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),
        "websocket": URLRouter(feeds.routing.websocket_urlpatterns),
    }
)
