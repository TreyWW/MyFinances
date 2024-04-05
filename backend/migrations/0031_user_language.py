# Generated by Django 5.0.4 on 2024-04-04 21:13
from __future__ import annotations

from django.db import migrations
from django.db import models


class Migration(migrations.Migration):

    dependencies = [
        ("backend", "0030_alter_invoice_items"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="language",
            field=models.CharField(choices=[("en", "English"), ("ru", "Russian")], default="en-us", max_length=10),
        ),
    ]