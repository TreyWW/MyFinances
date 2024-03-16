import json
from typing import NoReturn

from mypy_boto3_iam.type_defs import CreatePolicyResponseTypeDef, PolicyTypeDef

from infrastructure.aws.handler import get_iam_client, DEBUG_LEVEL
from settings.settings import AWS_TAGS_APP_NAME

iam_client = get_iam_client

def get_or_create_sfn_execute_role_arn() -> str:
    """
    :returns: RoleArn
    """
    if DEBUG_LEVEL == "debug":
        print("[AWS] Fetching scheduler role by name...", flush=True)

    try:
        response = iam_client.get_role(
            RoleName=f"{AWS_TAGS_APP_NAME}-invoicing-scheduler-fn"
        )

    except iam_client.exceptions.NoSuchEntityException:
        response = {}

    if response.get("Role"):
        if DEBUG_LEVEL == "debug":
            print(f"[AWS] Found role!")

        assign_policy(check=True)

        return response.get("Role").get("Arn")

    if DEBUG_LEVEL:
        print("[AWS] Creating scheduler role...", flush=True)
    response = iam_client.create_role(
        RoleName=f"{AWS_TAGS_APP_NAME}-invoicing-scheduler-fn",
        Path=f"/{AWS_TAGS_APP_NAME}-scheduled-invoices/",
        AssumeRolePolicyDocument=json.dumps({
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {
                        "Service": "scheduler.amazonaws.com"
                    },
                    "Action": "sts:AssumeRole"
                }
            ]
        })
    )  #

    assign_policy()

    return response.get("Role").get("Arn")


def assign_policy(check=False) -> NoReturn:
    policy = get_or_create_policy()
    print(policy)
    print(f"{AWS_TAGS_APP_NAME}-invoicing-scheduler-fn")
    if check:
        try:
            iam_client.get_role_policy(
                RoleName=f"{AWS_TAGS_APP_NAME}-invoicing-scheduler-fn",
                PolicyName=policy.get("PolicyName")
            )
            print("[AWS] Policy already attached to scheduler role!", flush=True)
            return
        except iam_client.exceptions.NoSuchEntityException:
            print("[AWS] Policy not attached to scheduler role, attaching now...", flush=True)

    if DEBUG_LEVEL:
        print("[AWS] Attaching policy to scheduler role...", flush=True)

    iam_client.attach_role_policy(
        RoleName=f"{AWS_TAGS_APP_NAME}-invoicing-scheduler-fn",
        PolicyArn=policy.get("Arn")
    )

    print("[AWS] Attached policy to scheduler role!", flush=True)


def get_or_create_policy() -> CreatePolicyResponseTypeDef | PolicyTypeDef:
    if DEBUG_LEVEL == "debug":
        print("[AWS] Fetching all policies by prefix...", flush=True)

    response = iam_client.list_policies(
        Scope="Local",
        PathPrefix=f"/{AWS_TAGS_APP_NAME}-scheduled-invoices/"
    )

    policies = [
        policy
        for policy in response.get("Policies", [])
        if policy.get("PolicyName") == f"{AWS_TAGS_APP_NAME}-invoicing-scheduler-fn"
    ]

    if len(policies) == 1:
        if DEBUG_LEVEL == "debug":
            print("[AWS] Found policy!", flush=True)
        return policies[0]

    if len(policies) > 1:
        if DEBUG_LEVEL == "debug":
            print("[AWS] Found more than one policy by prefix! Not yet implemented a way to filter.")
        raise Exception("More than one invoice scheduler function found. Not yet implemented a way to filter.")

    if DEBUG_LEVEL:
        print("[AWS] Creating new policy for scheduler step function to access API Destination...", flush=True)

    return iam_client.create_policy(
        PolicyName=f"{AWS_TAGS_APP_NAME}-invoicing-scheduler-fn",
        Path=f"/{AWS_TAGS_APP_NAME}-scheduled-invoices/",
        PolicyDocument=json.dumps({
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "CallAPIDestination",
                    "Effect": "Allow",
                    "Action": [
                        "states:InvokeHTTPEndpoint",
                        "states:StartExecution"
                    ],
                    "Resource": [
                        "*"
                    ]
                },
                {
                    "Sid": "AccessSecrets",
                    "Effect": "Allow",
                    "Action": [
                        "events:RetrieveConnectionCredentials",
                        "secretsmanager:GetSecretValue",
                        "secretsmanager:DescribeSecret"
                    ],
                    "Resource": [
                        "*"
                    ]
                },
                {
                    "Sid": "CreateLogDelivery",
                    "Effect": "Allow",
                    "Action": [
                        "logs:CreateLogDelivery",
                        "logs:CreateLogStream",
                        "logs:GetLogDelivery",
                        "logs:UpdateLogDelivery",
                        "logs:DeleteLogDelivery",
                        "logs:ListLogDeliveries",
                        "logs:PutLogEvents",
                        "logs:PutResourcePolicy",
                        "logs:DescribeResourcePolicies",
                        "logs:DescribeLogGroups"
                    ],
                    "Resource": "*"
                },
                {
                    "Sid": "AllowEventbridgeScheduler",
                    "Effect": "Allow",
                    "Action": [
                        "scheduler:*"
                    ],
                    "Resource": [
                        "*"
                    ]
                }
            ]
        })
    )
