"""The two kinds of transaction the finance manager knows."""

from __future__ import annotations

from enum import Enum


class TransactionCategory(Enum):
    """Whether a transaction adds money (income) or removes it (expense)."""

    INCOME = "Income"
    EXPENSE = "Expense"

    @property
    def opposite(self) -> TransactionCategory:
        """The category that cancels this one out.

        Used to undo transactions.
        """
        if self is TransactionCategory.INCOME:
            return TransactionCategory.EXPENSE
        return TransactionCategory.INCOME
