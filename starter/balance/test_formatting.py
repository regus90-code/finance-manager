import unittest

from balance.formatting import format_money


class TestFormatMoney(unittest.TestCase):

    def test_formats_amounts(self) -> None:
        cases = [
            (0, "$0.00"),
            (50, "$50.00"),
            (1234.5, "$1,234.50"),
            (-40, "-$40.00"),
            (-1375.126, "-$1,375.13"),
        ]
        for amount, expected in cases:
            with self.subTest(amount=amount):
                self.assertEqual(format_money(amount), expected)


if __name__ == "__main__":
    unittest.main()
