"""An AWS Python Pulumi program"""

from __future__ import annotations

import json
from contextlib import closing

import pulumi
from emails import default_email_templates
from pulumi_aws import ec2
from pulumi_aws import iam
from pulumi_aws import ses
from pulumi_aws import scheduler
from pulumi_aws import cloudwatch

from step_functions import get_state_machine

config = pulumi.Config()

tags = {"app": "myfinances", "stage": config.require("stage")}

site_name = config.require("site_name")

# VPC

# Main VPC

vpc = ec2.Vpc(
    resource_name="main_vpc",
    cidr_block=config.get("vpc_cidr", "10.0.0.0/16"),
    enable_dns_hostnames=True,
    # enable_dns_support=True,
    instance_tenancy="default",
    tags={"Name": "main vpc"},
)

# Public Subnet

vpc_public_subnet = ec2.Subnet(
    "main_subnet",
    vpc_id=vpc.id,
    cidr_block=config.get("public_subnet_cidr", "10.0.1.0/24"),
    availability_zone=config.get("public_subnet_az", "eu-west-2a"),
    map_public_ip_on_launch=True,
    tags={"Name": "main_subnet"},
)

# Private Subnet

vpc_private_subnet = ec2.Subnet(
    "private_subnet",
    vpc_id=vpc.id,
    cidr_block=config.get("private_subnet_cidr", "10.0.2.0/24"),
    availability_zone=config.get("private_subnet_az", "eu-west-2a"),
    tags={"Name": "private-subnet"},
)

# Email Users

ses_user = iam.User("ses_user", name=f'{config.require("site_name")}-ses-user', path=f"/myfinances/{config.require('stage')}/", tags=tags)

ses_user_access_key = iam.AccessKey("ses_user_access_key", user=ses_user.name)

send_emails_policy = iam.get_policy_document(
    statements=[
        {
            "effect": "Allow",
            "actions": ["ses:SendRawEmail", "ses:SendTemplatedEmail", "ses:SendBulkEmail", "ses:SendBulkTemplatedEmail"],
            "resources": ["*"],
        }
    ],
)

get_messages_policy = iam.get_policy_document(statements=[{"effect": "Allow", "actions": ["ses:GetMessageInsights"], "resources": ["*"]}])

ses_user_send_policy = iam.UserPolicy("ses_user_send_policy", policy=send_emails_policy.json, user=ses_user.name)
ses_user_get_messages_policy = iam.UserPolicy("ses_user_get_messages_policy", policy=get_messages_policy.json, user=ses_user.name)

# Email Templates

ses_template_user_send_client_email = ses.Template(
    "ses_template_user_send_client_email",
    name="user_send_client_email",
    subject=config.get("ses_template_user_send_client_email-subject", default_email_templates["user_send_email"]["subject"]),
    html=config.get("ses_template_user_send_client_email-content_html", default_email_templates["user_send_email"]["content_html"]),
    text=config.get("ses_template_user_send_client_email-content_text", default_email_templates["user_send_email"]["content_text"]),
)

# Invoice Schedules

invoice_schedules_group = scheduler.ScheduleGroup("invoice_schedules_group", name=f"{site_name}-invoice-schedules")


# API Destination


scheduled_invoices_api_connection = cloudwatch.EventConnection(
    "invoice_schedules_api_connection",
    name=f"{site_name}-scheduled-invoices-connection",
    description="Main connection to Django API",
    authorization_type="API_KEY",
    auth_parameters=cloudwatch.EventConnectionAuthParametersArgs(
        api_key=cloudwatch.EventConnectionAuthParametersApiKeyArgs(
            key="Authorization", value=f"Token {config.get('api_destination-api_key')}"
        )
    ),
)


scheduled_invoices_api_destination = cloudwatch.EventApiDestination(
    "invoice_schedules_api_destination",
    name=f"{site_name}-scheduled-invoices",
    description="MyFinances Scheduled Invoices",
    invocation_endpoint=f"{config.require('site_url')}/api/invoices/schedules/receive/",
    http_method="POST",
    invocation_rate_limit_per_second=300,
    connection_arn=scheduled_invoices_api_connection.arn,
)

# Step Functions

scheduler_execution_role = iam.Role(
    "scheduler-execution-role",
    name=f"{site_name}-invoicing-scheduler",
    path=f"/{site_name}-scheduled-invoices/",
    assume_role_policy=json.dumps(
        {
            "Version": "2012-10-17",
            "Statement": [
                {"Effect": "Allow", "Principal": {"Service": "scheduler.amazonaws.com"}, "Action": "sts:AssumeRole"},
                {"Effect": "Allow", "Principal": {"Service": "states.amazonaws.com"}, "Action": "sts:AssumeRole"},
            ],
        }
    ),
)
scheduler_execution_policy = iam.Policy(
    "scheduler-execution-policy",
    name=f"{site_name}-invoicing-scheduler",
    path=f"/{site_name}-scheduled-invoices/",
    policy=json.dumps(
        {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "CallAPIDestination",
                    "Effect": "Allow",
                    "Action": ["states:InvokeHTTPEndpoint", "states:StartExecution"],
                    "Resource": "*",
                },
                {
                    "Sid": "AccessSecrets",
                    "Effect": "Allow",
                    "Action": ["events:RetrieveConnectionCredentials", "secretsmanager:GetSecretValue", "secretsmanager:DescribeSecret"],
                    "Resource": "*",
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
                {"Sid": "AllowEventbridgeScheduler", "Effect": "Allow", "Action": ["scheduler:*"], "Resource": "*"},
            ],
        }
    ),
)

# Attach policy to role
scheduler_execution_policy_attachment = iam.RolePolicyAttachment(
    "scheduler-execution-policy",
    policy_arn=scheduler_execution_policy.arn,
    role=scheduler_execution_role.name,
    opts=pulumi.ResourceOptions(depends_on=[scheduler_execution_policy, scheduler_execution_role]),
)

scheduled_invoices_state_machine = get_state_machine(site_name, scheduled_invoices_api_connection, scheduler_execution_role)


pulumi.export("ses_user", ses_user.id)
pulumi.export("ses_user_access_key_id", ses_user_access_key.id)
pulumi.export("ses_user_access_key_secret", ses_user_access_key.ses_smtp_password_v4)
