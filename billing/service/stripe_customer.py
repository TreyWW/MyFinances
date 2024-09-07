from backend.models import User, Organization
import stripe


def get_or_create_customer_id(actor: User | Organization) -> str:
    if actor.stripe_customer_id:
        return actor.stripe_customer_id

    return create_stripe_customer_id(actor)


def create_stripe_customer_id(actor: User | Organization) -> str:
    if isinstance(actor, User):
        customer = stripe.Customer.create(
            email=actor.email,
            name=actor.get_full_name(),
        )
        actor.stripe_customer_id = customer.id
        actor.save()

        return customer.id

    else:
        customer = stripe.Customer.create(
            email=actor.leader.email,
            name=actor.name,
        )

        actor.stripe_customer_id = customer.id
        actor.save()

        return customer.id
