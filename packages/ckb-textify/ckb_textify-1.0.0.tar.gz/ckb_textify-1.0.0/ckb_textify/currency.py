# ckb_textify/currency.py
from .number_to_text import number_to_kurdish_text

# Currency info map: key -> (Kurdish main currency name, subunit name, subunit factor)
CURRENCY_MAP = {
    "IQD": ("دیناری عێڕاقی", "فلس", 100),  # Iraqi Dinar & cent
    "د.ع": ("دیناری عێڕاقی", "فلس", 100),
    "د،ع": ("دیناری عێڕاقی", "فلس", 100),
    "$": ("دۆلار", "سەنت", 100),
    "USD": ("دۆلار", "سەنت", 100),
    "€": ("یۆرۆ", "سەنت", 100),
    "EUR": ("یۆرۆ", "سەنت", 100),
}

def currency_to_kurdish_text(amount: str) -> str:
    """
    Convert currency string to Kurdish text.
    Examples:
      "$23.2" -> "بیست و سێ دۆلار و بیست سەنت"
      "IQD 23.3" -> "بیست و سێ دیناری عێڕاقی و سی سەنت"
      "€40.5" -> "چل یۆرۆ و نیو"
    """

    # Normalize input
    amount = amount.strip()

    # Find currency symbol/key
    currency_key = None
    value_str = None

    for key in CURRENCY_MAP:
        if amount.startswith(key):
            currency_key = key
            value_str = amount[len(key):].strip()
            break
        elif amount.endswith(key):
            currency_key = key
            value_str = amount[:-len(key)].strip()
            break

    # If not found, try splitting by space
    if currency_key is None and " " in amount:
        parts = amount.split(" ", 1)
        if parts[0] in CURRENCY_MAP:
            currency_key = parts[0]
            value_str = parts[1].strip()

    if currency_key is None:
        raise ValueError(f"Currency symbol not recognized in '{amount}'")

    kurd_currency, kurd_subunit, subunit_factor = CURRENCY_MAP[currency_key]

    # Convert value to float
    value_str = value_str.replace(",", "")  # remove commas if any
    value = float(value_str)

    integer_part = int(value)
    decimal_part = round((value - integer_part) * subunit_factor)

    # Convert integer part
    integer_text = number_to_kurdish_text(integer_part)

    # Handle decimals
    if decimal_part == 0:
        return f"{integer_text} {kurd_currency}"
    else:
        decimal_text = number_to_kurdish_text(decimal_part)
        return f"{integer_text} {kurd_currency} و {decimal_text} {kurd_subunit}"
