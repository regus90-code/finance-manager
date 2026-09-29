import io
import unittest
from contextlib import redirect_stdout

import main
from balance.balance import Balance


class TestMain(unittest.TestCase):

    def setUp(self) -> None:
        self.balance = Balance.get_instance()
        self.balance.reset()
        self.balance.clear_observers()
        self.addCleanup(self.balance.clear_observers)

    def run_main(self) -> str:
        output = io.StringIO()
        with redirect_stdout(output):
            main.main()
        return output.getvalue()

    def test_applies_all_transactions(self) -> None:
        self.run_main()
        # 100 - 50 + 200 - 75 + 1200 (adapted), then undo and redo the 1200
        self.assertEqual(self.balance.get_balance(), 1375)

    def test_prints_balance_changes_and_alert(self) -> None:
        output = self.run_main()

        self.assertIn(
            "Applied Transaction($1200, category='TransactionCategory.INCOME')"
            " -> balance: $1,375.00",
            output,
        )
        self.assertIn(
            "ALERT: Low balance! $50.00 is below the threshold of $100.00.",
            output,
        )
        self.assertIn("Undoing the last transaction...", output)
        self.assertIn("Net balance: $175.00", output)
        self.assertTrue(output.rstrip().endswith("Net balance: $1,375.00"))


if __name__ == "__main__":
    unittest.main()
