# Generated by Django 5.0.2 on 2024-02-22 18:16

import datetime
import uuid

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("backend", "0018_user_role"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="featureflags",
            options={
                "verbose_name": "Feature Flag",
                "verbose_name_plural": "Feature Flags",
            },
        ),
        migrations.AddField(
            model_name="user",
            name="awaiting_email_verification",
            field=models.BooleanField(default=True),
        ),
        migrations.CreateModel(
            name="VerificationCodes",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "uuid",
                    models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
                ),
                ("created", models.DateTimeField(auto_now_add=True)),
                (
                    "expiry",
                    models.DateTimeField(default=datetime.datetime(2024, 2, 22, 21, 16, 55, 46745, tzinfo=datetime.timezone.utc)),
                ),
                (
                    "service",
                    models.CharField(
                        choices=[
                            ("create_account", "Create Account"),
                            ("reset_password", "Reset Password"),
                        ],
                        max_length=14,
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]
