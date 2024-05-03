import json
from dataclasses import dataclass
from typing import Union, Literal
from datetime import datetime

import pytz
from django.urls import reverse
from django.utils import timezone

from backend.models import Invoice, InvoiceReminder
from infrastructure.aws.handler import get_event_bridge_scheduler
from infrastructure.aws.iam.sfn import get_sfn_execute_role_arn
from infrastructure.aws.step_functions.scheduler import get_step_function
from settings.settings import AWS_TAGS_APP_NAME, SITE_URL, SITE_NAME


@dataclass(frozen=True)
class SuccessResponse:
    reminder: InvoiceReminder
    success: Literal[True] = True


@dataclass(frozen=True)
class ErrorResponse:
    message: str
    success: Literal[False] = False


CreateReminderResponse = Union[ErrorResponse, SuccessResponse]


@dataclass(frozen=True)
class CreateReminderInputData:
    invoice: Invoice
    reminder: InvoiceReminder
    email_type: Literal["client_to_email", "client_email"]
    datetime: str


def create_reminder_schedule(data: CreateReminderInputData) -> CreateReminderResponse:
    print(f"Creating reminder for {data.invoice}", flush=True)

    date_time_to_obj: datetime = datetime.strptime(data.datetime, "%Y-%m-%dT%H:%M")
    date_time_to_obj = date_time_to_obj.astimezone(pytz.timezone("UTC"))
    date_time_to_obj = date_time_to_obj.strftime("%Y-%m-%dT%H:%M")  # type: ignore[assignment]

    # TODO: Add a signal to delete AWS Rule on OntimeSchedule model object delete

    scheduler_step_function = get_step_function()

    if not scheduler_step_function or not scheduler_step_function.get("stateMachineArn"):
        print("[AWS] [SFN] Step function not found", flush=True)
        return ErrorResponse("Step function not found")

    event_bridge_scheduler = get_event_bridge_scheduler()

    data.reminder.save()

    URL = SITE_URL + reverse("webhooks:receive_scheduled_invoice reminder")

    execute_role_arn = get_sfn_execute_role_arn()

    if not execute_role_arn:
        data.reminder.delete()
        return ErrorResponse("Error whilst creating schedule.")

    try:
        CREATED_SCHEDULE = event_bridge_scheduler.create_schedule(
            Name=f"{AWS_TAGS_APP_NAME}-reminder-{data.invoice.id}-{data.reminder.id}",
            FlexibleTimeWindow={"Mode": "OFF"},
            ScheduleExpression=f"at({date_time_to_obj})",
            GroupName=f"{SITE_NAME}-invoice-reminders",
            Target={
                "Arn": scheduler_step_function["stateMachineArn"],
                "RoleArn": get_sfn_execute_role_arn(),
                "Input": json.dumps(
                    {
                        "headers": {
                            "invoice_id": str(data.invoice.id),
                            "reminder_id": str(data.reminder.id),
                            "email_type": data.email_type,
                            "option": "invoice_reminder",
                        },
                        "body": {},
                        "receive_url": URL,
                    }
                ),
            },
            ActionAfterCompletion="DELETE",
        )
    except Exception:
        data.reminder.delete()
        return ErrorResponse("Error whilst creating schedule.")

    data.reminder.stored_schedule_arn = CREATED_SCHEDULE.get("ScheduleArn")
    data.reminder.status = data.reminder.StatusTypes.PENDING
    data.reminder.save()

    return SuccessResponse(data.reminder)
