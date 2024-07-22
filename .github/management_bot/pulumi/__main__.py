from __future__ import annotations

import json
import pulumi

from pulumi_aws import apigateway, iam, scheduler
from pulumi_aws import lambda_

config = pulumi.Config()

site_name: str = pulumi.get_project()
account_id = config.get("accountId", ":")
region = config.get("region", "eu-west-2")
tags = {"app": site_name}

# Reminders

reminders_group = scheduler.ScheduleGroup("invoice_reminders_group", name=f"myfinances-github-bot-remind_me")

# lambda_layer
lambda_access_role = iam.Role(
    "lambda_access_role",
    name="lambda_role",
    path="/myfinances/management_bot/",
    assume_role_policy=json.dumps(
        {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Action": "sts:AssumeRole",
                    "Principal": {
                        "Service": "lambda.amazonaws.com",
                    },
                    "Effect": "Allow",
                    "Sid": "",
                }
            ],
        }
    ),
)

# <editor-fold desc="lambda_execution_policy">
# This goes on Lambda to send comment
lambda_execution_policy = iam.Policy(
    "lambda-execution-policy",
    name=f"lambda-execution-policy",
    path="/myfinances/management_bot/",
    policy=json.dumps(
        {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "CreateLogDelivery",
                    "Effect": "Allow",
                    "Action": [
                        "kms:Decrypt",
                        "ssm:GetParametersByPath",
                        "ssm:GetParameters",
                        "ssm:GetParameter",
                        "logs:CreateLogGroup",
                        "logs:CreateLogStream",
                        "logs:PutLogEvents",
                    ],
                    "Resource": [
                        "arn:aws:ssm:*:*:parameter/myfinances/github_bot/*",
                        "arn:aws:kms:*:*:key/*",
                        "arn:aws:logs:*:*:log-group:/aws/lambda/myfinances_github_bot_webhooks:*",
                        "arn:aws:logs:*:*:log-group:/aws/lambda/myfinances_github_bot_reminders:*",
                        "arn:aws:logs:*:*:log-group:/aws/lambda/myfinances_github_bot_webhooks:*:log-stream:*",
                        "arn:aws:logs:*:*:log-group:/aws/lambda/myfinances_github_bot_reminders:*:log-stream:*",
                    ],
                }
            ],
        }
    ),
)
# </editor-fold>

# <editor-fold desc="lambda_execution_policy_attachment">
lambda_execution_policy_attachment = iam.RolePolicyAttachment(
    "lambda-execution-policy-attach",
    policy_arn=lambda_execution_policy.arn,
    role=lambda_access_role.name,
    opts=pulumi.ResourceOptions(depends_on=[lambda_access_role, lambda_execution_policy]),
)
# </editor-fold>

# <editor-fold desc="scheduler_execution_policy">

scheduler_execution_policy = iam.Policy(
    "scheduler-execution-policy",
    name=f"reminder-scheduler-execution-policy",
    path="/myfinances/management_bot/",
    policy=json.dumps(
        {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "InvokeLambda",
                    "Effect": "Allow",
                    "Action": ["lambda:InvokeFunction"],
                    "Resource": "arn:aws:lambda:*:*:function:myfinances_github_bot_reminders",
                },
                {
                    "Sid": "AllowEventbridgeScheduler",
                    "Effect": "Allow",
                    "Action": ["scheduler:*"],
                    "Resource": "*",
                },
            ],
        }
    ),
)
# </editor-fold>

# <editor-fold desc="scheduler_execution_role">
scheduler_execution_role = iam.Role(
    "scheduler-execution-role",
    name="reminder-scheduler-execution-role",
    path="/myfinances/management_bot/",
    assume_role_policy=json.dumps(
        {
            "Version": "2012-10-17",
            "Statement": [{"Effect": "Allow", "Principal": {"Service": "scheduler.amazonaws.com"}, "Action": "sts:AssumeRole"}],
        }
    ),
)
# </editor-fold>

# <editor-fold desc="scheduler_execution_policy_attachment">
scheduler_execution_policy_attachment = iam.RolePolicyAttachment(
    "scheduler-execution-policy-attach",
    policy_arn=scheduler_execution_policy.arn,
    role=scheduler_execution_role.name,
    opts=pulumi.ResourceOptions(depends_on=[scheduler_execution_policy, scheduler_execution_role]),
)
# </editor-fold>

scheduler_user = iam.User("scheduler_user", name="myfinances-github-bot-scheduler")

reminders_create_schedule_policy = iam.Policy(
    "reminders_create_schedule_policy",
    name="myfinances-github-bot-reminders-create-schedule-policy",
    path="/myfinances/management_bot/",
    policy=json.dumps(
        {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "AllowEventbridgeScheduler",
                    "Effect": "Allow",
                    "Action": ["scheduler:CreateSchedule"],
                    "Resource": "arn:aws:scheduler:*:*:schedule/myfinances-github-bot-remind_me/*",
                },
                {
                    "Sid": "AllowRolePass",
                    "Effect": "Allow",
                    "Action": ["iam:PassRole"],
                    "Resource": "arn:aws:iam::*:role/myfinances/management_bot/reminder-scheduler-execution-role",
                },
            ],
        }
    ),
)

iam.UserPolicyAttachment(
    "scheduler_user_policy_attachment",
    policy_arn=reminders_create_schedule_policy.arn,
    user=scheduler_user.name,
    opts=pulumi.ResourceOptions(depends_on=[reminders_create_schedule_policy, scheduler_user]),
)

scheduler_access_role_key = iam.AccessKey(
    "lambda_access_role_key", user=scheduler_user.name, opts=pulumi.ResourceOptions(depends_on=[scheduler_user])
)

lambda_layer = lambda_.LayerVersion(
    "lambda_layer", code=pulumi.FileArchive(config.require("lambda_zip_path")), layer_name="PyGithub_for_myfinances_management_bot"
)

reminder_handler_lambda_func = lambda_.Function(
    "reminder_lambda",
    name="myfinances_github_bot_reminders",
    role=lambda_access_role.arn,
    code=pulumi.AssetArchive({".": pulumi.FileArchive("./reminder_handler")}),
    handler="lambda_handler.lambda_handler",
    timeout=8,
    runtime=lambda_.Runtime.PYTHON3D12,
    environment=lambda_.FunctionEnvironmentArgs(variables={"ssm_prefix": "/myfinances/github_bot/"}),
    layers=[lambda_layer.arn, "arn:aws:lambda:eu-west-2:133256977650:layer:AWS-Parameters-and-Secrets-Lambda-Extension:11"],
    tags={"project": "MyFinancesBot"},
)

main_lambda_func = lambda_.Function(
    "webhook_lambda",
    name="myfinances_github_bot_webhooks",
    role=lambda_access_role.arn,
    code=pulumi.AssetArchive({".": pulumi.FileArchive("./webhook_handler")}),
    handler="lambda_handler.lambda_handler",
    timeout=8,
    runtime=lambda_.Runtime.PYTHON3D12,
    environment=lambda_.FunctionEnvironmentArgs(
        variables={
            "ssm_prefix": "/myfinances/github_bot/",
            "AWS_REMINDER_LAMBDA_ARN": reminder_handler_lambda_func.arn,
            "AWS_REMINDER_LAMBDA_ROLE_ARN": scheduler_execution_role.arn,
            "AWS_SCHEDULES_ACCESS_KEY_ID": scheduler_access_role_key.id,
            "AWS_SCHEDULES_SECRET_ACCESS_KEY": scheduler_access_role_key.secret,
            "AWS_SCHEDULES_REGION_NAME": region,
        }
    ),
    layers=[lambda_layer.arn, "arn:aws:lambda:eu-west-2:133256977650:layer:AWS-Parameters-and-Secrets-Lambda-Extension:11"],
    tags={"project": "MyFinancesBot"},
)

rest_api = apigateway.RestApi("managementApi")

# rest_api_main_resource = apigateway.Resource("main_resource", rest_api=rest_api.id, parent_id=rest_api.root_resource_id, path_part="/")

rest_api_main_resource_post = apigateway.Method(
    "main_post_method_for_webhook",
    rest_api=rest_api.id,
    resource_id=rest_api.root_resource_id,
    http_method="POST",
    authorization="NONE",
    api_key_required=False,
    request_parameters={
        "method.request.header.X-GitHub-Delivery": True,
        "method.request.header.X-GitHub-Event": True,
        "method.request.header.X-GitHub-Hook-ID": True,
        "method.request.header.X-GitHub-Hook-Installation-Target-ID": True,
        "method.request.header.X-GitHub-Hook-Installation-Target-Type": True,
    },
)

rest_api_lambda_integration = apigateway.Integration(
    "lambda_integration",
    rest_api=rest_api.id,
    resource_id=rest_api.root_resource_id,
    http_method="POST",
    integration_http_method="POST",
    type="AWS",
    timeout_milliseconds=8000,
    content_handling="CONVERT_TO_TEXT",
    uri=main_lambda_func.arn.apply(lambda arn: arn + ":${stageVariables.lambda_function_version}"),  # main_lambda_func.invoke_arn,
)

api_gw_200_resp = apigateway.MethodResponse(
    "200_resp",
    rest_api=rest_api.id,
    resource_id=rest_api.root_resource_id,
    http_method="POST",
    status_code="200",
    response_models={"application/json": "Empty"},
)

api_gw_integration_resp = apigateway.IntegrationResponse(
    "integ_resp",
    rest_api=rest_api.id,
    resource_id=rest_api.root_resource_id,
    http_method="POST",
    status_code="200",
    response_templates={"application/json": json.dumps({})},
)

api_gw_lambda = lambda_.Permission(
    "apigw_lambda",
    statement_id="AllowExecutionFromAPIGateway",
    action="lambda:InvokeFunction",
    function=main_lambda_func.name,
    principal="apigateway.amazonaws.com",
    source_arn=pulumi.Output.all(rest_api.id).apply(lambda id: f"arn:aws:execute-api:{region}:{account_id}:{id[0]}/*/POST/"),
)

deployment = apigateway.Deployment("deployment_resource", rest_api=rest_api.id)

prod_stage = apigateway.Stage(
    "productionStage",
    stage_name="production",
    rest_api=rest_api.id,
    deployment=deployment.id,
    opts=pulumi.ResourceOptions(ignore_changes=["variables", "deployment"]),
)

pulumi.export("invoke_url", prod_stage.invoke_url)
pulumi.export("scheduler_execution_role", scheduler_execution_role.arn)
pulumi.export("reminder_handler_lambda_func", reminder_handler_lambda_func.arn)
