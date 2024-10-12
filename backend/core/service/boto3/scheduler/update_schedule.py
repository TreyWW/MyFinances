import datetime
import logging
from uuid import UUID

from backend.finance.models import InvoiceRecurringProfile
from backend.core.service.boto3.handler import BOTO3_HANDLER
from backend.core.service.boto3.scheduler.create_schedule import create_boto_schedule
from backend.core.service.boto3.scheduler.get import get_boto_schedule
from backend.core.service.invoices.recurring.schedules.date_handlers import get_schedule_cron, CronServiceResponse

logger = logging.getLogger(__name__)


def update_boto_schedule(instance_id: int | str):
    print(f"Updating existing boto schedule {str(instance_id)}")
    instance: InvoiceRecurringProfile

    if isinstance(instance_id, int | str):
        try:
            instance = InvoiceRecurringProfile.objects.get(id=instance_id)
        except InvoiceRecurringProfile.DoesNotExist:
            logger.error(f"InvoiceRecurringProfile with id {instance_id} does not exist.")
            return None
    elif isinstance(instance_id, InvoiceRecurringProfile):
        instance = instance_id
    else:
        logger.error(f"Invalid instance type: {type(instance_id)}")
        return None

    if not BOTO3_HANDLER.initiated:
        logger.error(f'BOTO3 IS CURRENTLY DOWN, #{instance_id} has been set to "Paused"!')
        logger.error(f"Boto3 handler not initiated. Cannot use AWS services.")
        return None

    schedule_uuid: str

    if isinstance(instance.boto_schedule_uuid, str):
        schedule_uuid = instance.boto_schedule_uuid
    elif isinstance(instance.boto_schedule_uuid, UUID):
        schedule_uuid = str(instance.boto_schedule_uuid)
    else:
        print("Creating new boto schedule due to invalid schedule uuid")
        return create_boto_schedule(instance)

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

    end_date: datetime.date | None = instance.end_date
    end_datetime: datetime.datetime | str = datetime.datetime.combine(end_date, datetime.datetime.now().time()) if end_date else ""

    schedule_response = get_boto_schedule(schedule_uuid)

    if not schedule_response.success:
        logger.error(schedule_response.error)
        if schedule_response.error == "Schedule not found":
            print(f"Creating new boto schedule due to schedule {schedule_uuid} not being found")
            return create_boto_schedule(instance)
        return schedule_response.error

    new_schedule_params = {
        # "FlexibleTimeWindow": {"Mode": "OFF"},
        "ScheduleExpression": f"cron({CRON_RESPONSE.response})",
        "State": "ENABLED" if instance.status == "ongoing" else "DISABLED",
        # "Target": {
        #     "Arn": BOTO3_HANDLER.scheduler_lambda_arn,
        #     "RoleArn": BOTO3_HANDLER.scheduler_lambda_access_role_arn,
        #     "Input": json.dumps({"invoice_profile_id": instance.id, "endpoint_url": f"{SITE_URL}"}),
        #     "RetryPolicy": {"MaximumRetryAttempts": 20, "MaximumEventAgeInSeconds": 21600},  # 6 hours
        # },
        # "ActionAfterCompletion": "NONE",
        "EndDate": end_datetime,
    }

    if not end_datetime:
        del new_schedule_params["EndDate"]

    # check if every new param is the exact same as the original schedule_response, if so return None and add logger msg but ignore the
    # missing keys from the new one, only check the keys in the new one

    for k, v in new_schedule_params.items():
        if schedule_response.response.get(k) != v:
            break

        logger.info("No changes to schedule, returning early instead of sending request.")
        return None

    try:
        filtered_response = {
            k: v
            for k, v in schedule_response.response.items()
            if k not in ["ResponseMetadata", "Arn", "CreationDate", "LastModificationDate"]
        }
        merged_response = filtered_response | new_schedule_params

        resp = BOTO3_HANDLER._schedule_client.update_schedule(**merged_response)
    except (
        EXCEPTIONS.ValidationException,
        EXCEPTIONS.InternalServerException,
        EXCEPTIONS.ResourceNotFoundException,
    ):
        return False

    instance.boto_schedule_arn = resp["ScheduleArn"]
    instance.boto_schedule_uuid = schedule_uuid
    instance.status = "ongoing" if instance.status == "ongoing" else "paused"
    instance.save(update_fields=["boto_schedule_arn", "boto_schedule_uuid", "status"])
