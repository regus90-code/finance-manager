"""This module serves as the entry point for the program."""

from __future__ import annotations

from collections.abc import Iterable

from balance.balance import Balance
from balance.balance_observer import (
    IBalanceObserver,
    LowBalanceAlertObserver,
    PrintObserver,
)
from commands.command_history import CommandHistory
from commands.transaction_command import ApplyTransactionCommand
from transaction.external_income_transaction import ExternalFreelanceIncome
from transaction.transaction import Transaction
from transaction.transaction_adapter import TransactionAdapter
from transaction.transaction_category import TransactionCategory

LOW_BALANCE_THRESHOLD = 100


def create_balance(observers: Iterable[IBalanceObserver]) -> Balance:
    """Return the shared balance with ``observers`` registered."""
    balance = Balance.get_instance()
    for observer in observers:
        balance.register_observer(observer)
    return balance


def build_transactions() -> list[Transaction]:
    """Return the demo transactions, including one adapted external income."""
    transactions = [
        Transaction(100, TransactionCategory.INCOME),
        Transaction(50, TransactionCategory.EXPENSE),
        Transaction(200, TransactionCategory.INCOME),
        Transaction(75, TransactionCategory.EXPENSE),
    ]

    # Create an external income transaction (via Adapter pattern)
    freelance_income = ExternalFreelanceIncome(
        1200, "INV-98765", "Mobile App Project"
    )
    adapter = TransactionAdapter(freelance_income)
    return transactions + [adapter.to_transaction()]


def main() -> None:
    print("Adding transactions...")
    balance = create_balance(
        [
            PrintObserver(),
            LowBalanceAlertObserver(threshold=LOW_BALANCE_THRESHOLD),
        ]
    )
    history = CommandHistory()

    for transaction in build_transactions():
        history.execute(ApplyTransactionCommand(balance, transaction))
    print(balance.summary())

    print("\nUndoing the last transaction...")
    history.undo()
    print(balance.summary())

    print("\nRedoing it...")
    history.redo()
    print(balance.summary())


if __name__ == "__main__":
    main()
