from django.core.exceptions import ValidationError
from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext as _

from backend.models import OwnerBase, USER_OR_ORGANIZATION_CONSTRAINT
from backend.service.onboarding.utils import generate_unique_slug
import uuid


class OnboardingBooking(OwnerBase):
    uuid = models.UUIDField(_("UUID"), unique=True, null=True, default=uuid.uuid4, blank=True)

    primary_email = models.EmailField(_("Primary User Email"))
    name = models.CharField(_("Name"), max_length=100, null=True, blank=True)
    day = models.DateField(_("Day"))
    start_time = models.TimeField(_("Time"))
    end_time = models.TimeField(_("Time"))
    venue = models.CharField(_("Venue"), max_length=100)
    rooms = models.JSONField(_("Rooms"), default=list)
    notes = models.TextField(_("Notes"), blank=True)
    hourly_rate = models.DecimalField(_("Hourly Rate"), max_digits=10, decimal_places=2, null=True, blank=True)
    deposit = models.DecimalField(_("Deposit"), max_digits=10, decimal_places=2, null=True, blank=True)
    deposit_paid = models.BooleanField(_("Deposit Paid"), default=False)

    is_confirmed = models.BooleanField(_("Confirmed"), default=False)
    is_cancelled = models.BooleanField(_("Cancelled"), default=False)

    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated At"), auto_now=True)
    cancelled_at = models.DateTimeField(_("Cancelled At"), null=True, blank=True)

    class Meta:
        verbose_name = _("Onboarding Booking")
        verbose_name_plural = _("Onboarding Bookings")

    def __str__(self):
        return f"{self.name} ({self.day})"


class OnboardingFormManager(models.Manager): ...


class OnboardingForm(OwnerBase):
    objects = OnboardingFormManager()

    title = models.CharField(_("Title"), max_length=50)
    # slug = models.SlugField(_("Slug"), max_length=100, unique=True)
    uuid = models.UUIDField(_("UUID"), unique=True, null=True, default=uuid.uuid4, blank=True)

    intro_text = models.TextField(_("Intro"), blank=True)
    btn_text = models.CharField(_("Button Text"), default=_("Submit"), max_length=50, blank=True)
    response_text = models.TextField(_("Response"), blank=True)

    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated At"), auto_now=True)

    send_customer_email = models.BooleanField(_("Send Email"), default=False)
    customer_email_subject = models.CharField(_("Email Subject"), max_length=200, blank=True)
    customer_email_body = models.TextField(_("Email Body"), blank=True)

    send_owner_email = models.EmailField(_("Email Copy To"), blank=True)
    owner_email_subject = models.CharField(_("Email Subject"), max_length=200, blank=True)
    owner_email_body = models.TextField(_("Email Body"), blank=True)

    class Meta:
        verbose_name = _("Onboarding Form")
        verbose_name_plural = _("Onboarding Forms")

        constraints = [USER_OR_ORGANIZATION_CONSTRAINT()]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # if not self.slug:
        #     self.slug = generate_unique_slug(self.objects, "slug", slugify(self.title))
        super().save(*args, **kwargs)


class OnboardingFieldManager(models.Manager):
    def visible(self):
        return self.filter(visible=True)


class OnboardingField(models.Model):
    class FieldTypes(models.TextChoices):
        TEXT = "text", _("Text")
        EMAIL = "email", _("Email")
        CHECKBOX = "checkbox", _("Checkbox")
        DATE = "date", _("Date")
        TIME = "time", _("Time")
        DATETIME = "datetime", _("Combined Datetime")

    uuid = models.UUIDField(_("UUID"), unique=True, default=uuid.uuid4)
    form = models.ForeignKey(OnboardingForm, on_delete=models.CASCADE, related_name="fields")
    label = models.CharField(_("Label"), max_length=100)
    name = models.CharField(_("Name"), max_length=100)
    type = models.CharField(_("Type"), max_length=16, choices=FieldTypes.choices)
    visible = models.BooleanField(_("Visible"), default=True)
    required = models.BooleanField(_("Required"), default=False)
    order = models.PositiveSmallIntegerField(_("Order"), default=1000)

    objects = OnboardingFieldManager()

    class Meta:
        verbose_name = _("Onboarding Field")
        verbose_name_plural = _("Onboarding Fields")

    def __str__(self):
        return self.label

    def clean(self):
        if self.type not in self.FieldTypes.values:
            raise ValidationError(_("Invalid field type"))


class OnboardingFieldEntry(models.Model):
    field = models.ForeignKey(OnboardingField, on_delete=models.CASCADE, related_name="entries")
    value = models.TextField(_("Value"), blank=True)

    class Meta:
        verbose_name = _("Onboarding Field Entry")
        verbose_name_plural = _("Onboarding Field Entries")

    def __str__(self):
        return self.field.label


# class OnboardingFlowStep(models.Model):
#     ...
#
#
# class OnboardingFlow(OwnerBase):
#
#     steps = models.ManyToManyField(OnboardingFlowStep, verbose_name=_("Steps"))
#
#     class Meta:
#         verbose_name = _("Onboarding Flow")
#         verbose_name_plural = _("Onboarding Flows")
