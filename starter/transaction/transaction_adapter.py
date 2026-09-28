"""Adapter pattern: turns external freelance income into app transactions."""

from transaction.external_income_transaction import ExternalFreelanceIncome
from transaction.transaction import Transaction
from transaction.transaction_category import TransactionCategory


class TransactionAdapter:
    """Lets the app use an ``ExternalFreelanceIncome`` as a ``Transaction``.

    The rest of the app only knows ``Transaction``, so it never depends on the
    freelance platform's format. If the platform changes its format, only this
    class changes.
    """

    def __init__(self, external_transaction: ExternalFreelanceIncome) -> None:
        self.external_transaction = external_transaction

    def to_transaction(self) -> Transaction:
        """Convert an external transaction to a standard Transaction.

        The invoice ID and description are not part of ``Transaction`` and
        are dropped.

        Raises:
            ValueError: If the external record is not income or its amount
                is invalid. External data is checked here because the app
                does not control it.
        """
        external = self.external_transaction
        if external.typ != "income":
            raise ValueError(
                f"Unsupported external transaction type '{external.typ}' "
                f"(invoice {external.invoice_id})"
            )
        return Transaction(external.amount, TransactionCategory.INCOME)
