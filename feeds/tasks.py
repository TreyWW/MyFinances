import feedparser, json
from celery import shared_task
from django.utils import timezone
from redis import Redis

from .models import FeedSource


from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from .models import FeedEntry


def broadcast_new_feed_entry(entry):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "feeds_updates",
        {
            "type": "new_feed_entry",
            "text": json.dumps(
                {
                    "title": entry.title,
                    "link": entry.link,
                    "summary": entry.summary,
                    "published": entry.published.isoformat(),
                }
            ),
        },
    )


# 1. Create a Redis client (defaults to localhost:6379)
redis_client = Redis()


@shared_task
def fetch_all_feeds():
    redis_client = Redis(host="localhost", port=6379, db=0)
    for src in FeedSource.objects.filter(is_active=True):
        parsed = feedparser.parse(src.url)
        for entry in parsed.entries:
            if src.feedentry_set.filter(link=entry.link).exists():
                continue

            payload = {
                "source": src.slug,
                "title": entry.title,
                "link": entry.link,
                "summary": entry.get("summary", ""),  # Use .get() to handle missing summary
                "published": None,
            }

            if entry.get("published_parsed"):
                from django.utils.timezone import make_aware
                from datetime import datetime

                dt = datetime(*entry.published_parsed[:6])
                payload["published"] = make_aware(dt).isoformat()

            channel = f"finance.rss.{src.slug}"
            redis_client.publish(channel, json.dumps(payload))
