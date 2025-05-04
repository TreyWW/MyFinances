from django.db import models

class FeedSource(models.Model):
    name       = models.CharField(max_length=100)
    url        = models.URLField()
    slug       = models.SlugField(unique=True)
    is_active  = models.BooleanField(default=True)

    def __str__(self): return self.name

class FeedEntry(models.Model):
    source     = models.ForeignKey(FeedSource, on_delete=models.CASCADE)
    title      = models.CharField(max_length=255)
    link       = models.URLField(unique=True)
    published  = models.DateTimeField()
    summary    = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self): return f"{self.source.slug}: {self.title}"