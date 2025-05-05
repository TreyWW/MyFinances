import json
from django.core.management.base import BaseCommand
from redis import Redis
from django.utils.dateparse import parse_datetime

from feeds.models import FeedSource, FeedEntry


class Command(BaseCommand):
    help = "Subscribe to RSS pub/sub channels and save FeedEntry records"

    def handle(self, *args, **options):
        # 1. Connect to Redis
        redis_client = Redis(host="localhost", port=6379, db=0)
        pubsub = redis_client.pubsub(ignore_subscribe_messages=True)

        # 2. Build channel list from active FeedSources
        slugs = FeedSource.objects.filter(is_active=True).values_list("slug", flat=True)
        channels = [f"finance.rss.{slug}" for slug in slugs]
        pubsub.subscribe(*channels)
        self.stdout.write(self.style.SUCCESS(f"Subscribed to: {channels}"))

        # 3. Listen for messages indefinitely
        for message in pubsub.listen():
            try:
                data = json.loads(message["data"])
                src = FeedSource.objects.get(slug=data["source"])
                # 4. Create FeedEntry
                FeedEntry.objects.create(
                    source=src,
                    title=data["title"],
                    link=data["link"],
                    summary=data.get("summary", ""),
                    published=parse_datetime(data.get("published")),
                )
                self.stdout.write(f"Saved: {data['title']}")
            except Exception as e:
                # avoid crashing on bad data
                self.stderr.write(f"Error processing message: {e}")
