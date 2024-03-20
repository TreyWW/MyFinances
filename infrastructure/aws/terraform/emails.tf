resource "aws_ses_template" "reminder-overdue" {
  name    = "${var.SITE_NAME}-reminders-overdue"
  subject = "REMINDER | Invoice #{{invoice_id}} is shortly overdue"
  text    = local.aws_ses_reminder_template_OVERDUE
}

resource "aws_ses_template" "reminder-before-due" {
  name    = "${var.SITE_NAME}-reminders-before-due"
  subject = "REMINDER | Invoice #{{invoice_id}} is due in {{days}} days"
  text    = local.aws_ses_reminder_template_BEFORE_DUE
}

resource "aws_ses_template" "reminder-after-due" {
  name    = "${var.SITE_NAME}-reminders-after-due"
  subject = "REMINDER | Invoice #{{invoice_id}} is past due by {{days}} days"
  text    = local.aws_ses_reminder_template_AFTER_DUE
}


locals {
  aws_ses_reminder_template_OVERDUE    = <<EMAIL
      ${var.aws_ses_reminder_template_NAME}

      This is an automated email to let you know that your invoice #{{invoice_id}} is due TODAY.

      You can view the invoice here: {{invoice_url}}

      ${var.aws_ses_reminder_template_FAILURE_TO_PAY}

      ${var.aws_ses_reminder_template_FOOTER}
   EMAIL
  aws_ses_reminder_template_BEFORE_DUE = <<EMAIL
      ${var.aws_ses_reminder_template_NAME}

      This is an automated email to let you know that your invoice #{{invoice_id}} is due in {{days}} days.

      You can view the invoice here: {{invoice_url}}

      ${var.aws_ses_reminder_template_FAILURE_TO_PAY}

      ${var.aws_ses_reminder_template_FOOTER}
   EMAIL
  aws_ses_reminder_template_AFTER_DUE  = <<EMAIL
        ${var.aws_ses_reminder_template_NAME}

        This is an automated email to let you know that your invoice #{{invoice_id}} is past due by {{days}} days.

        You can view the invoice here: {{invoice_url}}

        ${var.aws_ses_reminder_template_FAILURE_TO_PAY}

        ${var.aws_ses_reminder_template_FOOTER}
     EMAIL
}

variable "aws_ses_reminder_template_NAME" {
  type    = string
  default = "Hi {{client_name}},"
}

variable "aws_ses_reminder_template_FAILURE_TO_PAY" {
  type    = string
  default = "Failure to pay the invoice may come with an added late fee depending on the merchant."
}

variable "aws_ses_reminder_template_FOOTER" {
  type    = string
  default = <<EOH
  Best regards

  Note: This is an automated email sent out by MyFinances on behalf of '{{company}}'. If you
  believe this is spam or fraudulent please report it to us and DO NOT pay the invoice. Once a report has been made you will
  have a case opened.
  EOH
}