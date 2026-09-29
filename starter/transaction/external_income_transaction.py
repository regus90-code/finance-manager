"""Transaction format of a third-party freelance platform."""


class ExternalFreelanceIncome:
    """Represents income from a third-party freelance platform.

    This class stands for data the app does not control. It has a different
    shape than ``Transaction`` (invoice ID, description, a text type), so
    ``TransactionAdapter`` converts it before the app uses it.
    """

    def __init__(
        self, amount: float, invoice_id: str, description: str
    ) -> None:
        self.amount = amount
        self.invoice_id = invoice_id
        self.description = description
        self.typ = "income"  # fixed, since it's always income
