# Generated by Django 5.0.3 on 2024-03-31 20:27

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("backend", "0026_invoice_discount_amount_invoice_discount_percentage"),
    ]

    operations = [
        migrations.CreateModel(
            name="QuotaLimit",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("slug", models.CharField(editable=False, max_length=100, unique=True)),
                ("name", models.CharField(editable=False, max_length=100, unique=True)),
                ("description", models.TextField(blank=True, max_length=500, null=True)),
                ("value", models.IntegerField()),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("adjustable", models.BooleanField(default=True)),
                (
                    "limit_type",
                    models.CharField(
                        choices=[
                            ("per_month", "Per Month"),
                            ("per_day", "Per Day"),
                            ("per_client", "Per Client"),
                            ("per_invoice", "Per Invoice"),
                            ("per_team", "Per Team"),
                            ("per_quota", "Per Quota"),
                            ("forever", "Forever"),
                        ],
                        default="per_month",
                        max_length=20,
                    ),
                ),
            ],
            options={
                "verbose_name": "Quota Limit",
                "verbose_name_plural": "Quota Limits",
            },
        ),
        migrations.CreateModel(
            name="QuotaIncreaseRequest",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("new_value", models.IntegerField()),
                ("current_value", models.IntegerField()),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "status",
                    models.CharField(
                        choices=[("pending", "Pending"), ("approved", "Approved"), ("rejected", "Rejected")],
                        default="pending",
                        max_length=20,
                    ),
                ),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                (
                    "quota_limit",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, related_name="quota_increase_requests", to="backend.quotalimit"
                    ),
                ),
            ],
            options={
                "verbose_name": "Quota Increase Request",
                "verbose_name_plural": "Quota Increase Requests",
            },
        ),
        migrations.CreateModel(
            name="QuotaOverrides",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("value", models.IntegerField()),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "quota_limit",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="quota_overrides", to="backend.quotalimit"),
                ),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "verbose_name": "Quota Override",
                "verbose_name_plural": "Quota Overrides",
            },
        ),
        migrations.CreateModel(
            name="QuotaUsage",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("extra_data", models.IntegerField(blank=True, null=True)),
                (
                    "quota_limit",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="quota_usage", to="backend.quotalimit"),
                ),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "verbose_name": "Quota Usage",
                "verbose_name_plural": "Quota Usage",
            },
        ),
    ]
