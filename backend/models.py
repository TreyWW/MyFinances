import random
import smtplib
import string

from django.contrib import messages
from django.contrib.auth.models import User
from django.core.mail import EmailMessage
from django.db import models

from settings import settings


def RandomCode(length=6):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user_profile')
    dark_mode = models.BooleanField(default=True)


class PasswordSecrets(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='password_secrets')
    secret = models.TextField(max_length=300)
    expires = models.DateTimeField(null=True, blank=True)


class AuditLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=100)
    date = models.DateTimeField(auto_now_add=True)  #


class LoginLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)


class Errors(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    error = models.CharField(max_length=250, null=True)
    error_code = models.CharField(max_length=100, null=True)
    error_colour = models.CharField(max_length=25, default='danger')
    date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.user_id)


class TracebackErrors(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    error = models.CharField(max_length=5000, null=True)
    date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.error)


def SEND_SENDGRID_EMAIL(DESTINATION, SUBJECT, CONTENT, FROM='myfinances@strelix.org', request=None):
    if not isinstance(DESTINATION, list):
        DESTINATION = [DESTINATION]
    msg = EmailMessage(
        subject=SUBJECT,
        from_email=FROM,
        to=DESTINATION,
        body=CONTENT
    )

    DATA = {
        "first_name": "list",
        "content": CONTENT
    }

    msg.template_id = settings.SENDGRID_TEMPLATE
    msg.dynamic_template_data = DATA
    msg.template_data = DATA

    try:
        msg.send(fail_silently=False)

    except smtplib.SMTPConnectError as error:
        if request:
            messages.error(request,
                           "Failed to connect to our email server. Please try again later or report this issue to our team.")
        print(f"[ERROR] {error}", flush=True)
        TracebackErrors(error=error).save()
        return False, "Failed to connect to our email server."

    except smtplib.SMTPException as error:
        if request:
            messages.error(request,
                           "Failed to connect to our email server. Please try again later or report this issue to our team.")
        print(f"[ERROR] {error}", flush=True)
        TracebackErrors(error=error).save()
        return False, error
    except Exception as error:
        print(f"[ERROR] {error}", flush=True)
        TracebackErrors(error=error).save()
        return False, "Error"
