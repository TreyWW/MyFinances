# Generated by Django 5.1 on 2024-09-08 13:50

import django.db.models.deletion
import django.db.models.manager
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("backend", "0058_organization_entitlements_and_more"),
    ]

    operations = [
        migrations.AlterModelManagers(
            name="invoicerecurringprofile",
            managers=[
                ("with_items", django.db.models.manager.Manager()),
            ],
        ),
        migrations.CreateModel(
            name="MonthlyReportRow",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("date", models.DateField()),
                ("reference_number", models.CharField(max_length=100)),
                ("item_type", models.CharField(max_length=100)),
                ("client_name", models.CharField(blank=True, max_length=64, null=True)),
                ("paid_in", models.DecimalField(decimal_places=2, default=0, max_digits=15)),
                ("paid_out", models.DecimalField(decimal_places=2, default=0, max_digits=15)),
                ("client", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to="backend.client")),
            ],
        ),
        migrations.CreateModel(
            name="MonthlyReport",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("uuid", models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ("name", models.CharField(blank=True, max_length=100, null=True)),
                ("profit", models.DecimalField(decimal_places=2, default=0, max_digits=15)),
                ("invoices_sent", models.PositiveIntegerField(default=0)),
                ("start_date", models.DateField()),
                ("end_date", models.DateField()),
                ("recurring_customers", models.PositiveIntegerField(default=0)),
                ("payments_in", models.DecimalField(decimal_places=2, default=0, max_digits=15)),
                ("payments_out", models.DecimalField(decimal_places=2, default=0, max_digits=15)),
                (
                    "currency",
                    models.CharField(
                        choices=[
                            ("GBP", "British Pound Sterling"),
                            ("EUR", "Euro"),
                            ("USD", "United States Dollar"),
                            ("JPY", "Japanese Yen"),
                            ("INR", "Indian Rupee"),
                            ("AUD", "Australian Dollar"),
                            ("CAD", "Canadian Dollar"),
                        ],
                        default="GBP",
                        max_length=3,
                    ),
                ),
                (
                    "organization",
                    models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to="backend.organization"),
                ),
                (
                    "user",
                    models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
                ),
                ("items", models.ManyToManyField(blank=True, to="backend.monthlyreportrow")),
            ],
            options={
                "abstract": False,
                "constraints": [
                    models.CheckConstraint(
                        check=models.Q(
                            models.Q(("organization__isnull", False), ("user__isnull", True)),
                            models.Q(("organization__isnull", True), ("user__isnull", False)),
                            _connector="OR",
                        ),
                        name="backend_monthlyreport_check_user_or_organization",
                    )
                ],
            },
        ),
    ]
