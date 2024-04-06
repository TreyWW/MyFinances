"""An AWS Python Pulumi program"""

from __future__ import annotations

import pulumi
from emails import default_email_templates
from pulumi_aws import ec2
from pulumi_aws import iam
from pulumi_aws import ses

config = pulumi.Config()

tags = {"app": "myfinances", "stage": config.require("stage")}

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

pulumi.export("ses_user", ses_user.id)
pulumi.export("ses_user_access_key_id", ses_user_access_key.id)
pulumi.export("ses_user_access_key_secret", ses_user_access_key.ses_smtp_password_v4)
