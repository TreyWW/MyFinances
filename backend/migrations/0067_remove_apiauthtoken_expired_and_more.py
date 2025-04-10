# Generated by Django 5.1.1 on 2024-10-19 19:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("backend", "0066_delete_apikey_remove_verificationcodes_expiry_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="apiauthtoken",
            name="expired",
        ),
        migrations.AlterField(
            model_name="apiauthtoken",
            name="active",
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name="apiauthtoken",
            name="expires",
            field=models.DateTimeField(blank=True, help_text="When the item will expire", null=True, verbose_name="Expires"),
        ),
    ]
