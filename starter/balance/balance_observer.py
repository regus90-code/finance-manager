"""Observer pattern: objects that react when the balance changes."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable

from balance.formatting import format_money
from transaction.transaction import Transaction


class IBalanceObserver(ABC):
    """Interface for everything that wants to hear about balance changes."""

    @abstractmethod
    def update(self, balance: float, transaction: Transaction) -> None:
        """Handle balance updates.

        Args:
            balance: The net balance after ``transaction`` was applied.
            transaction: The transaction that changed the balance.
        """


class PrintObserver(IBalanceObserver):
    """Prints the new balance after every transaction.

    Args:
        output: Where the message goes. Defaults to ``print``; tests pass a
            list's ``append`` instead.
    """

    def __init__(self, output: Callable[[str], None] = print) -> None:
        self._output = output

    def update(self, balance: float, transaction: Transaction) -> None:
        """Print balance update message."""
        self._output(f"Applied {transaction} -> balance: {format_money(balance)}")


class LowBalanceAlertObserver(IBalanceObserver):
    """Alerts the user while the balance is below ``threshold``.

    ``alert_triggered`` always reflects the latest update: True while the
    balance is below the threshold, False again once it has recovered. A
    balance exactly at the threshold is not an alert.

    Args:
        threshold: The lowest balance that is still fine.
        output: Where the alert goes. Defaults to ``print``.
    """

    def __init__(self, threshold: float, output: Callable[[str], None] = print) -> None:
        self.threshold = threshold
        self.alert_triggered = False
        self._output = output

    def update(self, balance: float, transaction: Transaction) -> None:
        """Alert if balance drops below threshold."""
        self.alert_triggered = balance < self.threshold
        if self.alert_triggered:
            self._output(
                f"ALERT: Low balance! {format_money(balance)} is below "
                f"the threshold of {format_money(self.threshold)}."
            )
