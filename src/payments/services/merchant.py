from decimal import Decimal

from django.db.models import Case, Count, F, OuterRef, Subquery, Sum, Value, When
from django.db.models.functions import TruncDate

from payments.models import ExchangeRate, Invoice, InvoiceStatus, Ledger, LedgerType
from payments.schemas.merchant import MerchantReportRequest


def get_balance(id: int):
    return (
        Ledger.objects
            .filter(merchant_id=id)
            .values(currency=F('invoice__currency'))
            .annotate(
                total_amount=Sum(
                    Case(
                        When(type=LedgerType.FUND, then=F('amount')),
                        When(type=LedgerType.FEE, then=-F('amount')),
                        default=Value(Decimal(0)),
                    )
                )
            )
    )


def get_report(id: int, params: MerchantReportRequest):
    exchange_rate_subquery__invoice = ExchangeRate.objects.filter(
        base_currency=OuterRef('currency'),
        target_currency=params.currency
    ).values('rate')[:1]
    group_by__invoice = (
        F('project')
        if params.group_by == 'project'
        else TruncDate(F('updated_at'))
    )

    invoice_cte = (
        Invoice.objects
            .filter(
                project__merchant=id,
                updated_at__gte=params.date_from,
                updated_at__lte=params.date_to,
            )
            .values(group=group_by__invoice)
            .annotate(
                payed_cnt=Sum(
                    Case(
                        When(status__in=[InvoiceStatus.PAID, InvoiceStatus.OVERPAID], then=Value(1)),  # noqa: E501
                        default=Value(0),
                    )
                ),
                total_cnt=Count(1),
                all_invoice_amount=Sum(
                    Case(
                        When(currency=params.currency, then=F('amount')),
                        default=Subquery(exchange_rate_subquery__invoice) * F('amount'),
                    )
                ),
            )
    )

    exchange_rate_subquery__ledger = ExchangeRate.objects.filter(
        base_currency=OuterRef('invoice__currency'),
        target_currency=params.currency
    ).values('rate')[:1]
    group_by__ledger = (
        F('project')
        if params.group_by == 'project'
        else TruncDate(F('dt'))
    )

    ledger_cte = (
        Ledger.objects
            .filter(
                merchant=id,
                dt__gte=params.date_from,
                dt__lte=params.date_to,
            )
            .values(group=group_by__ledger)
            .annotate(
                fund_amount=Sum(
                    Case(
                        When(
                            invoice__currency=params.currency,
                            type=LedgerType.FUND,
                            then=F('amount'),
                        ),
                        When(
                            type=LedgerType.FUND,
                            then=Subquery(exchange_rate_subquery__ledger) * F('amount')
                        ),
                        default=Value(Decimal(0)),
                    )
                ),
                fee_amount=Sum(
                    Case(
                        When(
                            invoice__currency=params.currency,
                            type=LedgerType.FEE,
                            then=F('amount'),
                        ),
                        When(
                            type=LedgerType.FEE,
                            then=Subquery(exchange_rate_subquery__ledger) * F('amount'),
                        ),
                        default=Value(Decimal(0)),
                    )
                ),
            )
    )

    res = list()
    ledger_map = {}

    for ledger in ledger_cte:
        ledger_map[ledger['group']] = ledger

    for invoice in invoice_cte:
        res.append({**invoice, **ledger_map.get(invoice['group'], {})})

    return res
