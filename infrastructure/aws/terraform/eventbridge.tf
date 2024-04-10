resource "aws_scheduler_schedule_group" "invoice-schedules" {
  name = "${var.SITE_NAME}-invoice-schedules"
  tags = local.app_tags
}
