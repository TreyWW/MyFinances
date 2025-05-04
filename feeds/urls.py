from django.urls import path
from .views import feed_list

urlpatterns = [
    path("", feed_list, name="feed_list"),
]
