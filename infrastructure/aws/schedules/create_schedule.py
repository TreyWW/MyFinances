import json
from dataclasses import dataclass
from typing import Optional, Union

import pytz
from django.utils import timezone

from backend.models import Invoice, InvoiceOnetimeSchedule
from infrastructure.aws.api_destination.api_destination import get_or_create_api_destination
from infrastructure.aws.handler import event_bridge_scheduler
from infrastructure.aws.iam.sfn import get_or_create_sfn_execute_role_arn
from infrastructure.aws.step_functions.scheduler import get_or_create_schedule_step_function
from settings.settings import AWS_TAGS_APP_NAME


@dataclass(frozen=True)
class ErrorResponse:
    message: str


@dataclass(frozen=True)
class SuccessResponse:
    schedule: InvoiceOnetimeSchedule


CreateOnetimeScheduleResponse = Union[ErrorResponse, SuccessResponse]


@dataclass(frozen=True)
class CreateOnetimeScheduleInputData:
    option: int
    date: Optional[str] = None
    time: Optional[str] = None
    datetime: Optional[str] = None


def create_onetime_schedule(data: CreateOnetimeScheduleInputData) -> CreateOnetimeScheduleResponse:
    get_or_create_api_destination()

    date_time = data.datetime

    if not date_time:
        if not data.date:
            return ErrorResponse("Missing date")

        if not data.time:
            return ErrorResponse("Missing time")

        date_time = data.date + "T" + data.time

    date_time_to_obj: timezone.datetime = timezone.datetime.strptime(date_time, "%Y-%m-%dT%H:%M")
    date_time_to_obj = date_time_to_obj.astimezone(pytz.timezone("UTC"))
    if date_time_to_obj < timezone.now():
        return ErrorResponse("Date time cannot be in the past")

    invoice = Invoice.objects.first()
    schedule = InvoiceOnetimeSchedule.objects.create(
        invoice=invoice,
        due=date_time_to_obj,
        status=InvoiceOnetimeSchedule.StatusTypes.CREATING
    )

    # TODO: Add a signal to delete AWS Rule on OntimeSchedule model object delete

    scheduler_step_function = get_or_create_schedule_step_function()

    if not scheduler_step_function.get("stateMachineArn"):
        print("[AWS] [SFN] Step function not found")
        return ErrorResponse("Step function not found")

    CREATED_SCHEDULE = event_bridge_scheduler.create_schedule(
        Name=f"{AWS_TAGS_APP_NAME}-scheduled-invoices-{invoice.id}-{schedule.id}",
        FlexibleTimeWindow={
            "Mode": "OFF"
        },
        ScheduleExpression=f"at({date_time})",
        Target={
            "Arn": scheduler_step_function["stateMachineArn"],
            "RoleArn": get_or_create_sfn_execute_role_arn(),
            "Input": json.dumps({
                "headers": {"invoice_id": str(invoice.id)},
                "body": {}
            })
        },
        ActionAfterCompletion="DELETE"
    )

    schedule.stored_schedule_arn = CREATED_SCHEDULE.get("ScheduleArn")
    schedule.status = InvoiceOnetimeSchedule.StatusTypes.PENDING
    schedule.save()

    return SuccessResponse(schedule)
