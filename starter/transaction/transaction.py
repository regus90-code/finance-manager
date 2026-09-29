"""The app's own transaction type: an amount plus a category."""

from __future__ import annotations

import math

from transaction.transaction_category import TransactionCategory


class Transaction:
    """Represents a financial transaction with an amount and category.

    Transactions are immutable value objects: two transactions with the same
    amount and category are equal and have the same hash. The amount is always
    positive; the category decides whether it is added or subtracted.
    """

    __slots__ = ("_amount", "_category")

    def __init__(self, amount: float, category: TransactionCategory) -> None:
        """Create a transaction.

        Raises:
            TypeError: If ``amount`` is not an int or float.
            ValueError: If ``amount`` is not a positive, finite number.
        """
        if isinstance(amount, bool) or not isinstance(amount, (int, float)):
            raise TypeError(
                f"amount must be a number, got {type(amount).__name__}"
            )
        if not math.isfinite(amount) or amount <= 0:
            raise ValueError(
                f"amount must be positive and finite, got {amount}"
            )
        self._amount = amount
        self._category = category

    @property
    def amount(self) -> float:
        """The positive amount of money moved by this transaction."""
        return self._amount

    @property
    def category(self) -> TransactionCategory:
        """Whether the amount is income or an expense."""
        return self._category

    def inverse(self) -> Transaction:
        """Return the transaction that cancels this one out."""
        return Transaction(self._amount, self._category.opposite)

    def __str__(self) -> str:
        return f"Transaction(${self._amount}, category='{self._category}')"

    __repr__ = __str__

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Transaction):
            return NotImplemented
        return (self._amount, self._category) == (
            other._amount,
            other._category,
        )

    def __hash__(self) -> int:
        return hash((self._amount, self._category))
