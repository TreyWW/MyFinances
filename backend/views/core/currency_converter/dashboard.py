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
        print("Initial currency not recognized, returning original amount")
        return amount
    if not isinstance(target_currency, str) or len(target_currency) != 3:
        print("Target currency not recognized, returning original amount")
        return amount
    if not isinstance(amount, int) or not isinstance(amount, float):
        print("Amount is not an accepted datatype, returning original amount")
        return amount

    currency_rates = CurrencyRates()

    target_amount = currency_rates.get_rates(init_currency, target_currency, amount)

    return round(target_amount, 2)
