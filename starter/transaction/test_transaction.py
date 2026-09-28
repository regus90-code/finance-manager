import unittest

from transaction.transaction import Transaction
from transaction.transaction_category import TransactionCategory


class TestTransaction(unittest.TestCase):

    def test_transaction_creation(self) -> None:
        t = Transaction(100, TransactionCategory.EXPENSE)
        self.assertEqual(t.amount, 100)
        self.assertEqual(t.category, TransactionCategory.EXPENSE)

    def test_transaction_str(self) -> None:
        t = Transaction(50, TransactionCategory.INCOME)
        self.assertEqual(
            str(t), "Transaction($50, category='TransactionCategory.INCOME')"
        )

    def test_transaction_equality(self) -> None:
        t1 = Transaction(20, TransactionCategory.EXPENSE)
        t2 = Transaction(20, TransactionCategory.EXPENSE)
        t3 = Transaction(30, TransactionCategory.EXPENSE)
        self.assertEqual(t1, t2)
        self.assertNotEqual(t1, t3)

    def test_same_amount_different_category_is_not_equal(self) -> None:
        self.assertNotEqual(
            Transaction(20, TransactionCategory.INCOME),
            Transaction(20, TransactionCategory.EXPENSE),
        )

    def test_not_equal_to_other_types(self) -> None:
        self.assertNotEqual(Transaction(20, TransactionCategory.INCOME), 20)

    def test_equal_transactions_have_equal_hashes(self) -> None:
        t1 = Transaction(20, TransactionCategory.EXPENSE)
        t2 = Transaction(20, TransactionCategory.EXPENSE)
        self.assertEqual(len({t1, t2}), 1)

    def test_is_immutable(self) -> None:
        t = Transaction(20, TransactionCategory.EXPENSE)
        with self.assertRaises(AttributeError):
            t.amount = 30  # type: ignore[misc]

    def test_rejects_invalid_amounts(self) -> None:
        cases = [
            (0, ValueError),
            (-5, ValueError),
            (float("nan"), ValueError),
            (float("inf"), ValueError),
            ("10", TypeError),
            (True, TypeError),
            (None, TypeError),
        ]
        for amount, error in cases:
            with self.subTest(amount=amount):
                with self.assertRaises(error):
                    Transaction(amount, TransactionCategory.INCOME)  # type: ignore

    def test_inverse_swaps_category(self) -> None:
        income = Transaction(40, TransactionCategory.INCOME)
        expense = Transaction(40, TransactionCategory.EXPENSE)
        self.assertEqual(income.inverse(), expense)
        self.assertEqual(expense.inverse(), income)


if __name__ == "__main__":
    unittest.main()
