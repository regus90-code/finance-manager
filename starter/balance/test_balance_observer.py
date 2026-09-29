import unittest

from balance.balance import Balance
from balance.balance_observer import (
    IBalanceObserver,
    LowBalanceAlertObserver,
    PrintObserver,
)
from transaction.transaction import Transaction
from transaction.transaction_category import TransactionCategory


class RecordingObserver(IBalanceObserver):
    """Remembers every update it receives."""

    def __init__(self) -> None:
        self.updates: list[tuple[float, Transaction]] = []

    def update(self, balance: float, transaction: Transaction) -> None:
        self.updates.append((balance, transaction))


class BalanceTestCase(unittest.TestCase):
    """Gives every test a clean balance without observers."""

    def setUp(self) -> None:
        self.balance = Balance.get_instance()
        self.balance.reset()
        self.balance.clear_observers()
        self.addCleanup(self.balance.clear_observers)


class TestLowBalanceAlertObserver(BalanceTestCase):

    def setUp(self) -> None:
        super().setUp()
        self.messages: list[str] = []

    def test_alert_triggers_on_low_balance(self) -> None:
        observer = LowBalanceAlertObserver(
            threshold=50, output=self.messages.append
        )
        self.balance.register_observer(observer)

        self.balance.apply_transaction(
            Transaction(100, TransactionCategory.INCOME)
        )
        self.assertFalse(observer.alert_triggered)

        self.balance.apply_transaction(
            Transaction(60, TransactionCategory.EXPENSE)
        )
        self.assertTrue(observer.alert_triggered)

        self.balance.apply_transaction(
            Transaction(100, TransactionCategory.INCOME)
        )
        self.assertFalse(observer.alert_triggered)

        self.balance.apply_transaction(
            Transaction(60, TransactionCategory.EXPENSE)
        )
        self.assertFalse(observer.alert_triggered)

        self.balance.apply_transaction(
            Transaction(60, TransactionCategory.EXPENSE)
        )
        self.assertTrue(observer.alert_triggered)

    def test_balance_at_threshold_is_no_alert(self) -> None:
        observer = LowBalanceAlertObserver(
            threshold=50, output=self.messages.append
        )
        self.balance.register_observer(observer)

        self.balance.add_income(50)

        self.assertFalse(observer.alert_triggered)
        self.assertEqual(self.messages, [])

    def test_alert_message(self) -> None:
        observer = LowBalanceAlertObserver(
            threshold=100, output=self.messages.append
        )
        self.balance.register_observer(observer)

        self.balance.add_expense(25)

        self.assertEqual(
            self.messages,
            ["ALERT: Low balance! -$25.00 is below the threshold of $100.00."],
        )


class TestPrintObserver(BalanceTestCase):

    def test_prints_balance_after_each_transaction(self) -> None:
        messages: list[str] = []
        self.balance.register_observer(PrintObserver(output=messages.append))

        self.balance.add_income(100)
        self.balance.add_expense(30)

        self.assertEqual(
            messages,
            [
                "Applied Transaction($100, "
                "category='TransactionCategory.INCOME') -> balance: $100.00",
                "Applied Transaction($30, "
                "category='TransactionCategory.EXPENSE') -> balance: $70.00",
            ],
        )


class TestObserverRegistration(BalanceTestCase):

    def test_observer_receives_new_balance_and_transaction(self) -> None:
        observer = RecordingObserver()
        self.balance.register_observer(observer)
        transaction = Transaction(80, TransactionCategory.INCOME)

        self.balance.apply_transaction(transaction)

        self.assertEqual(observer.updates, [(80, transaction)])

    def test_all_observers_are_notified(self) -> None:
        first, second = RecordingObserver(), RecordingObserver()
        self.balance.register_observer(first)
        self.balance.register_observer(second)

        self.balance.add_income(10)

        self.assertEqual(len(first.updates), 1)
        self.assertEqual(len(second.updates), 1)

    def test_registering_twice_notifies_once(self) -> None:
        observer = RecordingObserver()
        self.balance.register_observer(observer)
        self.balance.register_observer(observer)

        self.balance.add_income(10)

        self.assertEqual(len(observer.updates), 1)

    def test_unregistered_observer_is_not_notified(self) -> None:
        observer = RecordingObserver()
        self.balance.register_observer(observer)
        self.balance.unregister_observer(observer)

        self.balance.add_income(10)

        self.assertEqual(observer.updates, [])

    def test_unregistering_unknown_observer_raises(self) -> None:
        with self.assertRaises(ValueError):
            self.balance.unregister_observer(RecordingObserver())

    def test_failed_transaction_notifies_nobody(self) -> None:
        class FakeCategory:
            pass

        observer = RecordingObserver()
        self.balance.register_observer(observer)

        with self.assertRaises(ValueError):
            self.balance.apply_transaction(
                Transaction(10, FakeCategory())  # type: ignore[arg-type]
            )

        self.assertEqual(observer.updates, [])


if __name__ == "__main__":
    unittest.main()
