# Generated by Django 5.1 on 2024-08-23 11:54

import backend.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("backend", "0047_defaultvalues_default_invoice_logo"),
    ]

    operations = [
        migrations.AlterField(
            model_name="defaultvalues",
            name="default_invoice_logo",
            field=models.ImageField(blank=True, null=True, storage=backend.models._private_storage, upload_to="invoice_logos/"),
        ),
    ]