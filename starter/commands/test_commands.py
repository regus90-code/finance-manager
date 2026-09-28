import unittest

from balance.balance import Balance
from balance.balance_observer import LowBalanceAlertObserver
from commands.command_history import CommandHistory
from commands.transaction_command import ApplyTransactionCommand
from transaction.transaction import Transaction
from transaction.transaction_category import TransactionCategory


class TestApplyTransactionCommand(unittest.TestCase):

    def setUp(self) -> None:
        self.balance = Balance.get_instance()
        self.balance.reset()
        self.balance.clear_observers()
        self.addCleanup(self.balance.clear_observers)

    def test_execute_applies_transaction(self) -> None:
        income = Transaction(100, TransactionCategory.INCOME)
        ApplyTransactionCommand(self.balance, income).execute()
        self.assertEqual(self.balance.get_balance(), 100)

    def test_undo_reverses_income_and_expense(self) -> None:
        for category in TransactionCategory:
            with self.subTest(category=category):
                self.balance.reset()
                command = ApplyTransactionCommand(
                    self.balance, Transaction(40, category)
                )
                command.execute()
                command.undo()
                self.assertEqual(self.balance.get_balance(), 0)

    def test_undo_notifies_observers(self) -> None:
        alert = LowBalanceAlertObserver(threshold=50, output=lambda _: None)
        self.balance.register_observer(alert)
        command = ApplyTransactionCommand(
            self.balance, Transaction(100, TransactionCategory.INCOME)
        )
        command.execute()
        self.assertFalse(alert.alert_triggered)

        command.undo()

        self.assertTrue(alert.alert_triggered)


class TestCommandHistory(unittest.TestCase):

    def setUp(self) -> None:
        self.balance = Balance.get_instance()
        self.balance.reset()
        self.balance.clear_observers()
        self.history = CommandHistory()

    def apply(self, amount: float, category: TransactionCategory) -> None:
        command = ApplyTransactionCommand(self.balance, Transaction(amount, category))
        self.history.execute(command)

    def test_undo_restores_previous_balances_in_order(self) -> None:
        self.apply(100, TransactionCategory.INCOME)
        self.apply(30, TransactionCategory.EXPENSE)

        self.assertTrue(self.history.undo())
        self.assertEqual(self.balance.get_balance(), 100)
        self.assertTrue(self.history.undo())
        self.assertEqual(self.balance.get_balance(), 0)

    def test_redo_reapplies_undone_command(self) -> None:
        self.apply(100, TransactionCategory.INCOME)
        self.history.undo()

        self.assertTrue(self.history.redo())

        self.assertEqual(self.balance.get_balance(), 100)

    def test_undo_and_redo_on_empty_history_return_false(self) -> None:
        self.assertFalse(self.history.undo())
        self.assertFalse(self.history.redo())
        self.assertEqual(self.balance.get_balance(), 0)

    def test_new_command_clears_redo(self) -> None:
        self.apply(100, TransactionCategory.INCOME)
        self.history.undo()
        self.apply(20, TransactionCategory.INCOME)

        self.assertFalse(self.history.redo())
        self.assertEqual(self.balance.get_balance(), 20)

    def test_failed_command_is_not_recorded(self) -> None:
        class FakeCategory:
            pass

        bad = Transaction(10, FakeCategory())  # type: ignore[arg-type]
        with self.assertRaises(ValueError):
            self.history.execute(ApplyTransactionCommand(self.balance, bad))

        self.assertFalse(self.history.undo())


if __name__ == "__main__":
    unittest.main()
