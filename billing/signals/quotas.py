# from django.db.models.signals import post_save
# from django.dispatch import receiver
#
# from backend.finance.models import Invoice, Usage
#
#
# @receiver(post_save, sender=Invoice)
# def created_invoice(sender, instance: Invoice, **kwargs):
#     Usage.objects.create(
#         owner=instance.owner,
#         feature="invoices-created",
#         quantity=1,
#         unit="invocations",
#         instance_id=instance.id,
#     )
