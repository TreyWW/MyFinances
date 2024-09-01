from backend.models import User
from billing.models import UserSubscription


def get_user_from_stripe_customer(stripe_customer_id: str) -> User | None:
    return User.objects.filter(stripe_customer_id=stripe_customer_id).first()
