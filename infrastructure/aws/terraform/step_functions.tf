resource "aws_sfn_state_machine" "scheduler-step-function" {
  name     = var.sfn_machine_name
  role_arn = aws_iam_role.scheduler-execution-role.arn
  type     = "STANDARD"
  logging_configuration {
    level = "OFF"
  }
  definition = jsonencode({
    "Comment" : "A description of my state machine",
    "StartAt" : "Call Schedule Endpoint",
    "States" : {
      "StartAt" : "Call Schedule Endpoint",
      "States" : {
        "Call Schedule Endpoint" : {
          "Type" : "Task",
          "Resource" : "arn:aws:states:::http:invoke",
          "Parameters" : {
            "Authentication" : {
              "ConnectionArn" : aws_cloudwatch_event_connection.invoice-scheduler-connection.arn
            },
            "Method" : "POST",
            "ApiEndpoint" : "${var.SITE_URL}/api/invoices/schedules/receive/",
            "RequestBody.$" : "$.body",
            "Headers.$" : "$.headers"
          },
          "Retry" : [
            {
              "ErrorEquals" : [
                "States.ALL"
              ],
              "BackoffRate" : 2,
              "IntervalSeconds" : 1,
              "MaxAttempts" : 3,
              "JitterStrategy" : "FULL"
            }
          ],
          "End" : true
        }
      },
      "Comment" : "Call our django api to alert the schedule timestamp has reached."
    }
  })
  tags = local.app_tags
}

resource "aws_iam_role" "scheduler-execution-role" {
  name               = "${var.SITE_NAME}-invoicing-scheduler-fn"
  path               = "/${var.SITE_NAME}-scheduled-invoices/"
  assume_role_policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        "Effect" : "Allow",
        "Principal" : {
          "Service" : "scheduler.amazonaws.com"
        },
        "Action" : "sts:AssumeRole"
      }
    ]
  })
  tags = local.app_tags
}

resource "aws_iam_role_policy" "scheduler-execution-policy" {
  policy     = aws_iam_policy.scheduler-execution-policy.id
  role       = aws_iam_role.scheduler-execution-role.id
  depends_on = [
    aws_iam_policy.scheduler-execution-policy,
    aws_iam_role.scheduler-execution-role
  ]
}

resource "aws_iam_policy" "scheduler-execution-policy" {
  name   = "${var.SITE_NAME}-invoicing-scheduler-fn"
  path   = "/${var.SITE_NAME}-scheduled-invoices/"
  policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        "Sid" : "CallAPIDestination",
        "Effect" : "Allow",
        "Action" : [
          "states:InvokeHTTPEndpoint",
          "states:StartExecution"
        ],
        "Resource" : [
          "*"
        ]
      },
      {
        "Sid" : "AccessSecrets",
        "Effect" : "Allow",
        "Action" : [
          "events:RetrieveConnectionCredentials",
          "secretsmanager:GetSecretValue",
          "secretsmanager:DescribeSecret"
        ],
        "Resource" : [
          "*"
        ]
      },
      {
        "Sid" : "CreateLogDelivery",
        "Effect" : "Allow",
        "Action" : [
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
        "Resource" : "*"
      },
      {
        "Sid" : "AllowEventbridgeScheduler",
        "Effect" : "Allow",
        "Action" : [
          "scheduler:*"
        ],
        "Resource" : [
          "*"
        ]
      }
    ]
  })
}