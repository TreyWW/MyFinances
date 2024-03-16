from dataclasses import dataclass

from infrastructure.aws.handler import get_event_bridge_scheduler
from settings.settings import AWS_TAGS_APP_NAME

event_bridge_scheduler = get_event_bridge_scheduler


@dataclass(frozen=True)
class SuccessResponse:
    message: str


@dataclass(frozen=True)
class ErrorResponse:
    message: str


DeleteScheduleResponse = SuccessResponse | ErrorResponse


def delete_schedule(invoice_id, schedule_id) -> DeleteScheduleResponse:
    try:
        print(f"[AWS] [SCHEDULE] Deleting schedule: {invoice_id}-{schedule_id}")
        event_bridge_scheduler.delete_schedule(Name=f"{AWS_TAGS_APP_NAME}-scheduled-invoices-{invoice_id}-{schedule_id}")

        return SuccessResponse("Schedule deleted")

    except event_bridge_scheduler.exceptions.ResourceNotFoundException:
        return ErrorResponse("Schedule not found")

    except Exception as e:
        print(e)
        return ErrorResponse("Failed to delete schedule.")
