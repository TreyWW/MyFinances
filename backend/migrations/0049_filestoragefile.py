# Generated by Django 5.1 on 2024-08-25 20:16

import backend.models
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("backend", "0048_alter_defaultvalues_default_invoice_logo"),
    ]

    operations = [
        migrations.CreateModel(
            name="FileStorageFile",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "file",
                    models.FileField(storage=backend.core.models.get_private_storage, upload_to=backend.core.models.get_file_upload_path),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "last_edited_by",
                    models.ForeignKey(
                        blank=True,
                        editable=False,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="files_edited",
                        to=settings.AUTH_USER_MODEL,
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
                        name="backend_filestoragefile_check_user_or_organization",
                    )
                ],
            },
        ),
    ]
