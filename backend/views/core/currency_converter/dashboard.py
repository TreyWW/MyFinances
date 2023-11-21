from forex_python.converter import CurrencyRates


def convert_currency(init_currency, target_currency, amount):
    """
    Converts one currency to another, given an amount, using the forex_python library

    Parameters
    ----------
    init_currency : str, required
        The code for the initial currency to be converted

    target_currency : str, required
        The code for the target currency to be converted to

    amount : int or float, required
        The amount to be converted

    Returns
    ----------
    Returns an int or float representing the new amount
    """
    if not isinstance(init_currency, str) or len(init_currency) != 3:
        raise ValueError("Initial currency not recognized")

    if not isinstance(target_currency, str) or len(target_currency) != 3:
        raise ValueError("Target currency not recognized")

    if not isinstance(amount, (int, float)):
        raise ValueError("Amount is not an accepted datatype")

    currency_rates = CurrencyRates()

    try:
        target_amount = currency_rates.get_rates(init_currency, target_currency, amount)
        return round(target_amount, 2)
    except Exception as e:
        # Handle specific exceptions raised by forex_python if needed
        raise ValueError(f"Error in currency conversion: {e}")
