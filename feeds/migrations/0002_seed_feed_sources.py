from django.db import migrations


def create_feed_sources(apps, schema_editor):
    FeedSource = apps.get_model("feeds", "FeedSource")
    sources = [
        ("Reuters Business", "http://feeds.reuters.com/reuters/businessNews", "reuters-business"),
        ("Reuters Markets", "http://feeds.reuters.com/reuters/marketsNews", "reuters-markets"),
        ("MarketWatch Top Stories", "https://feeds.content.dowjones.io/public/rss/mw_topstories", "marketwatch-top"),
        ("CNBC – Finance", "https://www.cnbc.com/id/10000664/device/rss/rss.html", "cnbc-finance"),
        ("Seeking Alpha – Market Currents", "https://seekingalpha.com/market_currents.xml", "seeking-alpha"),
        ("Investing.com – News", "https://www.investing.com/rss/news.rss", "investing-news"),
        (
            "Investopedia – Headline News",
            "https://www.investopedia.com/feedbuilder/feed/getfeed/?feedName=rss_headline",
            "investopedia-headline",
        ),
        ("Financial Times – Home", "https://www.ft.com/?format=rss", "financial-times"),
    ]
    for name, url, slug in sources:
        FeedSource.objects.update_or_create(slug=slug, defaults={"name": name, "url": url, "is_active": True})


def delete_feed_sources(apps, schema_editor):
    FeedSource = apps.get_model("feeds", "FeedSource")
    slugs = [
        "reuters-business",
        "reuters-markets",
        "marketwatch-top",
        "cnbc-finance",
        "seeking-alpha",
        "investing-news",
        "investopedia-headline",
        "financial-times",
    ]
    FeedSource.objects.filter(slug__in=slugs).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("feeds", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(create_feed_sources, delete_feed_sources),
    ]
