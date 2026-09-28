"""The user's net balance: a Singleton that notifies its observers."""

from __future__ import annotations

import threading
from typing import ClassVar, Optional

from balance.balance_observer import IBalanceObserver
from balance.formatting import format_money
from transaction.transaction import Transaction
from transaction.transaction_category import TransactionCategory

# Only get_instance() knows this key, so Balance() cannot be called directly.
_CREATION_KEY = object()


class Balance:
    """Singleton to track the balance.

    There is exactly one balance per application, so every part of the app
    reads and changes the same number. Get it with ``Balance.get_instance()``;
    calling ``Balance()`` directly raises ``RuntimeError``.

    ``Balance`` is also the subject of the Observer pattern: every change goes
    through ``apply_transaction``, which notifies all registered observers.
    """

    _instance: ClassVar[Optional[Balance]] = None
    _lock: ClassVar[threading.Lock] = threading.Lock()

    def __init__(self, _key: object = None) -> None:
        """Initialize the balance. Prevent direct instantiation."""
        if _key is not _CREATION_KEY:
            raise RuntimeError("Balance is a singleton; use Balance.get_instance()")
        self._balance = 0.0
        self._observers: list[IBalanceObserver] = []

    @classmethod
    def get_instance(cls) -> Balance:
        """Return the single balance, creating it on first use (thread-safe)."""
        with cls._lock:
            if cls._instance is None:
                cls._instance = cls(_CREATION_KEY)
            return cls._instance

    def reset(self) -> None:
        """Reset the net balance to zero. Observers are kept and not notified."""
        self._balance = 0.0

    def register_observer(self, observer: IBalanceObserver) -> None:
        """Notify ``observer`` of every future change. Registering twice is a no-op."""
        if observer not in self._observers:
            self._observers.append(observer)

    def unregister_observer(self, observer: IBalanceObserver) -> None:
        """Stop notifying ``observer``.

        Raises:
            ValueError: If ``observer`` is not registered.
        """
        self._observers.remove(observer)

    def clear_observers(self) -> None:
        """Unregister all observers."""
        self._observers.clear()

    def add_income(self, amount: float) -> None:
        """Add income to the balance."""
        self.apply_transaction(Transaction(amount, TransactionCategory.INCOME))

    def add_expense(self, amount: float) -> None:
        """Subtract expense from the balance."""
        self.apply_transaction(Transaction(amount, TransactionCategory.EXPENSE))

    def apply_transaction(self, transaction: Transaction) -> None:
        """Apply a Transaction object to update the balance.

        Args:
            transaction: The transaction to apply.

        Raises:
            ValueError: If the transaction's category is neither income nor
                expense. The balance is not changed in that case.
        """
        if transaction.category is TransactionCategory.INCOME:
            self._balance += transaction.amount
        elif transaction.category is TransactionCategory.EXPENSE:
            self._balance -= transaction.amount
        else:
            raise ValueError(f"Unknown transaction category: {transaction.category!r}")
        self._notify(transaction)

    def get_balance(self) -> float:
        """Get the current net balance."""
        return self._balance

    def summary(self) -> str:
        """Return a summary string of the net balance."""
        return f"Net balance: {format_money(self._balance)}"

    def _notify(self, transaction: Transaction) -> None:
        # Iterate over a copy so an observer may unregister itself in update().
        for observer in list(self._observers):
            observer.update(self._balance, transaction)
