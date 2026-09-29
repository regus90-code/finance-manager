import unittest

from balance.balance import Balance
from transaction.external_income_transaction import ExternalFreelanceIncome
from transaction.transaction import Transaction
from transaction.transaction_adapter import TransactionAdapter
from transaction.transaction_category import TransactionCategory


class TestTransactionAdapter(unittest.TestCase):

    def test_adapter_converts_freelance_income(self) -> None:
        ext_txn = ExternalFreelanceIncome(
            500, "INV-12345", "Website development"
        )
        adapter = TransactionAdapter(ext_txn)
        txn = adapter.to_transaction()
        self.assertEqual(txn, Transaction(500, TransactionCategory.INCOME))

    def test_adapted_transaction_updates_balance(self) -> None:
        balance = Balance.get_instance()
        balance.reset()
        balance.clear_observers()
        ext_txn = ExternalFreelanceIncome(750.5, "INV-1", "Logo design")

        balance.apply_transaction(TransactionAdapter(ext_txn).to_transaction())

        self.assertEqual(balance.get_balance(), 750.5)

    def test_unknown_external_type_raises(self) -> None:
        ext_txn = ExternalFreelanceIncome(
            500, "INV-12345", "Website development"
        )
        ext_txn.typ = "refund"
        with self.assertRaisesRegex(ValueError, "refund.*INV-12345"):
            TransactionAdapter(ext_txn).to_transaction()

    def test_invalid_external_amount_raises(self) -> None:
        ext_txn = ExternalFreelanceIncome(
            -500, "INV-12345", "Website development"
        )
        with self.assertRaises(ValueError):
            TransactionAdapter(ext_txn).to_transaction()


if __name__ == "__main__":
    unittest.main()
