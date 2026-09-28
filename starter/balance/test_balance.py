import unittest

from balance.balance import Balance
from transaction.transaction import Transaction
from transaction.transaction_category import TransactionCategory


class TestBalance(unittest.TestCase):

    def setUp(self) -> None:
        self.balance = Balance.get_instance()
        self.balance.reset()
        self.balance.clear_observers()

    def test_initial_balance(self) -> None:
        self.assertEqual(self.balance.get_balance(), 0.0)

    def test_singleton_instance(self) -> None:
        balance1 = Balance.get_instance()
        balance2 = Balance.get_instance()
        self.assertIs(balance1, balance2)

    def test_direct_instantiation_is_prevented(self) -> None:
        with self.assertRaises(RuntimeError):
            Balance()

    def test_add_income(self) -> None:
        self.balance.add_income(100)
        self.assertEqual(self.balance.get_balance(), 100)

    def test_add_expense(self) -> None:
        self.balance.add_expense(40)
        self.assertEqual(self.balance.get_balance(), -40)

    def test_add_income_rejects_invalid_amount(self) -> None:
        with self.assertRaises(ValueError):
            self.balance.add_income(-10)
        self.assertEqual(self.balance.get_balance(), 0.0)

    def test_apply_transaction_income(self) -> None:
        t = Transaction(150, TransactionCategory.INCOME)
        self.balance.apply_transaction(t)
        self.assertEqual(self.balance.get_balance(), 150)

    def test_apply_transaction_expense(self) -> None:
        t = Transaction(60, TransactionCategory.EXPENSE)
        self.balance.apply_transaction(t)
        self.assertEqual(self.balance.get_balance(), -60)

    def test_apply_transaction_invalid_category(self) -> None:
        class FakeCategory:
            pass

        t = Transaction(100, FakeCategory())  # type: ignore[arg-type]
        with self.assertRaises(ValueError):
            self.balance.apply_transaction(t)
        self.assertEqual(self.balance.get_balance(), 0.0)

    def test_reset(self) -> None:
        self.balance.add_income(100)
        self.balance.add_expense(50)
        self.balance.reset()
        self.assertEqual(self.balance.get_balance(), 0.0)

    def test_state_is_shared_between_references(self) -> None:
        Balance.get_instance().add_income(30)
        self.assertEqual(self.balance.get_balance(), 30)

    def test_summary(self) -> None:
        self.balance.add_income(1234.5)
        self.assertEqual(self.balance.summary(), "Net balance: $1,234.50")


if __name__ == "__main__":
    unittest.main()
