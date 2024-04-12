import json
import logging

from mypy_boto3_iam.type_defs import CreatePolicyResponseTypeDef, PolicyTypeDef

from infrastructure.aws.handler import get_iam_client, DEBUG_LEVEL
from settings.settings import AWS_TAGS_APP_NAME


logger = logging.getLogger(__name__)


def get_sfn_execute_role_arn() -> str | None:
    """
    :returns: RoleArn
    """
    if DEBUG_LEVEL == "debug":
        print("[AWS] Fetching scheduler role by name...", flush=True)

    iam_client = get_iam_client()

    try:
        response = iam_client.get_role(RoleName=f"{AWS_TAGS_APP_NAME}-invoicing-scheduler")
    except (iam_client.exceptions.NoSuchEntityException, iam_client.exceptions.ServiceFailureException):
        response = {}

    if response.get("Role"):
        if DEBUG_LEVEL == "debug":
            print(f"[AWS] Found role!")
        return response.get("Role").get("Arn")

    logging.error("Failed to get STEP FUNCTION arn. Maybe you need to run `pulumi up`?")
    return None


def get_or_create_policy() -> CreatePolicyResponseTypeDef | PolicyTypeDef:
    if DEBUG_LEVEL == "debug":
        print("[AWS] Fetching all policies by prefix...", flush=True)

    iam_client = get_iam_client()

    response = iam_client.list_policies(Scope="Local", PathPrefix=f"/{AWS_TAGS_APP_NAME}-scheduled-invoices/")

    policies = [
        policy for policy in response.get("Policies", []) if policy.get("PolicyName") == f"{AWS_TAGS_APP_NAME}-invoicing-scheduler-fn"
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
        PolicyDocument=json.dumps(
            {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Sid": "CallAPIDestination",
                        "Effect": "Allow",
                        "Action": ["states:InvokeHTTPEndpoint", "states:StartExecution"],
                        "Resource": ["*"],
                    },
                    {
                        "Sid": "AccessSecrets",
                        "Effect": "Allow",
                        "Action": [
                            "events:RetrieveConnectionCredentials",
                            "secretsmanager:GetSecretValue",
                            "secretsmanager:DescribeSecret",
                        ],
                        "Resource": ["*"],
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
                            "logs:DescribeLogGroups",
                        ],
                        "Resource": "*",
                    },
                    {"Sid": "AllowEventbridgeScheduler", "Effect": "Allow", "Action": ["scheduler:*"], "Resource": ["*"]},
                ],
            }
        ),
    )
