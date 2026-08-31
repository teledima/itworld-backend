from decimal import Decimal

from payments.models import ExchangeRate


def exchange(base_currency, target_currency) -> Decimal:
    return ExchangeRate.objects.get(
        base_currency=base_currency,
        target_currency=target_currency
    ).rate
