import json
from channels.generic.websocket import AsyncWebsocketConsumer

class FeedConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("feeds_updates", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("feeds_updates", self.channel_name)

    async def new_feed_entry(self, event):
        feed_entry = json.loads(event["text"])
        await self.send(text_data=json.dumps({
            "title": feed_entry["title"],
            "link": feed_entry["link"],
            "summary": feed_entry.get("summary", ""),  # Handle missing summary
            "published": feed_entry["published"],
        }))