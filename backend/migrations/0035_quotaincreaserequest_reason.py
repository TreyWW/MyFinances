# Generated by Django 5.0.4 on 2024-04-19 15:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("backend", "0034_invoice_client_email_invoicereminder"),
    ]

    operations = [
        migrations.AddField(
            model_name="quotaincreaserequest",
            name="reason",
            field=models.CharField(default="", max_length=1000),
            preserve_default=False,
        ),
    ]
