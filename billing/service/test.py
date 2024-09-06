# import os
#
# import stripe
# from django.urls import reverse
#
# from backend.models import User
#
# user: User = User.objects.first()
#
# # stripe.billing.MeterEvent.create(
# #     event_name="invoices_created",
# #     payload={"invoices": "250", "stripe_customer_id": user.stripe_customer_id},
# #     # identifier="id"
# # )
# #
# # stripe.billing.Meter.list_event_summaries(
# #     ""
# # )
#
# # a = stripe.Customer.create(
# #     name=user.get_full_name(),
# #     email=user.email
# # )
# #
# # user.stripe_customer_id = a.id
# # user.save()
#
# # print(a)
#
# # stripe.checkout.Session.create(
# #     success_url=os.environ.get("SITE_URL", default="http://127.0.0.1:8000") + reverse("api:public:webhooks:receive_global"),
# #     line_items=[
# #         {
# #             "price": "price_",
# #             "quantity": 1
# #         }
# #     ]
# # )
