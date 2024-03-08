from dataclasses import dataclass
from typing import List

from mypy_boto3_scheduler.type_defs import ScheduleSummaryTypeDef

from infrastructure.aws.handler import event_bridge_scheduler
from settings.settings import AWS_TAGS_APP_NAME


@dataclass(frozen=True)
class SuccessResponse:
    schedules: List[ScheduleSummaryTypeDef]


@dataclass(frozen=True)
class ErrorResponse:
    message: str


ScheduleListResponse = ErrorResponse | SuccessResponse


def list_schedules() -> ScheduleListResponse:
    try:
        schedules = event_bridge_scheduler.list_schedules(
            NamePrefix=f"{AWS_TAGS_APP_NAME}-scheduled-invoices",
            State="ENABLED",
        )  # possibly add groups in the future

        return SuccessResponse(schedules=schedules.get("Schedules", []))

    except event_bridge_scheduler.exceptions.ResourceNotFoundException:
        return ErrorResponse("Failed to list schedules")

    except Exception:
        return ErrorResponse("Failed to list schedules")
