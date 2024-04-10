import json

from pulumi_aws import sfn


def get_state_machine(site_name, scheduled_invoices_api_connection, execution_role):
    return sfn.StateMachine(
        "invoice_schedules_step_function",
        name=f"{site_name}-scheduled-invoices",
        role_arn=execution_role.arn,
        definition=scheduled_invoices_api_connection.arn.apply(
            lambda arn: json.dumps(
                {
                    "StartAt": "Call Schedule Endpoint",
                    "States": {
                        "Call Schedule Endpoint": {
                            "Type": "Task",
                            "Resource": "arn:aws:states:::http:invoke",
                            "Parameters": {
                                "Authentication": {"ConnectionArn": arn},
                                "Method": "POST",
                                "ApiEndpoint.$": "$.receive_url",
                                "RequestBody.$": "$.body",
                                "Headers.$": "$.headers",
                            },
                            "Retry": [
                                {
                                    "ErrorEquals": ["States.ALL"],
                                    "BackoffRate": 2,
                                    "IntervalSeconds": 1,
                                    "MaxAttempts": 3,
                                    "JitterStrategy": "FULL",
                                }
                            ],
                            "End": True,
                        }
                    },
                    "Comment": "Call our django api to alert the schedule timestamp has reached.",
                }
            )
        ),
    )
