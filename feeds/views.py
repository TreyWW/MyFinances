from django.shortcuts import render
from .models import FeedEntry

def feed_list(request):
    entries = FeedEntry.objects.order_by("-published")[:20]
    return render(request, "feeds/list.html", {"entries": entries})
