from django.db.models.signals import post_save
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import json

from .models import FeedEntry


@receiver(post_save, sender=FeedEntry)
def announce_new_entry(sender, instance, created, **kwargs):
    if not created:
        return
    layer = get_channel_layer()
    payload = {
        "source": instance.source.slug,
        "title": instance.title,
        "link": instance.link,
        "published": instance.published.isoformat(),
    }
    async_to_sync(layer.group_send)("feeds_updates", {"type": "new_feed_entry", "text": json.dumps(payload)})
