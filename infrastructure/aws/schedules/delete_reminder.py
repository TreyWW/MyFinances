from dataclasses import dataclass
from typing import Literal

from infrastructure.aws.handler import get_event_bridge_scheduler
from settings.settings import AWS_TAGS_APP_NAME


@dataclass(frozen=True)
class SuccessResponse:
    message: str
    success: Literal[True] = True


@dataclass(frozen=True)
class ErrorResponse:
    message: str
    success: Literal[False] = False


DeleteScheduleResponse = SuccessResponse | ErrorResponse


def delete_reminder(invoice_id, reminder_id) -> DeleteScheduleResponse:
    event_bridge_scheduler = get_event_bridge_scheduler()
    try:
        print(f"[AWS] [SCHEDULE] Deleting schedule: {invoice_id}-{reminder_id}")
        event_bridge_scheduler.delete_schedule(
            Name=f"{AWS_TAGS_APP_NAME}-reminder-{invoice_id}-{reminder_id}", GroupName=f"{AWS_TAGS_APP_NAME}-invoice-reminders"
        )

        return SuccessResponse("Schedule deleted")

    except event_bridge_scheduler.exceptions.ResourceNotFoundException:
        return ErrorResponse("Schedule not found")

    except Exception as e:
        print(e)
        return ErrorResponse("Failed to delete schedule.")
