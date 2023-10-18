import smtplib
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.mail import EmailMessage
from django.db import models
from settings import settings
from django.utils.crypto import get_random_string

# def RandomCode(length=6):
#     characters = string.ascii_letters + string.digits
#     return "".join(random.choice(characters) for _ in range(length))


def RandomCode(length=6):
    return get_random_string(length=length).upper()


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
    profile_picture = models.ImageField(
        upload_to="profile_pictures", blank=True, null=True
    )

    @property
    def profile_picture_url(self):
        if self.profile_picture and hasattr(self.profile_picture, "url"):
            return self.profile_picture.url

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name = "User Settings"
        verbose_name_plural = "User Settings"


class Team(models.Model):
    name = models.CharField(max_length=100)
    leader = models.ForeignKey(User, on_delete=models.CASCADE)
    members = models.ManyToManyField(User, related_name="teams_joined")


class TeamInvitation(models.Model):
    code = models.CharField(max_length=10)
    team = models.ForeignKey(
        Team, on_delete=models.CASCADE, related_name="team_invitations"
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="team_invitations"
    )
    invited_by = models.ForeignKey(User, on_delete=models.CASCADE)
    expires = models.DateTimeField(null=True, blank=True)
    active = models.BooleanField(default=True)

    def is_active(self):
        if not self.active:
            return False
        if timezone.now() > self.expires:
            self.active = False
            self.save()
            return False
        return True

    def set_expires(self):
        self.expires = timezone.now() + timezone.timedelta(days=7)

    def save(self, *args, **kwargs):
        self.set_expires()
        self.code = RandomCode(10)
        super().save()

    def __str__(self):
        return self.team.name

    class Meta:
        verbose_name = "Team Invitation"
        verbose_name_plural = "Team Invitations"


class Receipt(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to="receipts")
    total_price = models.FloatField(null=True, blank=True)
    date = models.DateField(null=True, blank=True)
    date_uploaded = models.DateTimeField(auto_now=True)
    receipt_parsed = models.JSONField(null=True, blank=True)


class Client(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    active = models.BooleanField(default=True)

    name = models.CharField(max_length=64)
    phone_number = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)

    address = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)

    # team = models.ForeignKey(Team,  on_delete=models.BLANK, blank=True, null=True)

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

    client_to = models.ForeignKey(
        Client, on_delete=models.SET_NULL, blank=True, null=True
    )

    client_name = models.CharField(max_length=100, blank=True, null=True)
    client_company = models.CharField(max_length=100, blank=True, null=True)
    client_address = models.CharField(max_length=100, blank=True, null=True)
    client_city = models.CharField(max_length=100, blank=True, null=True)
    client_county = models.CharField(max_length=100, blank=True, null=True)
    client_country = models.CharField(max_length=100, blank=True, null=True)

    self_name = models.CharField(max_length=100, blank=True, null=True)
    self_company = models.CharField(max_length=100, blank=True, null=True)
    self_address = models.CharField(max_length=100, blank=True, null=True)
    self_city = models.CharField(max_length=100, blank=True, null=True)
    self_county = models.CharField(max_length=100, blank=True, null=True)
    self_country = models.CharField(max_length=100, blank=True, null=True)

    sort_code = models.CharField(max_length=100, blank=True, null=True)
    account_holder_name = models.CharField(max_length=100, blank=True, null=True)
    account_number = models.CharField(max_length=100, blank=True, null=True)
    reference = models.CharField(max_length=100, blank=True, null=True)
    invoice_number = models.CharField(max_length=100, blank=True, null=True)
    vat_number = models.CharField(max_length=100, blank=True, null=True)
    logo = models.ImageField(upload_to="invoice_logos", blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

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
        invoice_id = self.invoice_id or self.id
        if self.client_name:
            client = self.client_name
        elif self.client_to:
            client = self.client_to.name
        else:
            client = "Unknown Client"

        return f"Invoice #{invoice_id} for {client}"

    def get_subtotal(self):
        subtotal = 0
        for item in self.items.all():
            subtotal += item.get_total_price()
        return round(subtotal, 2)

    def get_total_price(self):
        total = 0
        subtotal = self.get_subtotal()
        if self.vat_number:
            total = subtotal * 1.2
        else:
            total = subtotal
        return round(total, 2)


class PasswordSecret(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="password_secrets"
    )
    secret = models.TextField(max_length=300)
    expires = models.DateTimeField(null=True, blank=True)


class Notification(models.Model):
    action_choices = [
        ("normal", "Normal"),
        ("modal", "Modal"),
        ("redirect", "Redirect"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.CharField(max_length=100)
    action = models.CharField(max_length=10, choices=action_choices, default="normal")
    action_value = models.CharField(max_length=100, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)


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
