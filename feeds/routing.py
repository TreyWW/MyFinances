from django.urls import path
from .consumers import FeedConsumer

websocket_urlpatterns = [
    path("ws/feeds/", FeedConsumer.as_asgi()),
]
