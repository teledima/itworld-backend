from decimal import Decimal

from django.db.models import Case, Subquery, Sum, Value, When, F, Count, OuterRef
from django.db.models.functions import TruncDate
from payments.models import ExchangeRate, Ledger, Invoice, InvoiceStatus
from payments.schemas.merchant import MerchantReportRequest


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
                        default=Value(Decimal(0)),
                    )
                )
            )
    )


def get_report(id: int, params: MerchantReportRequest):
    exchange_rate_subquery__invoice = ExchangeRate.objects.filter(base_currency=OuterRef('currency'), target_currency=params.currency).values('rate')[:1]
    invoice_cte = (
        Invoice.objects
            .filter(project__merchant=id)
            .values(group=F('project') if params.group_by == 'project' else TruncDate(F('updated_at')))
            .annotate(
                payed_cnt=Sum(Case(When(status__in=[InvoiceStatus.PAID, InvoiceStatus.OVERPAID], then=Value(1)), default=Value(0))),
                total_cnt=Count(1),
                all_invoice_amount=Sum(
                    Case(
                        When(currency=params.currency, then=F('amount')),
                        default=Subquery(exchange_rate_subquery__invoice) * F('amount'),
                    )
                ),
            )
    )

    exchange_rate_subquery__ledger = ExchangeRate.objects.filter(base_currency=OuterRef('invoice__currency'), target_currency=params.currency).values('rate')[:1]
    ledger_cte = (
        Ledger.objects
            .filter(merchant=id)
            .values(group=F('project') if params.group_by == 'project' else TruncDate(F('dt')))
            .annotate(
                fund_amount=Sum(
                    Case(
                        When(invoice__currency=params.currency, type=Ledger.LedgerType.FUND, then=F('amount')),
                        When(type=Ledger.LedgerType.FUND, then=Subquery(exchange_rate_subquery__ledger) * F('amount')),
                        default=Value(Decimal(0)),
                    )
                ),
                fee_amount=Sum(
                    Case(
                        When(invoice__currency=params.currency, type=Ledger.LedgerType.FEE, then=F('amount')),
                        When(type=Ledger.LedgerType.FEE, then=Subquery(exchange_rate_subquery__ledger) * F('amount')),
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
        res.append({**invoice, **ledger_map[invoice['group']]})

    return res
