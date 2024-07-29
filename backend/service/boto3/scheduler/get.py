import logging

from celery import shared_task
from mypy_boto3_scheduler.type_defs import GetScheduleOutputTypeDef

from backend.service.boto3.handler import BOTO3_HANDLER
from backend.utils.dataclasses import BaseServiceResponse

logger = logging.getLogger(__name__)


class GetScheduleServiceResponse(BaseServiceResponse[GetScheduleOutputTypeDef]): ...


@shared_task
def get_boto_schedule(name: str) -> GetScheduleServiceResponse:
    try:
        resp = BOTO3_HANDLER._schedule_client.get_schedule(Name=name, GroupName=BOTO3_HANDLER.scheduler_invoices_group_name)
        return GetScheduleServiceResponse(True, response=resp)
    except (
        BOTO3_HANDLER.SCHEDULE_EXCEPTIONS.ValidationException,
        BOTO3_HANDLER.SCHEDULE_EXCEPTIONS.InternalServerException,
        BOTO3_HANDLER.SCHEDULE_EXCEPTIONS.ResourceNotFoundException,
    ):
        return GetScheduleServiceResponse(False, error_message="Schedule not found")
