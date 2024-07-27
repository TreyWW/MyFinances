import json
from typing import Type
import logging
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.urls import reverse

from backend.service.boto3.handler import BOTO3_HANDLER
from backend.service.invoices.recurring.schedules.date_handlers import get_schedule_cron, CronServiceResponse

from uuid import uuid4
from backend.models import InvoiceRecurringSet
from settings.helpers import get_var

logger = logging.getLogger(__name__)


def recurring_set_created(instance: InvoiceRecurringSet, **kwargs):
    logger.info(f"Invoice recurring set was just created")

    schedule_uuid: str = instance.schedule_name or str(uuid4())

    if instance.schedule_arn:
        logger.info("Invoice recurring set already has schedule ARN. Leaving.")
        return None

    if not BOTO3_HANDLER.initiated:
        logger.error(f"Boto3 handler not initiated. Cannot use AWS services.")
        return None

    CRON_FREQUENCY_TYPE = instance.frequency.lower()
    CRON_RESPONSE: CronServiceResponse

    if CRON_FREQUENCY_TYPE == "weekly":
        CRON_RESPONSE = get_schedule_cron(frequency=CRON_FREQUENCY_TYPE, day_of_week=instance.day_of_week)
    elif CRON_FREQUENCY_TYPE == "monthly":
        CRON_RESPONSE = get_schedule_cron(frequency=CRON_FREQUENCY_TYPE, day_of_month=instance.day_of_month)

    elif CRON_FREQUENCY_TYPE == "yearly":
        CRON_RESPONSE = get_schedule_cron(frequency=CRON_FREQUENCY_TYPE, day_of_month=instance.day_of_month, month=instance.month_of_year)
    else:
        logger.error(f"Invalid frequency type: {CRON_FREQUENCY_TYPE}")
        return None

    if CRON_RESPONSE.failed:
        logger.error(f"Error getting cron expression: {CRON_RESPONSE.error}")
        return None

    EXCEPTIONS = BOTO3_HANDLER._schedule_client.exceptions

    SITE_URL = get_var("SITE_URL", default="http://127.0.0.1:8000") + reverse("webhooks:receive_scheduled_invoice schedule")

    try:
        boto_response = BOTO3_HANDLER._schedule_client.create_schedule(
            Name=f"{schedule_uuid}",
            GroupName=BOTO3_HANDLER.scheduler_invoices_group_name,
            FlexibleTimeWindow={"Mode": "FLEXIBLE", "MaximumWindowInMinutes": 10},
            ScheduleExpression=f"cron({CRON_RESPONSE.response})",
            Target={
                "Arn": BOTO3_HANDLER.scheduler_lambda_arn,
                "RoleArn": BOTO3_HANDLER.scheduler_lambda_access_role_arn,
                "Input": json.dumps({"invoice_set_id": instance.id, "endpoint_url": f"{SITE_URL}"}),
            },
        )
    except (
        EXCEPTIONS.ServiceQuotaExceededException,
        EXCEPTIONS.ValidationException,
        EXCEPTIONS.InternalServerException,
        EXCEPTIONS.ConflictException,
        EXCEPTIONS.ResourceNotFoundException,
    ) as error:
        logger.error(f"Error creating schedule for inv set #{instance.id}: {error}")
        return None

    if not (schedule_arn := boto_response.get("ScheduleArn")):
        logger.error(f"Something went wrong when creating the schedule. {boto_response}")
        return None

    instance.schedule_arn = schedule_arn

    instance.save(update_fields=["schedule_arn"])


@receiver(post_save, sender=InvoiceRecurringSet)
def create_client_defaults(sender: Type[InvoiceRecurringSet], instance: InvoiceRecurringSet, created, **kwargs):
    if not created:
        recurring_set_created(instance, **kwargs)
