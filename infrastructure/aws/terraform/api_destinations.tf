resource "aws_cloudwatch_event_api_destination" "invoice-scheduler-destination" {
  name                = "${var.SITE_NAME}-scheduled-invoices"
  description         = "MyFinances Scheduled Invoices"
  connection_arn      = aws_cloudwatch_event_connection.invoice-scheduler-connection.arn
  invocation_endpoint = "${var.SITE_URL}/api/invoices/schedules/receive/"
  http_method         = "POST"
}

resource "aws_cloudwatch_event_connection" "invoice-scheduler-connection" {
  name               = "${var.SITE_NAME}-scheduled-invoices"
  description        = "Example API Destination Connection"
  authorization_type = "API_KEY"

  auth_parameters {
    api_key {
      key   = "Authorization"
      value = "Token ${var.api_destination-api_key}"
    }
  }
}