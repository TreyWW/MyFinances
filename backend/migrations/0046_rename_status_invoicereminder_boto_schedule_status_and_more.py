# Generated by Django 5.0.7 on 2024-08-22 15:09

import backend.models
import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("backend", "0045_usersettings_disabled_features"),
    ]

    operations = [
        migrations.RenameField(
            model_name="invoicereminder",
            old_name="status",
            new_name="boto_schedule_status",
        ),
        migrations.RemoveField(
            model_name="invoicereminder",
            name="stored_schedule_arn",
        ),
        migrations.AddField(
            model_name="apiauthtoken",
            name="administrator_service_type",
            field=models.CharField(blank=True, max_length=64, null=True, verbose_name="Administrator Service Type"),
        ),
        migrations.AddField(
            model_name="invoicereminder",
            name="boto_last_updated",
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name="invoicereminder",
            name="boto_schedule_arn",
            field=models.CharField(blank=True, max_length=2048, null=True),
        ),
        migrations.AddField(
            model_name="invoicereminder",
            name="boto_schedule_uuid",
            field=models.UUIDField(blank=True, default=None, null=True),
        ),
        migrations.AlterField(
            model_name="invoice",
            name="logo",
            field=models.ImageField(blank=True, null=True, storage=backend.core.models.get_private_storage, upload_to="invoice_logos"),
        ),
        migrations.AlterField(
            model_name="receipt",
            name="image",
            field=models.ImageField(storage=backend.core.models.get_private_storage, upload_to="receipts"),
        ),
        migrations.AlterField(
            model_name="teammemberpermission",
            name="user",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE, related_name="team_permissions", to=settings.AUTH_USER_MODEL
            ),
        ),
        migrations.AlterField(
            model_name="usersettings",
            name="profile_picture",
            field=models.ImageField(blank=True, null=True, storage=backend.core.models.get_public_storage, upload_to="profile_pictures/"),
        ),
        migrations.CreateModel(
            name="InvoiceRecurringProfile",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("boto_schedule_arn", models.CharField(blank=True, max_length=2048, null=True)),
                ("boto_schedule_uuid", models.UUIDField(blank=True, default=None, null=True)),
                ("boto_last_updated", models.DateTimeField(auto_now=True)),
                ("received", models.BooleanField(default=False)),
                (
                    "boto_schedule_status",
                    models.CharField(
                        choices=[
                            ("pending", "Pending"),
                            ("creating", "Creating"),
                            ("completed", "Completed"),
                            ("failed", "Failed"),
                            ("deleting", "Deleting"),
                            ("cancelled", "Cancelled"),
                        ],
                        default="pending",
                        max_length=100,
                    ),
                ),
                ("client_name", models.CharField(blank=True, max_length=100, null=True)),
                ("client_email", models.EmailField(blank=True, max_length=254, null=True)),
                ("client_company", models.CharField(blank=True, max_length=100, null=True)),
                ("client_address", models.CharField(blank=True, max_length=100, null=True)),
                ("client_city", models.CharField(blank=True, max_length=100, null=True)),
                ("client_county", models.CharField(blank=True, max_length=100, null=True)),
                ("client_country", models.CharField(blank=True, max_length=100, null=True)),
                ("client_is_representative", models.BooleanField(default=False)),
                ("self_name", models.CharField(blank=True, max_length=100, null=True)),
                ("self_company", models.CharField(blank=True, max_length=100, null=True)),
                ("self_address", models.CharField(blank=True, max_length=100, null=True)),
                ("self_city", models.CharField(blank=True, max_length=100, null=True)),
                ("self_county", models.CharField(blank=True, max_length=100, null=True)),
                ("self_country", models.CharField(blank=True, max_length=100, null=True)),
                ("sort_code", models.CharField(blank=True, max_length=8, null=True)),
                ("account_holder_name", models.CharField(blank=True, max_length=100, null=True)),
                ("account_number", models.CharField(blank=True, max_length=100, null=True)),
                ("reference", models.CharField(blank=True, max_length=100, null=True)),
                ("invoice_number", models.CharField(blank=True, max_length=100, null=True)),
                ("vat_number", models.CharField(blank=True, max_length=100, null=True)),
                (
                    "logo",
                    models.ImageField(blank=True, null=True, storage=backend.core.models.get_private_storage, upload_to="invoice_logos"),
                ),
                ("notes", models.TextField(blank=True, null=True)),
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
                ("date_created", models.DateTimeField(auto_now_add=True)),
                ("date_issued", models.DateField(blank=True, null=True)),
                ("discount_amount", models.DecimalField(decimal_places=2, default=0, max_digits=15)),
                (
                    "discount_percentage",
                    models.DecimalField(
                        decimal_places=2, default=0, max_digits=5, validators=[django.core.validators.MaxValueValidator(100)]
                    ),
                ),
                ("active", models.BooleanField(default=True)),
                (
                    "status",
                    models.CharField(
                        choices=[("ongoing", "Ongoing"), ("paused", "paused"), ("cancelled", "cancelled")], default="paused", max_length=10
                    ),
                ),
                (
                    "frequency",
                    models.CharField(
                        choices=[("weekly", "Weekly"), ("monthly", "Monthly"), ("yearly", "Yearly")], default="monthly", max_length=20
                    ),
                ),
                ("end_date", models.DateField(blank=True, null=True)),
                ("due_after_days", models.PositiveSmallIntegerField(default=7)),
                ("day_of_week", models.PositiveSmallIntegerField(blank=True, null=True)),
                ("day_of_month", models.PositiveSmallIntegerField(blank=True, null=True)),
                ("month_of_year", models.PositiveSmallIntegerField(blank=True, null=True)),
                ("client_to", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to="backend.client")),
                ("items", models.ManyToManyField(blank=True, to="backend.invoiceitem")),
                (
                    "organization",
                    models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to="backend.organization"),
                ),
                (
                    "user",
                    models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.AddField(
            model_name="invoice",
            name="invoice_recurring_profile",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="generated_invoices",
                to="backend.invoicerecurringprofile",
            ),
        ),
        migrations.DeleteModel(
            name="InvoiceOnetimeSchedule",
        ),
        migrations.AddConstraint(
            model_name="invoicerecurringprofile",
            constraint=models.CheckConstraint(
                check=models.Q(
                    models.Q(("organization__isnull", False), ("user__isnull", True)),
                    models.Q(("organization__isnull", True), ("user__isnull", False)),
                    _connector="OR",
                ),
                name="backend_invoicerecurringprofile_check_user_or_organization",
            ),
        ),
    ]
