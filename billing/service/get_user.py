from backend.models import User, Organization


def get_actor_from_stripe_customer(stripe_customer_id: str) -> User | Organization | None:
    return (
        User.objects.filter(stripe_customer_id=stripe_customer_id).first()
        or Organization.objects.filter(stripe_customer_id=stripe_customer_id).first()
    )
