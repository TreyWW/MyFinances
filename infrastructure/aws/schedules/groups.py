from dataclasses import dataclass
from typing import Literal

from mypy_boto3_scheduler.type_defs import ScheduleGroupSummaryTypeDef

from infrastructure.aws.handler import get_event_bridge_scheduler


@dataclass
class Success:
    group: ScheduleGroupSummaryTypeDef
    success: Literal[True] = True


@dataclass
class Error:
    message: str
    success: Literal[False] = False


def get_group(name):
    event_bridge_scheduler = get_event_bridge_scheduler()
    try:
        group: ScheduleGroupSummaryTypeDef = event_bridge_scheduler.get_schedule_group(Name=name)
        return Success(group)
    except event_bridge_scheduler.exceptions.ResourceNotFoundException:
        return Error(f"Group not found.")
    except (
        event_bridge_scheduler.exceptions.InternalServerException,
        event_bridge_scheduler.exceptions.ThrottlingException,
        event_bridge_scheduler.exceptions.ValidationException,
    ):
        return Error("Failed to fetch group.")
