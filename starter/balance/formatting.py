"""Formatting of money amounts for console output."""


def format_money(amount: float) -> str:
    """Format an amount in dollars, e.g. ``1234.5 -> "$1,234.50"``.

    Negative amounts put the sign before the dollar sign: ``"-$40.00"``.
    """
    sign = "-" if amount < 0 else ""
    return f"{sign}${abs(amount):,.2f}"
