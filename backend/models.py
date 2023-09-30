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
    return "".join(random.choice(characters) for _ in range(length))


class UserSettings(models.Model):
    CURRENCIES = {
        "GBP": {"name": "British Pound Sterling", "symbol": "£"},
        "EUR": {"name": "Euro", "symbol": "€"},
        "USD": {"name": "United States Dollar", "symbol": "$"},
        "JPY": {"name": "Japanese Yen", "symbol": "¥"},
        "INR": {"name": "Indian Rupee", "symbol": "₹"},
        "AUD": {"name": "Australian Dollar", "symbol": "$"},
        "CAD": {"name": "Canadian Dollar", "symbol": "$"},
    }
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="user_profile"
    )
    dark_mode = models.BooleanField(default=True)
    currency = models.CharField(
        max_length=3,
        default="GBP",
        choices=[(code, info["name"]) for code, info in CURRENCIES.items()],
    )

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name = "User Settings"
        verbose_name_plural = "User Settings"


class Client(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    email = models.EmailField()

    def __str__(self):
        return self.name


class InvoiceItem(models.Model):
    description = models.CharField(max_length=100)
    is_service = models.BooleanField(default=True)
    # if service
    hours = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    price_per_hour = models.DecimalField(
        max_digits=15, decimal_places=2, blank=True, null=True
    )
    # if product
    price = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)

    def get_total_price(self):
        if self.is_service:
            return self.hours * self.price_per_hour
        else:
            return self.price

    def __str__(self):
        return self.description


class Invoice(models.Model):
    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("paid", "Paid"),
        ("overdue", "Overdue"),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    invoice_id = models.IntegerField(unique=True, blank=True, null=True)  # todo: add
    client = models.ForeignKey(
        Client, on_delete=models.CASCADE, blank=True, null=True
    )  # todo: add

    payment_status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default="pending"
    )
    items = models.ManyToManyField(InvoiceItem)

    date_created = models.DateTimeField(auto_now_add=True)
    date_due = models.DateField()
    date_issued = models.DateField(blank=True, null=True)
    payment_status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default="pending"
    )

    def __str__(self):
        return f"Invoice #{self.invoice_id or self.id} for {self.client or 'Unknown Client'}"

    def get_total_price(self):
        total = 0
        for item in self.items.all():
            total += item.get_total_price()
        return total


class PasswordSecret(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="password_secrets"
    )
    secret = models.TextField(max_length=300)
    expires = models.DateTimeField(null=True, blank=True)


class AuditLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=100)
    date = models.DateTimeField(auto_now_add=True)  #


class LoginLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)


class Error(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    error = models.CharField(max_length=250, null=True)
    error_code = models.CharField(max_length=100, null=True)
    error_colour = models.CharField(max_length=25, default="danger")
    date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.user_id)


class TracebackError(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    error = models.CharField(max_length=5000, null=True)
    date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.error)


def SEND_SENDGRID_EMAIL(
    to_email,
    subject,
    content,
    from_email="myfinances@strelix.org",
    request=None,
    **kwargs,
):
    DESTINATION = kwargs.get("DESTINATION") or to_email
    SUBJECT = kwargs.get("SUBJECT") or subject
    CONTENT = kwargs.get("CONTENT") or content
    FROM = kwargs.get("FROM") or from_email
    request = kwargs.get("request") or request

    if not isinstance(DESTINATION, list):
        DESTINATION = [DESTINATION]
    msg = EmailMessage(subject=SUBJECT, from_email=FROM, to=DESTINATION, body=CONTENT)

    DATA = {"first_name": "list", "content": CONTENT}

    msg.template_id = settings.SENDGRID_TEMPLATE
    msg.dynamic_template_data = DATA
    msg.template_data = DATA

    try:
        msg.send(fail_silently=False)

    except smtplib.SMTPConnectError as error:
        if request:
            messages.error(
                request,
                "Failed to connect to our email server. Please try again later or report this issue to our team.",
            )
        print(f"[ERROR] {error}", flush=True)
        TracebackError(error=error).save()
        return False, "Failed to connect to our email server."

    except smtplib.SMTPException as error:
        if request:
            messages.error(
                request,
                "Failed to connect to our email server. Please try again later or report this issue to our team.",
            )
        print(f"[ERROR] {error}", flush=True)
        TracebackError(error=error).save()
        return False, error
    except Exception as error:
        print(f"[ERROR] {error}", flush=True)
        TracebackError(error=error).save()
        return False, "Error"
