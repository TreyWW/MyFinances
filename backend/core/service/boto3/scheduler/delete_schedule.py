import datetime
import json
import logging
from typing import Type
from uuid import uuid4

from django.apps import apps
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse

from backend.finance.models import InvoiceRecurringProfile, BotoSchedule, InvoiceReminder
from backend.core.service.boto3.handler import BOTO3_HANDLER
from backend.core.service.invoices.recurring.schedules.date_handlers import get_schedule_cron, CronServiceResponse
from settings.helpers import get_var

logger = logging.getLogger(__name__)

BotoScheduleType = Type[BotoSchedule]


def delete_boto_schedule(model_name: str, instance_id: int | str):
    instance: BotoSchedule
    model_type: BotoScheduleType = apps.get_model("backend", model_name)

    try:
        # Dynamically retrieve the instance based on the model type and ID
        instance = model_type.objects.get(id=instance_id)  # type: ignore[attr-defined]
    except ObjectDoesNotExist:
        logger.error(f"{model_type.__name__} with id {instance_id} does not exist.")
        return None
    except Exception as e:
        logger.error(f"Error retrieving {model_type.__name__} with id {instance_id}: {e}")
        return None

    if not BOTO3_HANDLER.initiated:
        logger.error(f'BOTO3 IS CURRENTLY DOWN, #{instance_id} has been set to "Paused"!')
        return None

    EXCEPTIONS = BOTO3_HANDLER._schedule_client.exceptions

    try:
        BOTO3_HANDLER._schedule_client.delete_schedule(
            Name=str(instance.boto_schedule_uuid), GroupName=BOTO3_HANDLER.scheduler_invoices_group_name
        )
    except (
        EXCEPTIONS.ValidationException,
        EXCEPTIONS.ResourceNotFoundException,
        # EXCEPTIONS.InternalServerException, # use celery retry
        # EXCEPTIONS.ConflictException, # use celery retry
    ) as error:
        logger.error(f"Error deleting schedule for {model_type.__name__} #{instance.id}: {error}")  # type: ignore[attr-defined]
        return None

    instance.boto_schedule_status = instance.BotoStatusTypes.CANCELLED
    instance.boto_last_updated = datetime.datetime.now()
    instance.save()
    return None
