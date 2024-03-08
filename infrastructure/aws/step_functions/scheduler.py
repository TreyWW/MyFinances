import json

from infrastructure.aws.handler import sfn_client, APP_TAGS, DEBUG_LEVEL
from infrastructure.aws.iam.sfn import get_or_create_sfn_execute_role_arn
from settings.settings import AWS_TAGS_APP_NAME


def get_or_create_schedule_step_function() -> dict:
    if DEBUG_LEVEL == "debug":
        print("[AWS] [SFN] Fetching scheduler step function by name...")

    functions = sfn_client.list_state_machines()

    invoice_functions = [
        function
        for function in functions.get("stateMachines", [])
        if function.get("name") == f"{AWS_TAGS_APP_NAME}-invoicing-scheduler-fn"
    ]

    if len(invoice_functions) == 1:
        if DEBUG_LEVEL == "debug":
            print("[AWS] [SFN] Found scheduler step function!")
        return invoice_functions[0]

    if len(invoice_functions) > 1:
        if DEBUG_LEVEL == "debug":
            print("[AWS] [SFN] Found more than one scheduler step function! Not yet implemented a way to filter.")
        raise Exception("More than one invoice scheduler function found. Not yet implemented a way to filter.")

    role_arn = get_or_create_sfn_execute_role_arn()

    print("[AWS] [SFN] Creating scheduler step function...")

    return sfn_client.create_state_machine(
        name=f"{AWS_TAGS_APP_NAME}-invoicing-scheduler-fn",
        roleArn=role_arn,
        type="STANDARD",
        loggingConfiguration={
            "level": "OFF",
        },
        tags=[*APP_TAGS, {"key": "service", "value": "invoicing-scheduler"}],
        tracingConfiguration={
            "enabled": False
        },
        definition=json.dumps({
            "Comment": "A description of my state machine",
            "StartAt": "Call Schedule Endpoint",
            "States": {
                "StartAt": "Call Schedule Endpoint",
                "States": {
                    "Call Schedule Endpoint": {
                        "Type": "Task",
                        "Resource": "arn:aws:states:::http:invoke",
                        "Parameters": {
                            "Authentication": {
                                "ConnectionArn": "arn:aws:events:eu-west-2:303674098874:connection/MyFinances-AppRunner/25cfe143-ca0f-4d4f-803e-0ca9467436e9"
                            },
                            "Method": "POST",
                            "ApiEndpoint": "https://myfinances.strelix.dev/api/invoices/schedule_test/",
                            "RequestBody.$": "$.body",
                            "Headers.$": "$.headers"
                        },
                        "Retry": [
                            {
                                "ErrorEquals": [
                                    "States.ALL"
                                ],
                                "BackoffRate": 2,
                                "IntervalSeconds": 1,
                                "MaxAttempts": 3,
                                "JitterStrategy": "FULL"
                            }
                        ],
                        "End": True
                    }
                },
                "Comment": "Call our django api to alert the schedule timestamp has reached."
            }
        })
    )
