# Generated by Django 5.0.7 on 2024-08-09 18:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("backend", "0047_apiauthtoken_administrator_service_type"),
    ]

    operations = [
        migrations.RenameModel(
            old_name="InvoiceRecurringSet",
            new_name="InvoiceRecurringProfile",
        ),
        migrations.RemoveConstraint(
            model_name="invoicerecurringprofile",
            name="backend_invoicerecurringset_check_user_or_organization",
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