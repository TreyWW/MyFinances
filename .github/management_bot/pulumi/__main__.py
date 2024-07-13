from __future__ import annotations

import json
import pulumi

from pulumi_aws import apigateway, iam
from pulumi_aws import lambda_

config = pulumi.Config()

site_name: str = pulumi.get_project()
account_id = config.get("accountId", ":")
region = config.get("region", "eu-west-2")
tags = {"app": site_name}

# lambda_layer
lambda_access_role = iam.Role(
    "lambda_access_role",
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

lambda_layer = lambda_.LayerVersion(
    "lambda_layer", code=pulumi.FileArchive(config.require("lambda_zip_path")), layer_name="PyGithub_for_myfinances_management_bot"
)

lambda_func = lambda_.Function(
    "webhook_lambda",
    name="myfinances_github_bot_webhooks",
    role=lambda_access_role.arn,
    code=pulumi.AssetArchive({".": pulumi.FileArchive("./src")}),
    handler="lambda_handler.lambda_handler",
    timeout=8,
    runtime=lambda_.Runtime.PYTHON3D12,
    environment=lambda_.FunctionEnvironmentArgs(
        variables={"app_id": config.require_secret("app_id"), "private_key": config.require_secret("private_key")}
    ),
    layers=[lambda_layer.arn],
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
)

rest_api_lambda_integration = apigateway.Integration(
    "lambda_integration",
    rest_api=rest_api.id,
    resource_id=rest_api.root_resource_id,
    http_method="POST",
    integration_http_method="POST",
    type="AWS",
    timeout_milliseconds=8000,
    uri=lambda_func.invoke_arn,
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
    function=lambda_func.name,
    principal="apigateway.amazonaws.com",
    source_arn=pulumi.Output.all(rest_api.id).apply(lambda id: f"arn:aws:execute-api:{region}:{account_id}:{id[0]}/*/POST/"),
)

deployment = apigateway.Deployment("deployment_resource", rest_api=rest_api.id)

prod_stage = apigateway.Stage("productionStage", stage_name="production", rest_api=rest_api.id, deployment=deployment.id)

pulumi.export("invoke_url", prod_stage.invoke_url)
