import logging

from mypy_boto3_scheduler.type_defs import UpdateScheduleOutputTypeDef

from backend.core.service.boto3.handler import BOTO3_HANDLER
from backend.core.service.boto3.scheduler.get import get_boto_schedule
from backend.core.utils.dataclasses import BaseServiceResponse

logger = logging.getLogger(__name__)


class PauseScheduleServiceResponse(BaseServiceResponse[UpdateScheduleOutputTypeDef]): ...


def pause_boto_schedule(name: str, pause: bool = True) -> bool:
    state = "DISABLED" if pause else "ENABLED"
    schedule_response = get_boto_schedule(name)

    if not schedule_response.success:
        return False
        # return PauseScheduleServiceResponse(False, error_message=schedule_response.error_message)

    try:
        filtered_response = {
            k: v
            for k, v in schedule_response.response.items()
            if k not in ["ResponseMetadata", "Arn", "CreationDate", "LastModificationDate"]
        }
        merged_response = filtered_response | {"State": state}

        resp = BOTO3_HANDLER._schedule_client.update_schedule(**merged_response)
        return True
        # return PauseScheduleServiceResponse(True, response=resp)
    except (
        BOTO3_HANDLER.SCHEDULE_EXCEPTIONS.ValidationException,
        BOTO3_HANDLER.SCHEDULE_EXCEPTIONS.InternalServerException,
        BOTO3_HANDLER.SCHEDULE_EXCEPTIONS.ResourceNotFoundException,
    ):
        return False
        # return PauseScheduleServiceResponse(False, error_message="Schedule not found").asdict()
