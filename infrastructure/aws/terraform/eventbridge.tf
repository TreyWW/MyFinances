resource "aws_scheduler_schedule_group" "invoice-schedules" {
  name = "${var.SITE_NAME}-invoice-schedules"
  tags = local.app_tags
}

resource "aws_scheduler_schedule_group" "invoice-reminders" {
  name = "${var.SITE_NAME}-invoice-reminders"
  tags = local.app_tags
}