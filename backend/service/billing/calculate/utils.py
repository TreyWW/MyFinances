from decimal import Decimal, ROUND_HALF_UP
from typing import Dict


def round_currency(value: Decimal) -> Decimal:
    """Round a decimal value to 2 decimal places using ROUND_HALF_UP."""
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def calculate_free_tier_cost(quantity: Decimal, free_units_remaining: Decimal, unit_name: str) -> dict:
    """Return details for usage within the free tier."""
    return {
        "description": f"£{0.00:.2f} for {free_units_remaining} {unit_name} (plan free tier)",
        "quantity": free_units_remaining,
        "cost": Decimal("0.00"),
    }


def calculate_chargeable_cost(quantity: Decimal, cost_per_unit: Decimal, units_per_cost: Decimal, unit: str, plan_name: str) -> Dict:
    """Calculate the chargeable cost for usage beyond the free tier."""
    return {
        "description": f"£{cost_per_unit:.2f} per {units_per_cost} {unit} ({plan_name} plan)",
        "quantity": quantity,
        "cost": (quantity / units_per_cost) * cost_per_unit,  # Ensure both are Decimal
    }
