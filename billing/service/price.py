import stripe


def get_price_id_from_lookup_key(lookup_key: str) -> str:
    prices = stripe.Price.list(lookup_keys=[lookup_key])
    if prices.data:
        return prices.data[0].id  # Assuming the lookup key returns one price
    raise ValueError(f"Price with lookup key {lookup_key} not found.")
