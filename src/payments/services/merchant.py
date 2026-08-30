from django.db.models import Case, Sum, When, F
from payments.models.ledger import Ledger


def get_balance(id: int):
    return (
        Ledger.objects
            .filter(merchant_id=id)
            .values(currency=F('invoice__currency'))
            .annotate(
                total_amount=Sum(
                    Case(
                        When(type=Ledger.LedgerType.FUND, then=F('amount')),
                        When(type=Ledger.LedgerType.FEE, then=-F('amount')),
                    )
                )
            )
    )
