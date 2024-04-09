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
