import datetime
import json
import logging
from uuid import uuid4

from django.urls import reverse

from backend.models import InvoiceRecurringSet
from backend.service.boto3.handler import BOTO3_HANDLER
from backend.service.invoices.recurring.schedules.date_handlers import get_schedule_cron, CronServiceResponse
from settings.helpers import get_var

logger = logging.getLogger(__name__)


def update_boto_schedule(instance_id: int | str):
    print("TASK 7 - View logic")
    instance: InvoiceRecurringSet

    if isinstance(instance_id, int | str):
        try:
            instance = InvoiceRecurringSet.objects.get(id=instance_id)
        except InvoiceRecurringSet.DoesNotExist:
            logger.error(f"InvoiceRecurringSet with id {instance_id} does not exist.")
            return None
    elif isinstance(instance_id, InvoiceRecurringSet):
        instance = instance_id
    else:
        logger.error(f"Invalid instance type: {type(instance_id)}")
        return None

    if not BOTO3_HANDLER.initiated:
        instance.status = "paused"
        instance.save()
        logger.error(f'BOTO3 IS CURRENTLY DOWN, #{instance_id} has been set to "Paused"!')

    if isinstance(instance.boto_schedule_uuid, str):
        schedule_uuid: str = instance.boto_schedule_uuid
    else:
        schedule_uuid = str(uuid4())

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

    SITE_URL = get_var("SITE_URL", default="http://127.0.0.1:8000") + reverse("webhooks:receive_recurring_invoices")

    end_date: datetime.date | None = instance.end_date
    end_datetime: datetime.datetime | None = datetime.datetime.combine(end_date, datetime.datetime.now().time()) if end_date else ""

    create_schedule_params = {
        "Name": schedule_uuid,
        "GroupName": BOTO3_HANDLER.scheduler_invoices_group_name,
        "FlexibleTimeWindow": {"Mode": "OFF"},
        "ScheduleExpression": f"cron({CRON_RESPONSE.response})",
        "Target": {
            "Arn": BOTO3_HANDLER.scheduler_lambda_arn,
            "RoleArn": BOTO3_HANDLER.scheduler_lambda_access_role_arn,
            "Input": json.dumps({"invoice_set_id": instance.id, "endpoint_url": f"{SITE_URL}"}),
            "RetryPolicy": {"MaximumRetryAttempts": 20, "MaximumEventAgeInSeconds": 21600},  # 6 hours
        },
        "ActionAfterCompletion": "NONE",
        "EndDate": end_datetime,
    }

    if not end_datetime:
        del create_schedule_params["EndDate"]

    try:
        boto_response = BOTO3_HANDLER._schedule_client.create_schedule(**create_schedule_params)
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

    instance.boto_schedule_arn = schedule_arn
    instance.boto_schedule_uuid = schedule_uuid
    instance.status = "ongoing"
    instance.save(update_fields=["boto_schedule_arn", "boto_schedule_uuid", "status"])
