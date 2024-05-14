import json
from dataclasses import dataclass
from typing import Optional, Union, Literal

import pytz
from django.utils import timezone
from rest_framework.reverse import reverse
from datetime import datetime

from backend.models import Invoice, InvoiceOnetimeSchedule, AuditLog
from infrastructure.aws.handler import get_event_bridge_scheduler
from infrastructure.aws.iam.sfn import get_sfn_execute_role_arn
from infrastructure.aws.step_functions.scheduler import get_step_function
from settings.settings import AWS_TAGS_APP_NAME, SITE_URL


@dataclass(frozen=True)
class ErrorResponse:
    message: str


@dataclass(frozen=True)
class SuccessResponse:
    schedule: InvoiceOnetimeSchedule


CreateOnetimeScheduleResponse = Union[ErrorResponse, SuccessResponse]


@dataclass(frozen=True)
class CreateOnetimeScheduleInputData:
    invoice: Invoice
    option: int
    email_type: Literal["client_to_email", "client_email"]
    date: Optional[str] = None
    time: Optional[str] = None
    datetime: Optional[str] = None


def create_onetime_schedule(data: CreateOnetimeScheduleInputData) -> CreateOnetimeScheduleResponse:
    print(f"Creating onetime schedule for {data.invoice}", flush=True)
    print(f"Creating onetime schedule for {data.invoice} (no flush)")

    date_time = data.datetime

    if not date_time:
        if not data.date:
            return ErrorResponse("Missing date")

        if not data.time:
            return ErrorResponse("Missing time")

        date_time = data.date + "T" + data.time

    date_time_to_obj: datetime = datetime.strptime(date_time, "%Y-%m-%dT%H:%M")
    date_time_to_obj = date_time_to_obj.astimezone(pytz.timezone("UTC"))
    if date_time_to_obj < timezone.now():
        return ErrorResponse("Date time cannot be in the past")

    schedule = InvoiceOnetimeSchedule.objects.create(
        invoice=data.invoice, due=date_time_to_obj, status=InvoiceOnetimeSchedule.StatusTypes.CREATING
    )

    # TODO: Add a signal to delete AWS Rule on OntimeSchedule model object delete

    scheduler_step_function = get_step_function()

    if scheduler_step_function is None or not scheduler_step_function.get("stateMachineArn"):
        print("[AWS] [SFN] Step function not found", flush=True)
        AuditLog.objects.create(action="Failed to get STEP FUNCTION arn. Maybe you need to run `pulumi up`?")
        return ErrorResponse("Step function not found")

    execution_role_arn = get_sfn_execute_role_arn()

    if not execution_role_arn:
        AuditLog.objects.create(action="Failed to get STEP FUNCTION EXECUTION ROLE arn. Maybe you need to run `pulumi up`?")
        return ErrorResponse("Something went wrong on our end. Please contact support.")

    URL = SITE_URL + reverse("webhooks:receive_scheduled_invoice schedule")

    event_bridge_scheduler = get_event_bridge_scheduler()
    CREATED_SCHEDULE = event_bridge_scheduler.create_schedule(
        Name=f"{AWS_TAGS_APP_NAME}-scheduled-invoices-{data.invoice.id}-{schedule.id}",
        GroupName=f"{AWS_TAGS_APP_NAME}-invoice-schedules",
        FlexibleTimeWindow={"Mode": "OFF"},
        ScheduleExpression=f"at({date_time})",
        Target={
            "Arn": scheduler_step_function["stateMachineArn"],
            "RoleArn": get_sfn_execute_role_arn(),
            "Input": json.dumps(
                {
                    "headers": {
                        "invoice_id": str(data.invoice.id),
                        "schedule_id": str(schedule.id),
                        "schedule_occurrence": "once",
                        "email_type": "1",
                    },
                    "body": {},
                    "receive_url": URL,
                }
            ),
        },
        ActionAfterCompletion="DELETE",
    )

    schedule.stored_schedule_arn = CREATED_SCHEDULE.get("ScheduleArn")
    schedule.status = InvoiceOnetimeSchedule.StatusTypes.PENDING
    schedule.save()

    return SuccessResponse(schedule)
