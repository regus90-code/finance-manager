"""Command objects that change the balance."""

from abc import ABC, abstractmethod

from balance.balance import Balance
from transaction.transaction import Transaction


class Command(ABC):
    """An action that can be executed and undone again."""

    @abstractmethod
    def execute(self) -> None:
        """Perform the action."""

    @abstractmethod
    def undo(self) -> None:
        """Reverse the effect of ``execute``."""


class ApplyTransactionCommand(Command):
    """Applies one transaction to a balance.

    Undo applies the inverse transaction instead of changing the balance
    directly, so observers are notified about the correction as well (e.g. a
    low-balance alert fires when undoing an income).

    Args:
        balance: The balance to change. Injected, so the command does not
            depend on how the balance is created.
        transaction: The transaction to apply.
    """

    def __init__(self, balance: Balance, transaction: Transaction) -> None:
        self._balance = balance
        self._transaction = transaction

    def execute(self) -> None:
        self._balance.apply_transaction(self._transaction)

    def undo(self) -> None:
        self._balance.apply_transaction(self._transaction.inverse())
