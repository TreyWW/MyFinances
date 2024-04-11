from __future__ import annotations
import os
import pulumi

config = pulumi.Config()

SITE_ABUSE_EMAIL = config.require("ses_abuse_email")

default_user_send_email_footer_text = (
    """
    Note: This was originally sent by {{sender_name}} (#uid {{sender_id}}) manually and NOT an official email by MyFinances
"""
    + f"\n To report this email, please contact {SITE_ABUSE_EMAIL}"
)

default_user_send_email_footer_html = (
    """
    <p>Note: This was originally sent by {{sender_name}} (#uid {{sender_id}}) manually and NOT an official email by MyFinances</p>

"""
    + f'<p>To report this email, please contact <a href="mailto:{SITE_ABUSE_EMAIL}">{SITE_ABUSE_EMAIL}</a>'
)

default_user_send_email_content_html = "<p>{{content_html}}</p><br>" + default_user_send_email_footer_html

default_user_send_email_content_text = "{{content_text}}\n" + default_user_send_email_footer_text

default_user_send_email_subject = "{{subject}}"

default_email_templates = {
    "user_send_email": {
        "subject": default_user_send_email_subject,
        "content_html": default_user_send_email_content_html,
        "content_text": default_user_send_email_content_text,
    }
}

default_reminder_template_name = "Hi {{client_name}}"
default_reminder_template_failure_to_pay = "Failure to pay the invoice may come with an added late fee depending on the merchant"
default_reminder_template_footer = """
Note: This is an automated email sent out by MyFinances on behalf of '{{company}}'. If you
believe this is spam or fraudulent please report it to us and DO NOT pay the invoice. Once a report has been made you will
have a case opened.
"""

default_reminder_overdue_content = "This is an automated email to let you know that your invoice #{{invoice_id}} is due TODAY."
default_reminder_before_due_content = (
    "This is an automated email to let you know that your invoice #{{invoice_id}} is due in {{days}} " "days."
)
default_reminder_after_due_content = (
    "This is an automated email to let you know that your invoice #{{invoice_id}} is past due by {{" "days}} " "days."
)

default_reminder_subject = "REMINDER | Invoice #{{invoice_id}}"


default_reminder_overdue = {
    "text": f"""
        {default_reminder_template_name}

        {default_reminder_overdue_content}

        {default_reminder_template_failure_to_pay}

        {default_reminder_template_footer}
    """,
    "html": f"""
        <h1>{default_reminder_template_name}</h1>

        <p>{default_reminder_overdue_content}</p>

        <p>{default_reminder_template_failure_to_pay}</p>

        <p>{default_reminder_template_footer}</p>
    """,
}

default_reminder_before_due = {
    "text": f"""
        {default_reminder_template_name}

        {default_reminder_before_due_content}

        {default_reminder_template_failure_to_pay}

        {default_reminder_template_footer}
    """,
    "html": f"""
        <h1>{default_reminder_template_name}</h1>

        <p>{default_reminder_before_due_content}</p>

        <p>{default_reminder_template_failure_to_pay}</p>

        <p>{default_reminder_template_footer}</p>
    """,
}

default_reminder_after_due = {
    "text": f"""
        {default_reminder_template_name}

        {default_reminder_after_due_content}

        {default_reminder_template_failure_to_pay}

        {default_reminder_template_footer}
    """,
    "html": f"""
        <h1>{default_reminder_template_name}</h1>

        <p>{default_reminder_after_due_content}</p>

        <p>{default_reminder_template_failure_to_pay}</p>

        <p>{default_reminder_template_footer}</p>
    """,
}

default_reminders = {
    "subject": default_reminder_subject,
    "overdue": {"text": default_reminder_overdue["text"], "html": default_reminder_overdue["html"]},
    "before_due": {"text": default_reminder_before_due["text"], "html": default_reminder_before_due["html"]},
    "after_due": {"text": default_reminder_after_due["text"], "html": default_reminder_after_due["html"]},
}
